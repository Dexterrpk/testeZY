from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles # Import StaticFiles
from fastapi.responses import RedirectResponse # Import RedirectResponse
import os # Import os

from .core.config import settings
from .core.database import create_db_and_tables, get_session
from .services import plan_service

# Import routers
from .routes import users, auth, plans, campaigns, ai_training, ai_interaction

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

@app.on_event("startup")
def on_startup():
    """Actions to perform on application startup."""
    create_db_and_tables()
    with next(get_session()) as session:
        plan_service.create_default_plans(session)

# Include API routers
app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["Auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])
app.include_router(plans.router, prefix=f"{settings.API_V1_STR}/plans", tags=["Plans"])
app.include_router(campaigns.router, prefix=f"{settings.API_V1_STR}/campaigns", tags=["Campaigns"])
app.include_router(ai_training.router, prefix=f"{settings.API_V1_STR}/ai-training", tags=["AI Training"])
app.include_router(ai_interaction.router, prefix=f"{settings.API_V1_STR}/ai", tags=["AI Interaction"])

# --- Static Files Configuration ---
# Determine the absolute path to the frontend directory relative to main.py
# Assuming main.py is in ZYNAPSE/backend/
backend_dir = os.path.dirname(__file__)
project_root = os.path.dirname(backend_dir)
frontend_dir = os.path.join(project_root, "frontend")

# Mount the frontend directory to serve static files (HTML, CSS, JS)
# Access via paths like /frontend/login.html, /frontend/index.html
app.mount("/frontend", StaticFiles(directory=frontend_dir, html=True), name="frontend")

# --- Root Redirect ---
@app.get("/")
def read_root():
    """Redirects the root path to the login page."""
    # Redirect to login page by default
    return RedirectResponse(url="/frontend/login.html")

# Note: The previous root endpoint returning JSON is replaced by the redirect.
# If you need an API root check, use a different path like /api/v1/status

# Add dependency injection for security later
# from .core import security
# app.dependency_overrides[security.get_current_user] = security.get_current_user_dependency

