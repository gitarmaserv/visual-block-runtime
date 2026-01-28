"""API routes for graph management."""
import json
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any

from backend.db.database import ProjectDatabase

router = APIRouter(prefix="/graph", tags=["graph"])


class GraphData(BaseModel):
    path: str
    name: str
    graph_json: Dict[str, Any]


@router.get("/load")
def load_graph(path: str, name: str):
    """Load graph data."""
    try:
        db_path = os.path.join(path, "project.sqlite")
        db = ProjectDatabase(db_path)
        graph_json = db.load_graph(name)
        
        if not graph_json:
            raise HTTPException(status_code=404, detail="Graph not found")
        
        return {"graph_json": graph_json}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save")
def save_graph(data: GraphData):
    """Save graph data."""
    print(f"Saving graph: path={repr(data.path)}, name={repr(data.name)}")
    print(f"Directory exists: {os.path.exists(data.path)}")
    print(f"graph_json type: {type(data.graph_json)}")
    if data.graph_json:
        print(f"graph_json keys: {list(data.graph_json.keys())}")
    try:
        db_path = os.path.join(data.path, "project.sqlite")
        print(f"db_path: {db_path}")
        try:
            db = ProjectDatabase(db_path)
            print("Database initialized successfully")
        except Exception as e:
            print(f"Failed to initialize database: {e}")
            raise

        graph_id = db.save_graph(data.name, data.graph_json)

        return {"success": True, "graph_id": graph_id}
    except Exception as e:
        print(f"Error saving graph: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate")
def validate_graph(data: GraphData):
    """Validate graph for errors."""
    try:
        graph = data.graph_json
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        
        errors = []
        
        # Check for Start node when validating
        has_start = any(
            n.get("data", {}).get("plugin_id") == "__start__"
            for n in nodes
        )
        
        if not has_start:
            errors.append({
                "type": "warning",
                "message": "No Start node found (required for 'Start from beginning')"
            })
        
        # Check edge branches
        ok_edges = {}
        fail_edges = {}
        
        for edge in edges:
            source = edge.get("source")
            branch = edge.get("data", {}).get("branch", "ok")
            
            if branch == "ok":
                if source in ok_edges:
                    errors.append({
                        "node_uid": source,
                        "error": "MULTIPLE_OK_EDGES",
                        "message": "Node has multiple OK edges"
                    })
                ok_edges[source] = True
            else:
                if source in fail_edges:
                    errors.append({
                        "node_uid": source,
                        "error": "MULTIPLE_FAIL_EDGES",
                        "message": "Node has multiple FAIL edges"
                    })
                fail_edges[source] = True
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
