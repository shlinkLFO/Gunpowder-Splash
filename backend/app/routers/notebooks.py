"""
Jupyter Notebook Router
API endpoints for notebook operations
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from pathlib import Path

from app.services import notebook_service

router = APIRouter(prefix="/api/notebooks", tags=["notebooks"])

WORKSPACE_DIR = Path("workspace")


class ExecuteCellRequest(BaseModel):
    cell: Dict[str, Any]
    cell_index: int
    filepath: str
    session_id: str


class ExecuteAllRequest(BaseModel):
    cells: List[Dict[str, Any]]
    filepath: str
    session_id: str


class ResetContextRequest(BaseModel):
    filepath: str
    session_id: str


class GetVariablesRequest(BaseModel):
    filepath: str
    session_id: str


class ParseNotebookRequest(BaseModel):
    filepath: str


@router.post("/parse")
async def parse_notebook(request: ParseNotebookRequest):
    """
    Parse a Jupyter notebook file and return its structure
    """
    try:
        filepath = WORKSPACE_DIR / request.filepath
        if not filepath.exists():
            raise HTTPException(status_code=404, detail="Notebook file not found")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        result = notebook_service.parse_notebook(content)
        
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('error'))
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute-cell")
async def execute_cell(request: ExecuteCellRequest):
    """
    Execute a single notebook cell with isolated session context
    """
    try:
        result = notebook_service.execute_notebook_cell(
            request.cell,
            request.cell_index,
            request.filepath,
            request.session_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute-all")
async def execute_all(request: ExecuteAllRequest):
    """
    Execute all cells in a notebook with isolated session context
    """
    try:
        results = notebook_service.execute_all_cells(
            request.cells,
            request.filepath,
            request.session_id
        )
        return {'results': results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset")
async def reset_context(request: ResetContextRequest):
    """
    Reset the notebook execution context for a specific session
    """
    try:
        result = notebook_service.reset_notebook_context(
            request.filepath,
            request.session_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/variables")
async def get_variables(request: GetVariablesRequest):
    """
    Get all variables in the notebook context for a specific session
    """
    try:
        variables = notebook_service.get_notebook_variables(
            request.filepath,
            request.session_id
        )
        return {'variables': variables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
