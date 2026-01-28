"""API routes for variables."""
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any

from backend.db.database import ProjectDatabase, AppDatabase

router = APIRouter(prefix="/vars", tags=["variables"])


class CreateVarRequest(BaseModel):
    path: str
    base_name: str
    description: str = ""


class SetVarRequest(BaseModel):
    ref: str
    value: Any


# Project Variables

@router.get("/project")
def get_project_vars(path: str):
    """Get all project variables."""
    try:
        db = ProjectDatabase(f"{path}/project.sqlite")
        vars = db.get_project_vars()
        
        # Add value preview
        for v in vars:
            try:
                v["value_preview"] = json.loads(v.get("value_json", "null"))
            except:
                v["value_preview"] = None
        
        return {"variables": vars}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/project/create")
def create_project_var(req: CreateVarRequest):
    """Create a new project variable."""
    try:
        db = ProjectDatabase(f"{req.path}/project.sqlite")
        result = db.create_project_var(req.base_name, req.description)
        
        return {
            "var_id": result["var_id"],
            "title": result["title"],
            "ref": f"proj:{result['var_id']}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/project/set")
def set_project_var_value(path: str, var_id: int, value: Any):
    """Set project variable value."""
    try:
        db = ProjectDatabase(f"{path}/project.sqlite")
        db.set_project_var_value(var_id, value)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Global Variables

@router.get("/global")
def get_global_vars(path: str):
    """Get all global variables."""
    try:
        db = AppDatabase(f"{path}/../app.sqlite")
        vars = db.get_global_vars()
        
        for v in vars:
            try:
                v["value_preview"] = json.loads(v.get("value_json", "null"))
            except:
                v["value_preview"] = None
        
        return {"variables": vars}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/global/create")
def create_global_var(req: CreateVarRequest):
    """Create a new global variable."""
    try:
        db = AppDatabase(f"{req.path}/../app.sqlite")
        result = db.create_global_var(req.base_name, req.description)
        
        return {
            "var_id": result["var_id"],
            "title": result["title"],
            "ref": f"glob:{result['var_id']}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/global/set")
def set_global_var_value(path: str, var_id: int, value: Any):
    """Set global variable value."""
    try:
        db = AppDatabase(f"{path}/../app.sqlite")
        db.set_global_var_value(var_id, value)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Generic

@router.get("/get")
def get_variable(ref: str, path: str):
    """Get variable value by ref."""
    try:
        if ref.startswith("proj:"):
            var_id = int(ref[5:])
            db = ProjectDatabase(f"{path}/project.sqlite")
            var = db.get_project_var(var_id)
        elif ref.startswith("glob:"):
            var_id = int(ref[5:])
            db = AppDatabase(f"{path}/../app.sqlite")
            var = db.get_global_var(var_id)
        else:
            raise HTTPException(status_code=400, detail="Invalid ref format")
        
        if not var:
            raise HTTPException(status_code=404, detail="Variable not found")
        
        return {"value": json.loads(var.get("value_json", "null"))}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/set")
def set_variable(req: SetVarRequest, path: str):
    """Set variable value by ref."""
    try:
        if req.ref.startswith("proj:"):
            var_id = int(req.ref[5:])
            db = ProjectDatabase(f"{path}/project.sqlite")
            db.set_project_var_value(var_id, req.value)
        elif req.ref.startswith("glob:"):
            var_id = int(req.ref[5:])
            db = AppDatabase(f"{path}/../app.sqlite")
            db.set_global_var_value(var_id, req.value)
        else:
            raise HTTPException(status_code=400, detail="Invalid ref format")
        
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
