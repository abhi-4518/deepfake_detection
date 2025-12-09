from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.routes import router
from app.config import PORT
import uvicorn
import os

from app.db import engine, Base
from app.api import auth

# Import all models to register them with SQLAlchemy
from app.models.user import User
from app.models.analysis import Analysis
from app.models.analysis_result import AnalysisResult

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Deepfaker API")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(router)
app.include_router(auth.router)

@app.get("/")
async def read_root():
    from fastapi.responses import FileResponse
    return FileResponse("app/static/index.html")

@app.get("/login")
async def login_page():
    from fastapi.responses import FileResponse
    return FileResponse("app/static/login.html")

@app.get("/signup")
async def signup_page():
    from fastapi.responses import FileResponse
    return FileResponse("app/static/signup.html")

@app.get("/dashboard")
async def dashboard_page():
    from fastapi.responses import FileResponse
    return FileResponse("app/static/dashboard.html")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
