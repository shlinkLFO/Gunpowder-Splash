"""
Project management router
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid
from ..database import get_db
from ..auth import get_current_user
from ..models import User, Project, Workspace, Membership, RoleEnum
from ..storage import storage_service

router = APIRouter(prefix="/projects", tags=["projects"])


class ProjectResponse(BaseModel):
    """Project information response"""
    id: str
    workspace_id: str
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime


class CreateProjectRequest(BaseModel):
    """Request to create new project"""
    workspace_id: str
    name: str
    description: Optional[str] = None


class UpdateProjectRequest(BaseModel):
    """Request to update project"""
    name: Optional[str] = None
    description: Optional[str] = None


class FileResponse(BaseModel):
    """File metadata response"""
    path: str
    size: int
    content_type: str
    updated_at: datetime


def check_project_access(
    db: Session,
    user_id: uuid.UUID,
    project_id: uuid.UUID,
    write_access: bool = False
) -> tuple[Project, RoleEnum]:
    """
    Check if user has access to project
    
    Args:
        db: Database session
        user_id: User UUID
        project_id: Project UUID
        write_access: If True, check for write permissions
        
    Returns:
        Tuple of (Project, Role)
        
    Raises:
        HTTPException: If access denied
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check workspace membership
    membership = db.query(Membership).filter(
        Membership.user_id == user_id,
        Membership.workspace_id == project.workspace_id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this project"
        )
    
    # Check if workspace is read-only
    if write_access:
        workspace = project.workspace
        if workspace.is_read_only:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Workspace is in read-only mode"
            )
    
    return project, membership.role


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    workspace_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all projects in a workspace
    
    Args:
        workspace_id: Workspace UUID
        
    Returns:
        List of projects
    """
    # Check workspace access
    membership = db.query(Membership).filter(
        Membership.user_id == current_user.id,
        Membership.workspace_id == workspace_id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this workspace"
        )
    
    projects = db.query(Project).filter(
        Project.workspace_id == workspace_id
    ).all()
    
    return [
        ProjectResponse(
            id=str(project.id),
            workspace_id=str(project.workspace_id),
            name=project.name,
            description=project.description,
            created_at=project.created_at,
            updated_at=project.updated_at
        )
        for project in projects
    ]


@router.post("", response_model=ProjectResponse)
async def create_project(
    request: CreateProjectRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new project (ADMIN only)
    
    Args:
        request: Project creation details
        
    Returns:
        Created project
    """
    workspace_id = uuid.UUID(request.workspace_id)
    
    # Check if user is ADMIN of workspace
    membership = db.query(Membership).filter(
        Membership.user_id == current_user.id,
        Membership.workspace_id == workspace_id
    ).first()
    
    if not membership or membership.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only ADMIN can create projects"
        )
    
    # Check if project name already exists
    existing = db.query(Project).filter(
        Project.workspace_id == workspace_id,
        Project.name == request.name
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Project '{request.name}' already exists"
        )
    
    # Create project
    project = Project(
        workspace_id=workspace_id,
        name=request.name,
        description=request.description
    )
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return ProjectResponse(
        id=str(project.id),
        workspace_id=str(project.workspace_id),
        name=project.name,
        description=project.description,
        created_at=project.created_at,
        updated_at=project.updated_at
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get project details
    
    Args:
        project_id: Project UUID
        
    Returns:
        Project information
    """
    project, role = check_project_access(db, current_user.id, project_id)
    
    return ProjectResponse(
        id=str(project.id),
        workspace_id=str(project.workspace_id),
        name=project.name,
        description=project.description,
        created_at=project.created_at,
        updated_at=project.updated_at
    )


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    request: UpdateProjectRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update project details (ADMIN/MOD only)
    
    Args:
        project_id: Project UUID
        request: Update details
        
    Returns:
        Updated project
    """
    project, role = check_project_access(db, current_user.id, project_id, write_access=True)
    
    if role == RoleEnum.USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="USER role cannot modify project settings"
        )
    
    # Update fields
    if request.name is not None:
        # Check for name conflicts
        existing = db.query(Project).filter(
            Project.workspace_id == project.workspace_id,
            Project.name == request.name,
            Project.id != project_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Project '{request.name}' already exists"
            )
        
        project.name = request.name
    
    if request.description is not None:
        project.description = request.description
    
    project.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(project)
    
    return ProjectResponse(
        id=str(project.id),
        workspace_id=str(project.workspace_id),
        name=project.name,
        description=project.description,
        created_at=project.created_at,
        updated_at=project.updated_at
    )


