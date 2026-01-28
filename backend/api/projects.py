"""API routes for project management."""
import os
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from backend.db.database import ProjectDatabase

router = APIRouter(prefix="/projects", tags=["projects"])


class CreateProjectRequest(BaseModel):
    name: str
    path: str


class OpenProjectRequest(BaseModel):
    path: str


class SaveProjectRequest(BaseModel):
    path: str
    name: str
    graph_json: dict


# Global state for current project
_current_project_path = None


@router.post("/create")
def create_project(req: CreateProjectRequest):
    """Create a new project."""
    try:
        project_path = req.path
        
        # Create directory structure
        os.makedirs(project_path, exist_ok=True)
        os.makedirs(os.path.join(project_path, "artifacts"), exist_ok=True)
        
        # Create log file
        with open(os.path.join(project_path, "log.txt"), 'w') as f:
            pass
        
        # Initialize database
        db_path = os.path.join(project_path, "project.sqlite")
        db = ProjectDatabase(db_path)
        db.init_schema()
        
        # Save initial graph
        db.save_graph(req.name, {"nodes": [], "edges": [], "viewport": {"x": 0, "y": 0, "zoom": 1}})
        
        global _current_project_path
        _current_project_path = project_path
        
        return {
            "success": True,
            "project_id": req.name,
            "path": project_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/open")
def open_project(req: OpenProjectRequest):
    """Open an existing project."""
    try:
        if not os.path.exists(req.path):
            raise HTTPException(status_code=404, detail="Project not found")
        
        global _current_project_path
        _current_project_path = req.path
        
        return {
            "success": True,
            "path": req.path
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/state")
def get_project_state():
    """Get current project state."""
    global _current_project_path
    if not _current_project_path:
        return {"active": False}
    
    return {
        "active": True,
        "path": _current_project_path
    }


@router.post("/save")
def save_project(req: SaveProjectRequest):
    """Save project graph."""
    try:
        db_path = os.path.join(req.path, "project.sqlite")
        db = ProjectDatabase(db_path)
        
        graph_id = db.save_graph(req.name, req.graph_json)
        
        return {
            "success": True,
            "graph_id": graph_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
