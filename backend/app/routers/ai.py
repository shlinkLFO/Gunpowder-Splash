"""
AI integration router for Beacon Studio
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from ..database import get_db
from ..auth import get_current_user
from ..models import User, Membership
from ..ai_providers import (
    get_ai_provider,
    get_default_provider,
    ChatRequest,
    ChatResponse,
    CompletionRequest,
    CompletionResponse,
    ChatMessage
)

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    workspace_id: uuid.UUID,
    request: ChatRequest,
    provider: str = "gemini",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Chat with AI assistant
    
    Args:
        workspace_id: Workspace UUID (for usage tracking)
        request: Chat request with messages
        provider: AI provider ('gemini', 'lm_studio', 'ollama')
        
    Returns:
        AI response
    """
    # Verify workspace access
    membership = db.query(Membership).filter(
        Membership.user_id == current_user.id,
        Membership.workspace_id == workspace_id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this workspace"
        )
    
    # Get AI provider
    try:
        ai_provider = get_ai_provider(provider)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Generate response
    try:
        response = await ai_provider.chat(request)
        
        # Track usage (does not commit)
        ai_provider.track_usage(
            db=db,
            user_id=current_user.id,
            workspace_id=workspace_id,
            model_name=response.model,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            cost_cents=calculate_cost(provider, response.input_tokens, response.output_tokens)
        )
        
        # Commit only after successful response
        db.commit()
        return response
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI request failed: {str(e)}"
        )


@router.post("/completion", response_model=CompletionResponse)
async def generate_completion(
    workspace_id: uuid.UUID,
    request: CompletionRequest,
    provider: str = "gemini",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate text completion
    
    Args:
        workspace_id: Workspace UUID (for usage tracking)
        request: Completion request
        provider: AI provider ('gemini', 'lm_studio', 'ollama')
        
    Returns:
        Completion response
    """
    # Verify workspace access
    membership = db.query(Membership).filter(
        Membership.user_id == current_user.id,
        Membership.workspace_id == workspace_id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this workspace"
        )
    
    # Get AI provider
    try:
        ai_provider = get_ai_provider(provider)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Generate completion
    try:
        response = await ai_provider.generate_completion(request)
        
        # Track usage (does not commit)
        ai_provider.track_usage(
            db=db,
            user_id=current_user.id,
            workspace_id=workspace_id,
            model_name=response.model,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            cost_cents=calculate_cost(provider, response.input_tokens, response.output_tokens)
        )
        
        # Commit only after successful response
        db.commit()
        return response
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI request failed: {str(e)}"
        )


@router.get("/usage/{workspace_id}")
async def get_ai_usage(
    workspace_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get AI usage statistics for workspace
    
    Args:
        workspace_id: Workspace UUID
        
    Returns:
        Usage statistics
    """
    from ..models import AIUsage
    from sqlalchemy import func
    
    # Verify workspace access
    membership = db.query(Membership).filter(
        Membership.user_id == current_user.id,
        Membership.workspace_id == workspace_id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this workspace"
        )
    
    # Get usage stats
    stats = db.query(
        func.count(AIUsage.id).label('total_requests'),
        func.sum(AIUsage.input_tokens).label('total_input_tokens'),
        func.sum(AIUsage.output_tokens).label('total_output_tokens'),
        func.sum(AIUsage.cost_cents).label('total_cost_cents')
    ).filter(
        AIUsage.workspace_id == workspace_id
    ).first()
    
    return {
        "workspace_id": str(workspace_id),
        "total_requests": stats.total_requests or 0,
        "total_input_tokens": stats.total_input_tokens or 0,
        "total_output_tokens": stats.total_output_tokens or 0,
        "total_cost_cents": stats.total_cost_cents or 0,
        "total_cost_usd": (stats.total_cost_cents or 0) / 100
    }


def calculate_cost(provider: str, input_tokens: Optional[int], output_tokens: Optional[int]) -> Optional[int]:
    """
    Calculate estimated cost in cents
    
    Args:
        provider: AI provider name
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        
    Returns:
        Cost in cents (or None if tokens not provided)
    """
    if not input_tokens or not output_tokens:
        return None
    
    # Gemini Flash pricing (as of 2024)
    # Input: $0.075 / 1M tokens
    # Output: $0.30 / 1M tokens
    if provider == "gemini":
        input_cost = (input_tokens / 1_000_000) * 0.075
        output_cost = (output_tokens / 1_000_000) * 0.30
        return int((input_cost + output_cost) * 100)
    
    # Local providers have no cost
    return 0

