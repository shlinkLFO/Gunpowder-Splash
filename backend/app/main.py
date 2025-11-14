from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import logging

from app.routers import files, data, history, templates, system, notebooks, auth, diagnostics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

WORKSPACE_DIR = Path("workspace")
WORKSPACE_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Gunpowder Splash - Collaborative IDE API | Glowstone")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

app.include_router(files.router)
app.include_router(data.router)
app.include_router(history.router)
app.include_router(templates.router)
app.include_router(system.router)
app.include_router(notebooks.router)
app.include_router(auth.router)
app.include_router(diagnostics.router)

@app.get("/")
async def root():
    return {"message": "Gunpowder Splash - Collaborative IDE API by Glowstone (shlinx.com)"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
