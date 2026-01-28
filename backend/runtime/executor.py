"""Runtime executor for graph execution."""
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from enum import Enum

from .context import RuntimeContext, Logger


class ExecutionState(Enum):
    """State of the execution."""
    IDLE = "Idle"
    RUNNING = "Running"
    PAUSED = "Paused"
    STOPPED = "Stopped"
    FINISHED = "Finished"
    ERROR = "Error"


class GraphExecutor:
    """Executes the graph based on nodes and edges."""
    
    def __init__(self, project_dir: str, log_path: str, event_callback: Callable = None):
        self.project_dir = project_dir
        self.log_path = log_path
        self.logger = Logger(log_path)
        self.event_callback = event_callback or (lambda x: None)
        
        self.state = ExecutionState.IDLE
        self.current_run_id = None
        self.active_node_uid = None
        self.active_node_title = None
        
        self._stop_requested = False
        self._hard_stop_requested = False
        self._should_pause = False
    
    async def execute(self, graph: Dict, start_node_id: str = None, 
                      from_beginning: bool = False) -> Dict:
        """
        Execute the graph starting from a node.
        
        Args:
            graph: Graph data with nodes and edges
            start_node_id: Node UID to start from (if not from_beginning)
            from_beginning: If True, start from __start__ node
        
        Returns:
            Execution result
        """
        self._stop_requested = False
        self._hard_stop_requested = False
        self._should_pause = False
        self.state = ExecutionState.RUNNING
        
        # Generate run_id
        run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_run_id = run_id
        
        self.logger.info(f"Execution started (from_beginning={from_beginning})", run_id=run_id)
        self._emit_state()
        
        try:
            # Build adjacency list from edges
            edges = graph.get("edges", [])
            edges_by_node = self._build_edge_map(edges)
            
            # Get nodes
            nodes = graph.get("nodes", [])
            nodes_dict = {n["id"]: n for n in nodes}
            
            # Find start node
            start_uid = None
            if from_beginning:
                # Find __start__ node
                for node in nodes:
                    if node.get("data", {}).get("plugin_id") == "__start__":
                        start_uid = node["id"]
                        break
                if not start_uid:
                    return {"success": False, "error": "No Start node found"}
            elif start_node_id:
                start_uid = start_node_id
            else:
                return {"success": False, "error": "No start node specified"}
            
            # Start traversal from start node
            result = await self._execute_node(
                start_uid, nodes_dict, edges_by_node, run_id
            )
            
            if self._hard_stop_requested:
                self.state = ExecutionState.STOPPED
                self.logger.info("Execution stopped (hard)", run_id=run_id)
            else:
                self.state = ExecutionState.FINISHED
                self.logger.info("Execution finished", run_id=run_id)
            
            return {"success": True, "result": result}
            
        except Exception as e:
            self.state = ExecutionState.ERROR
            self.logger.error(f"Execution error: {str(e)}", run_id=run_id)
            return {"success": False, "error": str(e)}
        finally:
            self._emit_state()
            self.current_run_id = None
            self.active_node_uid = None
    
    async def _execute_node(self, node_uid: str, nodes_dict: Dict, 
                           edges_by_node: Dict, run_id: str) -> Dict:
        """Execute a single node."""
        
        # Check for hard stop
        if self._hard_stop_requested:
            return {"status": "STOPPED", "code": "HARD_STOP"}
        
        # Check for soft stop (after current node completes)
        if self._stop_requested:
            return {"status": "STOPPED", "code": "SOFT_STOP"}
        
        node = nodes_dict.get(node_uid)
        if not node:
            return {"status": "ERROR", "code": "NODE_NOT_FOUND", "node_uid": node_uid}
        
        node_data = node.get("data", {})
        plugin_id = node_data.get("plugin_id")
        node_title = node_data.get("node_title", plugin_id)
        
        self.active_node_uid = node_uid
        self.active_node_title = node_title
        self._emit_state()
        
        self.logger.info(f"Node started: {node_title}", run_id=run_id, 
                        node_uid=node_uid, node_title=node_title)
        self._emit_node_status(node_uid, "running")
        
        # Check for breakpoint (pause before execution)
        if node_data.get("breakpoint"):
            self.state = ExecutionState.PAUSED
            self.logger.info("Paused at breakpoint", run_id=run_id,
                           node_uid=node_uid, node_title=node_title)
            self._emit_state()
            
            # Wait until unpaused or stopped
            while self.state == ExecutionState.PAUSED and not self._hard_stop_requested:
                await asyncio.sleep(0.1)
            
            if self._hard_stop_requested:
                return {"status": "STOPPED", "code": "HARD_STOP"}
        
        # Get plugin
        plugin = self._get_plugin(plugin_id)
        if not plugin:
            result = {"status": "ERROR", "code": "PLUGIN_NOT_FOUND", 
                     "message": f"Plugin {plugin_id} not found"}
            self._finish_node(node_uid, node_title, run_id, result)
            return result
        
        # Get parameters and variables
        params = node_data.get("params", {})
        input_var_ref = node_data.get("input_var_ref")
        output_var_ref = node_data.get("output_var_ref")
        
        # Validate input requirement
        if plugin.get("requires_input") and not input_var_ref:
            result = {"status": "ERROR", "code": "INPUT.NOT_SELECTED",
                     "message": "Input variable not selected"}
            self._finish_node(node_uid, node_title, run_id, result)
            return result
        
        # Validate output requirement
        if plugin.get("produces_output") and not output_var_ref:
            result = {"status": "ERROR", "code": "OUTPUT.NOT_SELECTED",
                     "message": "Output variable not selected"}
            self._finish_node(node_uid, node_title, run_id, result)
            return result
        
        # Get input data
        in_data = None
        if input_var_ref:
            in_data = self._get_variable_value(input_var_ref)
        
        # Execute plugin
        ctx = RuntimeContext(
            run_id=run_id,
            node_uid=node_uid,
            node_title=node_title,
            logger=self.logger,
            project_dir=self.project_dir
        )
        
        try:
            if plugin.get("run_func"):
                run_result = plugin["run_func"](ctx, params, in_data)
            else:
                run_result = {"status": "ERROR", "code": "NO_RUN_FUNC",
                             "message": "Plugin has no run function"}
        except Exception as e:
            run_result = {"status": "ERROR", "code": "PLUGIN_EXCEPTION",
                         "message": str(e), "details": {"exception": str(type(e).__name__)}}
        
        # Handle result
        if not isinstance(run_result, dict):
            run_result = {"status": "ERROR", "code": "INVALID_RESULT",
                         "message": "Plugin returned non-dict result"}
        
        # Save output if OK
        if run_result.get("status") == "OK" and output_var_ref:
            output = run_result.get("output")
            self._set_variable_value(output_var_ref, output)
        
        # Determine next node
        status = run_result.get("status", "ERROR")
        
        if status == "OK":
            next_uid = self._get_next_node(node_uid, "ok", edges_by_node)
            if next_uid:
                return await self._execute_node(next_uid, nodes_dict, edges_by_node, run_id)
        elif status == "FAIL":
            next_uid = self._get_next_node(node_uid, "fail", edges_by_node)
            if next_uid:
                return await self._execute_node(next_uid, nodes_dict, edges_by_node, run_id)
        elif status == "ERROR":
            if node_data.get("error_to_fail"):
                next_uid = self._get_next_node(node_uid, "fail", edges_by_node)
                if next_uid:
                    return await self._execute_node(next_uid, nodes_dict, edges_by_node, run_id)
            # else: stop execution
        
        self._finish_node(node_uid, node_title, run_id, run_result)
        return run_result
    
    def _finish_node(self, node_uid: str, node_title: str, run_id: str, result: Dict):
        """Finish node execution and log result."""
        status = result.get("status", "ERROR")
        code = result.get("code", "")
        
        log_level = "INFO" if status == "OK" else ("WARN" if status == "FAIL" else "ERROR")
        message = f"Node finished: status={status}" + (f" code={code}" if code else "")
        
        self.logger.log(log_level, message, run_id=run_id, 
                       node_uid=node_uid, node_title=node_title)
        self._emit_node_status(node_uid, status.lower())
        
        self.active_node_uid = None
        self.active_node_title = None
    
    def _build_edge_map(self, edges: List[Dict]) -> Dict[str, List[Dict]]:
        """Build adjacency list from edges."""
        result = {}
        for edge in edges:
            source = edge.get("source")
            if source not in result:
                result[source] = []
            result[source].append({
                "target": edge.get("target"),
                "branch": edge.get("data", {}).get("branch", "ok")
            })
        return result
    
    def _get_next_node(self, node_uid: str, branch: str, edges_by_node: Dict) -> Optional[str]:
        """Get the next node based on branch."""
        edges = edges_by_node.get(node_uid, [])
        for edge in edges:
            if edge.get("branch") == branch:
                return edge.get("target")
        return None
    
    def _get_plugin(self, plugin_id: str) -> Optional[Dict]:
        """Get a loaded plugin by ID."""
        from backend.plugins.loader import get_plugin_loader
        return get_plugin_loader().get_plugin(plugin_id)
    
    def _get_variable_value(self, ref: str) -> Any:
        """Get variable value by ref."""
        from backend.db.database import ProjectDatabase, AppDatabase
        
        try:
            if ref.startswith("proj:"):
                var_id = int(ref[5:])
                db = ProjectDatabase(f"{self.project_dir}/project.sqlite")
                var = db.get_project_var(var_id)
                if var:
                    return json.loads(var.get("value_json", "null"))
            elif ref.startswith("glob:"):
                var_id = int(ref[5:])
                db = AppDatabase(f"{self.project_dir}/../app.sqlite")
                var = db.get_global_var(var_id)
                if var:
                    return json.loads(var.get("value_json", "null"))
        except Exception:
            pass
        return None
    
    def _set_variable_value(self, ref: str, value: Any):
        """Set variable value by ref."""
        from backend.db.database import ProjectDatabase, AppDatabase
        
        try:
            if ref.startswith("proj:"):
                var_id = int(ref[5:])
                db = ProjectDatabase(f"{self.project_dir}/project.sqlite")
                db.set_project_var_value(var_id, value)
            elif ref.startswith("glob:"):
                var_id = int(ref[5:])
                db = AppDatabase(f"{self.project_dir}/../app.sqlite")
                db.set_global_var_value(var_id, value)
        except Exception as e:
            self.logger.error(f"Failed to set variable {ref}: {e}")
    
    def _emit_state(self):
        """Emit state change event."""
        self.event_callback({
            "type": "run_state",
            "state": self.state.value,
            "run_id": self.current_run_id,
            "active_node_uid": self.active_node_uid,
            "active_node_title": self.active_node_title
        })
    
    def _emit_node_status(self, node_uid: str, status: str):
        """Emit node status change event."""
        self.event_callback({
            "type": "node_status",
            "node_uid": node_uid,
            "status": status
        })
    
    def soft_stop(self):
        """Request soft stop."""
        self._stop_requested = True
    
    def hard_stop(self):
        """Request hard stop."""
        self._hard_stop_requested = True
    
    def resume(self):
        """Resume from pause."""
        if self.state == ExecutionState.PAUSED:
            self.state = ExecutionState.RUNNING
            self._emit_state()
