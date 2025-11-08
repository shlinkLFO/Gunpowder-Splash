"""
Cloud Storage service with quota enforcement
"""
from google.cloud import storage
from google.oauth2 import service_account
from typing import Optional, BinaryIO
from pathlib import Path
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from .config import get_settings
from .models import Workspace, Project
import uuid
from datetime import timedelta

settings = get_settings()


class StorageService:
    """Cloud Storage operations with quota enforcement"""
    
    def __init__(self):
        """Initialize GCS client"""
        if settings.gcs_credentials_path:
            credentials = service_account.Credentials.from_service_account_file(
                settings.gcs_credentials_path
            )
            self.client = storage.Client(
                project=settings.gcs_project_id,
                credentials=credentials
            )
        else:
            # Use default credentials (for Cloud Run)
            self.client = storage.Client(project=settings.gcs_project_id)
        
        self.bucket = self.client.bucket(settings.gcs_bucket_name)
    
    def _get_object_path(
        self,
        workspace_id: uuid.UUID,
        project_id: uuid.UUID,
        file_path: str
    ) -> str:
        """
        Generate GCS object path
        
        Format: workspace_<id>/project_<id>/path/to/file
        """
        # Normalize file_path (remove leading slash)
        file_path = file_path.lstrip("/")
        return f"workspace_{workspace_id}/project_{project_id}/{file_path}"
    
    def _check_storage_quota(
        self,
        db: Session,
        workspace_id: uuid.UUID,
        delta_bytes: int
    ) -> tuple[Workspace, int]:
        """
        Check if storage operation would exceed quota
        
        Args:
            db: Database session
            workspace_id: Workspace UUID
            delta_bytes: Change in bytes (positive for increase, negative for decrease)
            
        Raises:
            HTTPException: If quota would be exceeded
        """
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
        
        # Check if workspace is read-only
        if workspace.is_read_only:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Workspace is in read-only mode (cancelled subscription)"
            )
        
        # Calculate new usage
        new_usage = workspace.storage_used_bytes + delta_bytes
        
        # Get plan storage limit
        plan = workspace.plan
        storage_limit = plan.storage_limit_bytes
        
        if new_usage > storage_limit:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Storage limit exceeded. Used: {new_usage} bytes, Limit: {storage_limit} bytes"
            )
        
        return workspace, max(0, new_usage)
    
    def write_file(
        self,
        db: Session,
        workspace_id: uuid.UUID,
        project_id: uuid.UUID,
        file_path: str,
        content: bytes,
        content_type: Optional[str] = None
    ) -> dict:
        """
        Write file to storage with quota enforcement
        
        Args:
            db: Database session
            workspace_id: Workspace UUID
            project_id: Project UUID
            file_path: Relative file path within project
            content: File content bytes
            content_type: Optional MIME type
            
        Returns:
            Dictionary with file metadata
            
        Raises:
            HTTPException: If quota exceeded or workspace not found
        """
        object_path = self._get_object_path(workspace_id, project_id, file_path)
        blob = self.bucket.blob(object_path)
        
        # Check if file exists and get old size
        old_size = 0
        if blob.exists():
            blob.reload()
            old_size = blob.size or 0
        
        # Calculate delta
        new_size = len(content)
        delta_bytes = new_size - old_size
        
        # Check quota (locks workspace row until transaction complete)
        workspace, new_usage = self._check_storage_quota(db, workspace_id, delta_bytes)
        
        # Upload file
        try:
            blob.upload_from_string(
                content,
                content_type=content_type or "application/octet-stream"
            )

            # Persist updated storage usage only after successful upload
            workspace.storage_used_bytes = new_usage
            db.commit()
            
            return {
                "path": file_path,
                "size": new_size,
                "content_type": blob.content_type,
                "updated_at": blob.updated
            }
        except Exception as e:
            # Ensure no quota changes are persisted on failure
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file: {str(e)}"
            )
    
    def read_file(
        self,
        workspace_id: uuid.UUID,
        project_id: uuid.UUID,
        file_path: str
    ) -> bytes:
        """
        Read file from storage
        
        Args:
            workspace_id: Workspace UUID
            project_id: Project UUID
            file_path: Relative file path within project
            
        Returns:
            File content bytes
            
        Raises:
            HTTPException: If file not found
        """
        object_path = self._get_object_path(workspace_id, project_id, file_path)
        blob = self.bucket.blob(object_path)
        
        if not blob.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {file_path}"
            )
        
        try:
            return blob.download_as_bytes()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to read file: {str(e)}"
            )
    
    def delete_file(
        self,
        db: Session,
        workspace_id: uuid.UUID,
        project_id: uuid.UUID,
        file_path: str
    ) -> None:
        """
        Delete file from storage and update quota
        
        Args:
            db: Database session
            workspace_id: Workspace UUID
            project_id: Project UUID
            file_path: Relative file path within project
            
        Raises:
            HTTPException: If file not found or workspace read-only
        """
        object_path = self._get_object_path(workspace_id, project_id, file_path)
        blob = self.bucket.blob(object_path)
        
        if not blob.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {file_path}"
            )
        
        # Get file size before deletion
        blob.reload()
        file_size = blob.size or 0
        
        # Lock workspace row and check if read-only
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

        if workspace.is_read_only:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Workspace is in read-only mode"
            )
        
        # Delete file
        try:
            blob.delete()
            
            # Update storage usage (negative delta)
            workspace.storage_used_bytes = max(0, workspace.storage_used_bytes - file_size)
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete file: {str(e)}"
            )
    
    def list_files(
        self,
        workspace_id: uuid.UUID,
        project_id: uuid.UUID,
        prefix: str = ""
    ) -> list[dict]:
        """
        List files in a project directory
        
        Args:
            workspace_id: Workspace UUID
            project_id: Project UUID
            prefix: Optional path prefix to filter
            
        Returns:
            List of file metadata dictionaries
        """
        base_prefix = f"workspace_{workspace_id}/project_{project_id}/"
        full_prefix = base_prefix + prefix.lstrip("/")
        
        blobs = self.client.list_blobs(self.bucket, prefix=full_prefix)
        
        files = []
        for blob in blobs:
            # Remove base prefix to get relative path
            relative_path = blob.name[len(base_prefix):]
            
            files.append({
                "path": relative_path,
                "size": blob.size,
                "content_type": blob.content_type,
                "updated_at": blob.updated,
                "created_at": blob.time_created
            })
        
        return files
    
    def get_signed_url(
        self,
        workspace_id: uuid.UUID,
        project_id: uuid.UUID,
        file_path: str,
        expiration_minutes: int = 60
    ) -> str:
        """
        Generate signed URL for temporary file access
        
        Args:
            workspace_id: Workspace UUID
            project_id: Project UUID
            file_path: Relative file path within project
            expiration_minutes: URL expiration time in minutes
            
        Returns:
            Signed URL string
        """
        object_path = self._get_object_path(workspace_id, project_id, file_path)
        blob = self.bucket.blob(object_path)
        
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=expiration_minutes),
            method="GET"
        )
        
        return url
    
    def calculate_workspace_storage(
        self,
        workspace_id: uuid.UUID
    ) -> int:
        """
        Calculate total storage used by workspace across all projects
        
        Args:
            workspace_id: Workspace UUID
            
        Returns:
            Total bytes used
        """
        prefix = f"workspace_{workspace_id}/"
        blobs = self.client.list_blobs(self.bucket, prefix=prefix)
        
        total_bytes = sum(blob.size or 0 for blob in blobs)
        return total_bytes
    
    def delete_project(
        self,
        workspace_id: uuid.UUID,
        project_id: uuid.UUID
    ) -> int:
        """
        Delete all files for a specific project
        
        Args:
            workspace_id: Workspace UUID
            project_id: Project UUID
        
        Returns:
            Total bytes of deleted files
        """
        prefix = f"workspace_{workspace_id}/project_{project_id}/"
        blobs = list(self.client.list_blobs(self.bucket, prefix=prefix))
        
        deleted_bytes = sum(blob.size or 0 for blob in blobs)
        
        # Delete all blobs for this project
        # Consider batch deletion for performance on large projects
        for blob in blobs:
            blob.delete()
            
        return deleted_bytes
    
    def delete_workspace(
        self,
        workspace_id: uuid.UUID
    ) -> None:
        """
        Delete all files for a workspace (used during purge)
        
        Args:
            workspace_id: Workspace UUID
        """
        prefix = f"workspace_{workspace_id}/"
        blobs = self.client.list_blobs(self.bucket, prefix=prefix)
        
        # Delete all blobs
        for blob in blobs:
            blob.delete()
    
    def export_workspace(
        self,
        workspace_id: uuid.UUID
    ) -> str:
        """
        Create and upload workspace export archive, return signed URL
        
        Args:
            workspace_id: Workspace UUID
            
        Returns:
            Signed URL for downloading the export archive
        """
        import zipfile
        import io
        from datetime import datetime
        
        # Create in-memory ZIP archive
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            prefix = f"workspace_{workspace_id}/"
            blobs = self.client.list_blobs(self.bucket, prefix=prefix)
            
            for blob in blobs:
                # Get relative path (remove workspace prefix)
                relative_path = blob.name[len(prefix):]
                
                # Download and add to ZIP
                content = blob.download_as_bytes()
                zip_file.writestr(relative_path, content)
        
        # Upload archive to temporary location
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        archive_path = f"exports/workspace_{workspace_id}_{timestamp}.zip"
        archive_blob = self.bucket.blob(archive_path)
        
        zip_buffer.seek(0)
        archive_blob.upload_from_file(zip_buffer, content_type="application/zip")
        
        # Generate signed URL (24 hour expiration)
        signed_url = archive_blob.generate_signed_url(
            version="v4",
            expiration=timedelta(hours=24),
            method="GET"
        )
        
        return signed_url


# Singleton instance
storage_service = StorageService()