@router.delete("/{project_id}")
async def delete_project(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete project (ADMIN only)
    
    Args:
        project_id: Project UUID
        
    Returns:
        Success message
    """
    project, role = check_project_access(db, current_user.id, project_id, write_access=True)
    
    if role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only ADMIN can delete projects"
        )
    
    project_name = project.name
    
    # Lock the workspace for update
    workspace = (
        db.query(Workspace)
        .filter(Workspace.id == project.workspace_id)
        .with_for_update()
        .first()
    )
    if not workspace:
        # This should not be reachable if project exists due to FK constraints
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent workspace not found"
        )

    # Delete all files and get the total size
    deleted_bytes = storage_service.delete_project(project.workspace_id, project.id)
    
    # Update storage quota
    workspace.storage_used_bytes = max(0, workspace.storage_used_bytes - deleted_bytes)
    
    # Delete project from database
    db.delete(project)
    db.commit()
    
    return {"message": f"Project '{project_name}' deleted"}


@router.get("/{project_id}/files", response_model=List[FileResponse])
async def list_files(
    project_id: uuid.UUID,
    prefix: str = "",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List files in project
    
    Args:
        project_id: Project UUID
        prefix: Optional path prefix to filter
        
    Returns:
        List of files
    """
    project, role = check_project_access(db, current_user.id, project_id)
    
    files = storage_service.list_files(
        workspace_id=project.workspace_id,
        project_id=project.id,
        prefix=prefix
    )
    
    return [
        FileResponse(
            path=file["path"],
            size=file["size"],
            content_type=file["content_type"],
            updated_at=file["updated_at"]
        )
        for file in files
    ]


@router.post("/{project_id}/files")
async def upload_file(
    project_id: uuid.UUID,
    file_path: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload file to project
    
    Args:
        project_id: Project UUID
        file_path: Destination path in project
        file: File upload
        
    Returns:
        File metadata
    """
    project, role = check_project_access(db, current_user.id, project_id, write_access=True)
    
    # Read file content
    content = await file.read()
    
    # Upload to storage
    result = storage_service.write_file(
        db=db,
        workspace_id=project.workspace_id,
        project_id=project.id,
        file_path=file_path,
        content=content,
        content_type=file.content_type
    )
    
    return result


@router.get("/{project_id}/files/{file_path:path}")
async def download_file(
    project_id: uuid.UUID,
    file_path: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Download file from project
    
    Args:
        project_id: Project UUID
        file_path: File path in project
        
    Returns:
        File content
    """
    project, role = check_project_access(db, current_user.id, project_id)
    
    content = storage_service.read_file(
        workspace_id=project.workspace_id,
        project_id=project.id,
        file_path=file_path
    )
    
    from fastapi.responses import Response
    
    return Response(content=content, media_type="application/octet-stream")


@router.delete("/{project_id}/files/{file_path:path}")
async def delete_file(
    project_id: uuid.UUID,
    file_path: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete file from project
    
    Args:
        project_id: Project UUID
        file_path: File path in project
        
    Returns:
        Success message
    """
    project, role = check_project_access(db, current_user.id, project_id, write_access=True)
    
    storage_service.delete_file(
        db=db,
        workspace_id=project.workspace_id,
        project_id=project.id,
        file_path=file_path
    )
    
    return {"message": f"File '{file_path}' deleted"}

