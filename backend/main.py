from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import settings
from backend.database.database import init_db
from backend.routers.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure MongoDB indexes on startup
    try:
        init_db()
    except Exception:
        pass
    yield


app = FastAPI(
    title="Prodapt Hackathon API",
    description="Production-ready FastAPI backend with MongoDB, JWT authentication, refresh token rotation, and HttpOnly cookies.",
    version="1.0.0",
    lifespan=lifespan,
    swagger_ui_parameters={"persistAuthorization": True},
)

# CORS configuration for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Authentication Router
app.include_router(auth_router)


@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "online",
        "service": "Prodapt Hackathon API",
        "database": "MongoDB",
        "version": "1.0.0",
    }
