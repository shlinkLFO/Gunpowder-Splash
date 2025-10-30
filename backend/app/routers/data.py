from fastapi import APIRouter, UploadFile, File, Body, HTTPException
from fastapi.responses import Response
from typing import Optional
from pydantic import BaseModel

from app.services import execution_service, data_service, query_service

router = APIRouter(prefix="/api/data", tags=["data"])


class CodeExecution(BaseModel):
    code: str


class SQLQuery(BaseModel):
    query: str


class FilterRequest(BaseModel):
    dataset_name: str
    column: str
    value: str


class SearchRequest(BaseModel):
    dataset_name: str
    search_text: str


@router.post("/upload")
async def upload_data(file: UploadFile = File(...)):
    """Upload and process data file"""
    content = await file.read()
    result = data_service.upload_and_process_file(file.filename, content)
    
    if not result.get('success'):
        raise HTTPException(status_code=400, detail=result.get('error'))
    
    return result


@router.get("/preview/{dataset_name}")
async def preview_data(dataset_name: str, limit: int = 100):
    """Preview dataset"""
    result = data_service.get_dataset_preview(dataset_name, limit)
    
    if not result.get('success'):
        raise HTTPException(status_code=404, detail=result.get('error'))
    
    return result


@router.get("/datasets")
async def list_datasets():
    """List all available datasets"""
    datasets = data_service.list_datasets()
    return {"datasets": datasets}


@router.get("/export/{dataset_name}")
async def export_data(dataset_name: str, format: str = "csv"):
    """Export dataset as CSV or JSON"""
    data = data_service.export_dataset(dataset_name, format)
    
    if data is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    media_type = "text/csv" if format == "csv" else "application/json"
    filename = f"{dataset_name}.{format}"
    
    return Response(
        content=data,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.post("/execute")
async def execute_code(data: CodeExecution):
    """Execute Python code and return results"""
    result = execution_service.execute_python_code(data.code)
    return result


@router.post("/query")
async def execute_query(data: SQLQuery):
    """Execute SQL query on loaded datasets"""
    result = query_service.execute_sql_query(data.query)
    
    if not result.get('success'):
        raise HTTPException(status_code=400, detail=result.get('error'))
    
    return result


@router.post("/filter")
async def filter_data(data: FilterRequest):
    """Filter dataset by column value"""
    result = query_service.filter_dataset(data.dataset_name, data.column, data.value)
    
    if not result.get('success'):
        raise HTTPException(status_code=400, detail=result.get('error'))
    
    return result


@router.post("/search")
async def search_data(data: SearchRequest):
    """Search for text in dataset"""
    result = query_service.search_dataset(data.dataset_name, data.search_text)
    
    if not result.get('success'):
        raise HTTPException(status_code=400, detail=result.get('error'))
    
    return result


@router.get("/dataframes")
async def get_dataframes():
    """Get loaded DataFrames information"""
    dataframes = execution_service.get_loaded_dataframes()
    return {"dataframes": dataframes}


@router.post("/clear")
async def clear_context():
    """Clear execution context"""
    result = execution_service.clear_execution_context()
    return result
