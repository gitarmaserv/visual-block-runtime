"""API routes for node settings."""
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from backend.db.database import ProjectDatabase

router = APIRouter(prefix="/nodes", tags=["nodes"])


class UpdateSettingsRequest(BaseModel):
    path: str
    graph_name: str
    node_uid: str
    settings: Dict[str, Any]


@router.get("/settings")
def get_node_settings(path: str, graph_name: str):
    """Get all node settings for a graph."""
    try:
        db = ProjectDatabase(f"{path}/project.sqlite")
        graph_id = db.get_graph_id(graph_name)
        
        if not graph_id:
            raise HTTPException(status_code=404, detail="Graph not found")
        
        settings = db.get_node_settings(graph_id)
        return {"settings": settings}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/settings/update")
def update_node_settings(req: UpdateSettingsRequest):
    """Update settings for a specific node."""
    try:
        db = ProjectDatabase(f"{req.path}/project.sqlite")
        graph_id = db.get_graph_id(req.graph_name)
        
        if not graph_id:
            raise HTTPException(status_code=404, detail="Graph not found")
        
        db.save_node_settings(graph_id, req.node_uid, req.settings)
        
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class BatchUpdateRequest(BaseModel):
    path: str
    graph_name: str
    nodes: Dict[str, Dict[str, Any]]


@router.post("/settings/batch_update")
def batch_update_settings(req: BatchUpdateRequest):
    """Batch update settings for multiple nodes."""
    try:
        db = ProjectDatabase(f"{req.path}/project.sqlite")
        graph_id = db.get_graph_id(req.graph_name)
        
        if not graph_id:
            raise HTTPException(status_code=404, detail="Graph not found")
        
        for node_uid, settings in req.nodes.items():
            db.save_node_settings(graph_id, node_uid, settings)
        
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
