"""
Workspace management router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid
from ..database import get_db
from ..auth import get_current_user
from ..models import User, Workspace, Membership, RoleEnum, Project, Plan
from ..storage import storage_service

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


class WorkspaceResponse(BaseModel):
    """Workspace information response"""
    id: str
    owner_user_id: str
    plan_id: str
    plan_name: str
    storage_used_bytes: int
    storage_limit_bytes: int
    is_read_only: bool
    cancelled_at: Optional[datetime]
    delete_after: Optional[datetime]
    member_count: int
    project_count: int
    my_role: str


class MemberResponse(BaseModel):
    """Workspace member information"""
    user_id: str
    email: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    role: str
    joined_at: datetime


class AddMemberRequest(BaseModel):
    """Request to add member to workspace"""
    email: str
    role: str = "USER"


class UpdateMemberRequest(BaseModel):
    """Request to update member role"""
    role: str


def get_user_workspace_role(
    db: Session,
    user_id: uuid.UUID,
    workspace_id: uuid.UUID
) -> Optional[RoleEnum]:
    """Get user's role in workspace"""
    membership = db.query(Membership).filter(
        Membership.user_id == user_id,
        Membership.workspace_id == workspace_id
    ).first()
    
    return membership.role if membership else None


def require_workspace_access(
    workspace_id: uuid.UUID,
    required_role: Optional[RoleEnum] = None
):
    """
    Dependency to check workspace access
    
    Args:
        workspace_id: Workspace UUID
        required_role: Optional minimum required role
    """
    async def dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        role = get_user_workspace_role(db, current_user.id, workspace_id)
        
        if not role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this workspace"
            )
        
        if required_role:
            role_hierarchy = {
                RoleEnum.USER: 1,
                RoleEnum.MOD: 2,
                RoleEnum.ADMIN: 3
            }
            
            if role_hierarchy.get(role, 0) < role_hierarchy.get(required_role, 999):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Requires {required_role.value} role"
                )
        
        return current_user, role
    
    return dependency


@router.get("", response_model=List[WorkspaceResponse])
async def list_my_workspaces(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all workspaces accessible to current user
    
    Returns:
        List of workspaces with user's role
    """
    memberships = db.query(Membership).filter(
        Membership.user_id == current_user.id
    ).all()
    
    workspaces = []
    for membership in memberships:
        workspace = membership.workspace
        plan = workspace.plan
        
        member_count = db.query(Membership).filter(
            Membership.workspace_id == workspace.id
        ).count()
        
        project_count = db.query(Project).filter(
            Project.workspace_id == workspace.id
        ).count()
        
        workspaces.append(WorkspaceResponse(
            id=str(workspace.id),
            owner_user_id=str(workspace.owner_user_id),
            plan_id=workspace.plan_id,
            plan_name=plan.name,
            storage_used_bytes=workspace.storage_used_bytes,
            storage_limit_bytes=plan.storage_limit_bytes,
            is_read_only=workspace.is_read_only,
            cancelled_at=workspace.cancelled_at,
            delete_after=workspace.delete_after,
            member_count=member_count,
            project_count=project_count,
            my_role=membership.role.value
        ))
    
    return workspaces


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get workspace details
    
    Args:
        workspace_id: Workspace UUID
        
    Returns:
        Workspace information
    """
    role = get_user_workspace_role(db, current_user.id, workspace_id)
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this workspace"
        )
    
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    plan = workspace.plan
    
    member_count = db.query(Membership).filter(
        Membership.workspace_id == workspace.id
    ).count()
    
    project_count = db.query(Project).filter(
        Project.workspace_id == workspace.id
    ).count()
    
    return WorkspaceResponse(
        id=str(workspace.id),
        owner_user_id=str(workspace.owner_user_id),
        plan_id=workspace.plan_id,
        plan_name=plan.name,
        storage_used_bytes=workspace.storage_used_bytes,
        storage_limit_bytes=plan.storage_limit_bytes,
        is_read_only=workspace.is_read_only,
        cancelled_at=workspace.cancelled_at,
        delete_after=workspace.delete_after,
        member_count=member_count,
        project_count=project_count,
        my_role=role.value
    )


@router.get("/{workspace_id}/members", response_model=List[MemberResponse])
async def list_workspace_members(
    workspace_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all members of a workspace
    
    Args:
        workspace_id: Workspace UUID
        
    Returns:
        List of workspace members
    """
    role = get_user_workspace_role(db, current_user.id, workspace_id)
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this workspace"
        )
    
    memberships = db.query(Membership).filter(
        Membership.workspace_id == workspace_id
    ).all()
    
    members = []
    for membership in memberships:
        user = membership.user
        members.append(MemberResponse(
            user_id=str(user.id),
            email=user.primary_email,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            role=membership.role.value,
            joined_at=membership.joined_at
        ))
    
    return members


@router.post("/{workspace_id}/members")
async def add_workspace_member(
    workspace_id: uuid.UUID,
    request: AddMemberRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a member to workspace (ADMIN only)
    
    Args:
        workspace_id: Workspace UUID
        request: Member details (email, role)
        
    Returns:
        Success message
    """
    # Check if current user is ADMIN
    role = get_user_workspace_role(db, current_user.id, workspace_id)
    
    if role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only ADMIN can add members"
        )
    
    # Validate role
    try:
        new_role = RoleEnum(request.role.upper())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role: {request.role}"
        )
    
    # Find user by email
    target_user = db.query(User).filter(User.primary_email == request.email).first()
    
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found with email: {request.email}"
        )
    
    # Check if already a member
    existing = db.query(Membership).filter(
        Membership.user_id == target_user.id,
        Membership.workspace_id == workspace_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this workspace"
        )
    
    # Team size limit is enforced by database trigger
    try:
        membership = Membership(
            user_id=target_user.id,
            workspace_id=workspace_id,
            role=new_role
        )
        db.add(membership)
        db.commit()
        
        return {"message": f"User {request.email} added to workspace"}
    except Exception as e:
        db.rollback()
        if "Team size limit exceeded" in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Team size limit exceeded for this plan"
            )
        raise


@router.delete("/{workspace_id}/members/{user_id}")
async def remove_workspace_member(
    workspace_id: uuid.UUID,
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove a member from workspace (ADMIN only)
    
    Args:
        workspace_id: Workspace UUID
        user_id: User UUID to remove
        
    Returns:
        Success message
    """
    # Check if current user is ADMIN
    role = get_user_workspace_role(db, current_user.id, workspace_id)
    
    if role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only ADMIN can remove members"
        )
    
    # Cannot remove workspace owner
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if workspace and workspace.owner_user_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove workspace owner"
        )
    
    # Delete membership
    membership = db.query(Membership).filter(
        Membership.user_id == user_id,
        Membership.workspace_id == workspace_id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found in this workspace"
        )
    
    db.delete(membership)
    db.commit()
    
    return {"message": "Member removed from workspace"}


@router.post("/{workspace_id}/export")
async def export_workspace(
    workspace_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export workspace as downloadable archive
    
    Args:
        workspace_id: Workspace UUID
        
    Returns:
        Signed URL for downloading export
    """
    role = get_user_workspace_role(db, current_user.id, workspace_id)
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this workspace"
        )
    
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    # Check if workspace is cancelled and within grace period
    if workspace.cancelled_at:
        if not workspace.delete_after or datetime.utcnow() > workspace.delete_after:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Export grace period has expired"
            )
    
    # Create export
    signed_url = storage_service.export_workspace(workspace_id)
    
    return {
        "export_url": signed_url,
        "expires_in_hours": 24,
        "message": "Export ready for download"
    }

