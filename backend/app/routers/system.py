from fastapi import APIRouter

router = APIRouter(prefix="/api/system", tags=["system"])

@router.get("/info")
async def get_system_info():
    """Get system information"""
    return {"info": {}}

@router.get("/packages")
async def get_packages():
    """Get installed packages"""
    return {"packages": []}
