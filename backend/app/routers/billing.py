"""
Stripe billing integration router
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import uuid
import stripe
from ..database import get_db
from ..auth import get_current_user
from ..models import User, Workspace, Plan, RoleEnum, Membership
from ..config import get_settings

settings = get_settings()
stripe.api_key = settings.stripe_api_key

router = APIRouter(prefix="/billing", tags=["billing"])


class CheckoutSessionRequest(BaseModel):
    """Request to create checkout session"""
    workspace_id: str
    plan_id: str
    success_url: str
    cancel_url: str


class CheckoutSessionResponse(BaseModel):
    """Checkout session response"""
    session_id: str
    checkout_url: str


class PortalSessionResponse(BaseModel):
    """Customer portal session response"""
    portal_url: str


class SubscriptionResponse(BaseModel):
    """Subscription information"""
    workspace_id: str
    plan_id: str
    plan_name: str
    status: str
    current_period_end: Optional[datetime]
    cancel_at_period_end: bool


@router.post("/checkout", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    request: CheckoutSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create Stripe checkout session for subscription
    
    Args:
        request: Checkout details
        
    Returns:
        Checkout session URL
    """
    workspace_id = uuid.UUID(request.workspace_id)
    
    # Verify user is ADMIN of workspace
    membership = db.query(Membership).filter(
        Membership.user_id == current_user.id,
        Membership.workspace_id == workspace_id
    ).first()
    
    if not membership or membership.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only ADMIN can manage billing"
        )
    
    # Validate plan
    plan = db.query(Plan).filter(Plan.id == request.plan_id).first()
    if not plan or plan.id == "free":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan ID"
        )
    
    # Get Stripe price ID for plan
    price_id_map = {
        "haste_i": settings.stripe_price_id_haste_i,
        "haste_ii": settings.stripe_price_id_haste_ii,
        "haste_iii": settings.stripe_price_id_haste_iii
    }
    
    price_id = price_id_map.get(request.plan_id)
    if not price_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No Stripe price configured for plan: {request.plan_id}"
        )
    
    # Lock workspace and create or retrieve Stripe customer
    workspace = (
        db.query(Workspace)
        .filter(Workspace.id == workspace_id)
        .with_for_update()
        .first()
    )
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    if workspace.stripe_customer_id:
        customer_id = workspace.stripe_customer_id
    else:
        customer = stripe.Customer.create(
            email=current_user.primary_email,
            metadata={
                "workspace_id": str(workspace_id),
                "user_id": str(current_user.id)
            }
        )
        customer_id = customer.id
        workspace.stripe_customer_id = customer_id
        db.commit()
    
    # Create checkout session
    session = stripe.checkout.Session.create(
        customer=customer_id,
        mode="subscription",
        payment_method_types=["card"],
        line_items=[{
            "price": price_id,
            "quantity": 1
        }],
        success_url=request.success_url,
        cancel_url=request.cancel_url,
        metadata={
            "workspace_id": str(workspace_id),
            "plan_id": request.plan_id
        }
    )
    
    return CheckoutSessionResponse(
        session_id=session.id,
        checkout_url=session.url
    )


@router.post("/portal", response_model=PortalSessionResponse)
async def create_portal_session(
    workspace_id: uuid.UUID,
    return_url: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create Stripe customer portal session
    
    Args:
        workspace_id: Workspace UUID
        return_url: URL to return to after portal
        
    Returns:
        Portal session URL
    """
    # Verify user is ADMIN of workspace
    membership = db.query(Membership).filter(
        Membership.user_id == current_user.id,
        Membership.workspace_id == workspace_id
    ).first()
    
    if not membership or membership.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only ADMIN can manage billing"
        )
    
    # Get workspace
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    if not workspace.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No Stripe customer associated with this workspace"
        )
    
    # Create portal session
    session = stripe.billing_portal.Session.create(
        customer=workspace.stripe_customer_id,
        return_url=return_url
    )
    
    return PortalSessionResponse(portal_url=session.url)


@router.get("/subscription/{workspace_id}", response_model=SubscriptionResponse)
async def get_subscription(
    workspace_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get subscription details for workspace
    
    Args:
        workspace_id: Workspace UUID
        
    Returns:
        Subscription information
    """
    # Verify user is member of workspace
    membership = db.query(Membership).filter(
        Membership.user_id == current_user.id,
        Membership.workspace_id == workspace_id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this workspace"
        )
    
    # Get workspace
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    plan = workspace.plan
    
    # Get Stripe subscription details if exists
    status_str = "active"
    current_period_end = None
    cancel_at_period_end = False
    
    if workspace.stripe_subscription_id:
        try:
            subscription = stripe.Subscription.retrieve(workspace.stripe_subscription_id)
            status_str = subscription.status
            current_period_end = datetime.fromtimestamp(subscription.current_period_end)
            cancel_at_period_end = subscription.cancel_at_period_end
        except stripe.error.StripeError:
            pass
    
    return SubscriptionResponse(
        workspace_id=str(workspace_id),
        plan_id=workspace.plan_id,
        plan_name=plan.name,
        status=status_str,
        current_period_end=current_period_end,
        cancel_at_period_end=cancel_at_period_end
    )


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature"),
    db: Session = Depends(get_db)
):
    """
    Handle Stripe webhook events
    
    Args:
        request: Raw request body
        stripe_signature: Stripe signature header
        
    Returns:
        Success response
    """
    payload = await request.body()
    
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.stripe_webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle different event types
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        
        # Get workspace from metadata
        workspace_id = uuid.UUID(session["metadata"]["workspace_id"])
        plan_id = session["metadata"]["plan_id"]
        subscription_id = session["subscription"]
        
        # Lock and update workspace
        workspace = (
            db.query(Workspace)
            .filter(Workspace.id == workspace_id)
            .with_for_update()
            .first()
        )
        if workspace:
            workspace.plan_id = plan_id
            workspace.stripe_subscription_id = subscription_id
            workspace.is_read_only = False
            workspace.cancelled_at = None
            workspace.delete_after = None
            db.commit()
    
    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        subscription_id = subscription["id"]
        
        # Lock and mark workspace as cancelled
        workspace = (
            db.query(Workspace)
            .filter(Workspace.stripe_subscription_id == subscription_id)
            .with_for_update()
            .first()
        )
        
        if workspace:
            workspace.cancelled_at = datetime.utcnow()
            workspace.delete_after = datetime.utcnow() + timedelta(days=30)
            workspace.is_read_only = True
            db.commit()
    
    elif event["type"] == "customer.subscription.updated":
        subscription = event["data"]["object"]
        subscription_id = subscription["id"]
        
        # Lock and handle plan changes or reactivations
        workspace = (
            db.query(Workspace)
            .filter(Workspace.stripe_subscription_id == subscription_id)
            .with_for_update()
            .first()
        )
        
        if workspace and subscription["status"] == "active":
            # Reactivate if was cancelled
            if workspace.is_read_only:
                workspace.is_read_only = False
                workspace.cancelled_at = None
                workspace.delete_after = None
                db.commit()
    
    return {"status": "success"}

