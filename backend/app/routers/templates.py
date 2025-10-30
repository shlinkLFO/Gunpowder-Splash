from fastapi import APIRouter

router = APIRouter(prefix="/api/templates", tags=["templates"])

@router.get("/")
async def get_templates():
    """Get all available templates"""
    return {"templates": {}}

@router.get("/{template_name}")
async def get_template(template_name: str):
    """Get a specific template"""
    return {"code": ""}
