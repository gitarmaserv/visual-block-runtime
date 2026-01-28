"""API routes for execution control."""
import asyncio
import json
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

from backend.runtime.executor import GraphExecutor, ExecutionState
from backend.db.database import ProjectDatabase

router = APIRouter(prefix="/run", tags=["execution"])

# Global executor instance
_executor: Optional[GraphExecutor] = None


class StartRequest(BaseModel):
    path: str
    graph_name: str
    node_uid: Optional[str] = None
    from_beginning: bool = False
    run_id: Optional[str] = None


@router.post("/start_from_beginning")
async def start_from_beginning(req: StartRequest, background_tasks: BackgroundTasks):
    """Start execution from beginning (Start node)."""
    return await _start_execution(req, background_tasks)


@router.post("/start_from_selected")
async def start_from_selected(req: StartRequest, background_tasks: BackgroundTasks):
    """Start execution from selected node."""
    return await _start_execution(req, background_tasks)


async def _start_execution(req: StartRequest, background_tasks: BackgroundTasks):
    """Internal execution start."""
    global _executor
    
    if _executor and _executor.state == ExecutionState.RUNNING:
        raise HTTPException(status_code=400, detail="Execution already in progress")
    
    try:
        # Load graph
        db = ProjectDatabase(f"{req.path}/project.sqlite")
        graph_json = db.load_graph(req.graph_name)
        
        if not graph_json:
            raise HTTPException(status_code=404, detail="Graph not found")
        
        # Create executor
        log_path = f"{req.path}/log.txt"
        _executor = GraphExecutor(req.path, log_path, event_callback=_broadcast_event)
        
        # Start run
        db_path = f"{req.path}/project.sqlite"
        run_db = ProjectDatabase(db_path)
        run_id = req.run_id or f"run_{__import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')}"
        graph_id = run_db.get_graph_id(req.graph_name)
        run_db.start_run(run_id, graph_id)
        
        # Run in background
        background_tasks.add_task(
            _run_graph,
            _executor,
            graph_json,
            req.node_uid,
            req.from_beginning
        )
        
        return {"success": True, "run_id": run_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _run_graph(executor: GraphExecutor, graph: dict, start_node: str, from_beginning: bool):
    """Run graph in background."""
    await executor.execute(graph, start_node, from_beginning)


@router.post("/stop_soft")
def soft_stop():
    """Request soft stop."""
    global _executor
    if _executor:
        _executor.soft_stop()
        return {"success": True}
    return {"success": False, "message": "No active execution"}


@router.post("/stop_hard")
def hard_stop():
    """Request hard stop."""
    global _executor
    if _executor:
        _executor.hard_stop()
        return {"success": True}
    return {"success": False, "message": "No active execution"}


@router.post("/resume")
def resume():
    """Resume from pause."""
    global _executor
    if _executor:
        _executor.resume()
        return {"success": True}
    return {"success": False, "message": "No active execution"}


@router.get("/status")
def get_status():
    """Get current execution status."""
    global _executor
    if _executor:
        return {
            "state": _executor.state.value,
            "run_id": _executor.current_run_id,
            "active_node_uid": _executor.active_node_uid,
            "active_node_title": _executor.active_node_title
        }
    return {
        "state": ExecutionState.IDLE.value,
        "run_id": None,
        "active_node_uid": None,
        "active_node_title": None
    }


def _broadcast_event(event: dict):
    """Placeholder for event broadcasting (WebSocket would implement this)."""
    # In real implementation, this would send to all connected WebSocket clients
    print(f"Event: {json.dumps(event)}")
