"""
Code Server router: Manage per-user VS Code instances and workspaces
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import logging
from ..database import get_db
from ..auth import get_current_user
from ..models import User
from ..services.code_server_manager import code_server_manager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/code-server", tags=["code-server"])


@router.post("/start")
async def start_code_server(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start or access user's code-server instance
    Creates isolated container with private workspace
    """
    try:
        result = code_server_manager.start_user_container(current_user.id)
        
        logger.info(f"Code-server started for user {current_user.id}: {result}")
        
        return {
            "user_id": current_user.id,
            "status": result["status"],
            "port": result["port"],
            "container_id": result.get("container_id"),
            "workspace": result.get("workspace"),
            "url": f"/code/user/{current_user.id}/"
        }
    except Exception as e:
        logger.error(f"Failed to start code-server for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
async def stop_code_server(
    current_user: User = Depends(get_current_user)
):
    """Stop user's code-server instance"""
    try:
        success = code_server_manager.stop_user_container(current_user.id)
        
        if success:
            return {"message": "Code-server stopped", "user_id": current_user.id}
        else:
            raise HTTPException(status_code=500, detail="Failed to stop code-server")
    except Exception as e:
        logger.error(f"Error stopping code-server for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def code_server_status(
    current_user: User = Depends(get_current_user)
):
    """Check if user's code-server is running"""
    is_running = code_server_manager.is_container_running(current_user.id)
    port = code_server_manager.get_user_port(current_user.id) if is_running else None
    
    return {
        "user_id": current_user.id,
        "running": is_running,
        "port": port,
        "url": f"/code/user/{current_user.id}/" if is_running else None
    }


@router.get("/workspace-info")
async def workspace_info(
    current_user: User = Depends(get_current_user)
):
    """Get information about the user's workspace"""
    workspace = code_server_manager.get_user_workspace(current_user.id)
    
    # Count files in workspace
    try:
        file_count = sum(1 for _ in workspace.rglob('*') if _.is_file())
    except:
        file_count = 0
    
    return {
        "user_id": current_user.id,
        "workspace_path": str(workspace),
        "file_count": file_count,
        "exists": workspace.exists()
    }

