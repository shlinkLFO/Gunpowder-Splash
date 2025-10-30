from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.services import history_service

router = APIRouter(prefix="/api/history", tags=["history"])


class HistoryEntry(BaseModel):
    type: str
    description: str
    details: Optional[str] = None
    user_id: str = "default"


@router.get("/")
async def get_history(limit: int = 100):
    """Get activity history"""
    history = history_service.get_history(limit)
    return {"history": history}


@router.post("/")
async def add_history(entry: HistoryEntry):
    """Add a history entry"""
    result = history_service.add_history_entry(
        entry.type,
        entry.description,
        entry.details,
        entry.user_id
    )
    return result


@router.delete("/")
async def clear_history():
    """Clear all history"""
    result = history_service.clear_history()
    return result


@router.get("/stats")
async def get_stats():
    """Get history statistics"""
    stats = history_service.get_statistics()
    return stats
