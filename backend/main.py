"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.api import plugins, projects, graph, nodes, variables, execution, logs


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Load plugins on startup
    from backend.plugins.loader import load_plugins
    load_plugins()
    yield


app = FastAPI(
    title="Visual Block Runtime API",
    description="Backend API for Visual Block Runtime Desktop Application",
    version="1.0.0",
    lifespan=lifespan
)

# CORS - allow all for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(plugins.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(graph.router, prefix="/api")
app.include_router(nodes.router, prefix="/api")
app.include_router(variables.router, prefix="/api")
app.include_router(execution.router, prefix="/api")
app.include_router(logs.router, prefix="/api")


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "name": "Visual Block Runtime API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}
