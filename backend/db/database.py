"""Database module for SQLite operations."""
import sqlite3
import json
import os
from typing import Any, Dict, List, Optional
from contextlib import contextmanager
from datetime import datetime


class Database:
    """Base database manager."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_db_exists()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _ensure_db_exists(self):
        """Create database file if not exists."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with self.get_connection() as conn:
            pass  # Just create the file
    
    def execute(self, query: str, params: tuple = ()):
        """Execute a query."""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor
    
    def fetch_one(self, query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        """Fetch one row."""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchone()
    
    def fetch_all(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Fetch all rows."""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchall()
    
    def insert(self, query: str, params: tuple = ()) -> int:
        """Insert and return rowid."""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.lastrowid


class AppDatabase(Database):
    """Application database (app.sqlite)."""
    
    def init_schema(self):
        """Initialize database schema."""
        with self.get_connection() as conn:
            # App settings
            conn.execute("""
                CREATE TABLE IF NOT EXISTS app_settings (
                    key TEXT PRIMARY KEY,
                    value_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Global variables definition
            conn.execute("""
                CREATE TABLE IF NOT EXISTS global_vars_def (
                    var_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    base_name TEXT NOT NULL,
                    title TEXT NOT NULL UNIQUE,
                    description TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Global variables values
            conn.execute("""
                CREATE TABLE IF NOT EXISTS global_vars_val (
                    var_id INTEGER PRIMARY KEY,
                    value_json TEXT,
                    updated_at TEXT NOT NULL
                )
            """)
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        row = self.fetch_one(
            "SELECT value_json FROM app_settings WHERE key = ?",
            (key,)
        )
        if row:
            return json.loads(row["value_json"])
        return default
    
    def set_setting(self, key: str, value: Any):
        """Set a setting value."""
        value_json = json.dumps(value)
        now = datetime.now().isoformat()
        self.execute(
            "INSERT OR REPLACE INTO app_settings (key, value_json, updated_at) VALUES (?, ?, ?)",
            (key, value_json, now)
        )
    
    # Global variables
    def create_global_var(self, base_name: str, description: str = "") -> Dict:
        """Create a new global variable."""
        now = datetime.now().isoformat()
        with self.get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO global_vars_def (base_name, title, description, created_at) VALUES (?, ?, ?, ?)",
                (base_name, "", description, now)
            )
            var_id = cursor.lastrowid
            
            # Generate title
            title = f"{var_id}Value_Glob_{base_name}"
            conn.execute(
                "UPDATE global_vars_def SET title = ? WHERE var_id = ?",
                (title, var_id)
            )
            
            # Create value entry
            conn.execute(
                "INSERT INTO global_vars_val (var_id, value_json, updated_at) VALUES (?, ?, ?)",
                (var_id, "null", now)
            )
            
            return {"var_id": var_id, "title": title}
    
    def get_global_vars(self) -> List[Dict]:
        """Get all global variables with values."""
        rows = self.fetch_all("""
            SELECT v_def.var_id, v_def.base_name, v_def.title, v_def.description,
                   v_val.value_json, v_val.updated_at
            FROM global_vars_def v_def
            JOIN global_vars_val v_val ON v_def.var_id = v_val.var_id
        """)
        return [
            {
                "var_id": row["var_id"],
                "base_name": row["base_name"],
                "title": row["title"],
                "description": row["description"],
                "value_json": row["value_json"],
                "updated_at": row["updated_at"]
            }
            for row in rows
        ]
    
    def set_global_var_value(self, var_id: int, value: Any):
        """Set global variable value."""
        value_json = json.dumps(value)
        now = datetime.now().isoformat()
        self.execute(
            "UPDATE global_vars_val SET value_json = ?, updated_at = ? WHERE var_id = ?",
            (value_json, now, var_id)
        )
    
    def get_global_var(self, var_id: int) -> Optional[Dict]:
        """Get a specific global variable."""
        row = self.fetch_one("""
            SELECT v_def.var_id, v_def.base_name, v_def.title, v_def.description,
                   v_val.value_json, v_val.updated_at
            FROM global_vars_def v_def
            JOIN global_vars_val v_val ON v_def.var_id = v_val.var_id
            WHERE v_def.var_id = ?
        """, (var_id,))
        if row:
            return {
                "var_id": row["var_id"],
                "base_name": row["base_name"],
                "title": row["title"],
                "description": row["description"],
                "value_json": row["value_json"],
                "updated_at": row["updated_at"]
            }
        return None


class ProjectDatabase(Database):
    """Project database (project.sqlite)."""

    def __init__(self, db_path: str):
        super().__init__(db_path)
        self.init_schema()

    def init_schema(self):
        """Initialize database schema."""
        with self.get_connection() as conn:
            # Graphs
            conn.execute("""
                CREATE TABLE IF NOT EXISTS graphs (
                    graph_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    graph_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Node settings
            conn.execute("""
                CREATE TABLE IF NOT EXISTS node_settings (
                    graph_id INTEGER NOT NULL,
                    node_uid TEXT NOT NULL,
                    plugin_id TEXT NOT NULL,
                    params_json TEXT NOT NULL,
                    input_var_ref TEXT,
                    output_var_ref TEXT,
                    error_to_fail INTEGER DEFAULT 0,
                    breakpoint INTEGER DEFAULT 0,
                    visual_json TEXT,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (graph_id, node_uid)
                )
            """)
            
            # Project variables definition
            conn.execute("""
                CREATE TABLE IF NOT EXISTS project_vars_def (
                    var_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    base_name TEXT NOT NULL,
                    title TEXT NOT NULL UNIQUE,
                    description TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Project variables values
            conn.execute("""
                CREATE TABLE IF NOT EXISTS project_vars_val (
                    var_id INTEGER PRIMARY KEY,
                    value_json TEXT,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Runs
            conn.execute("""
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    graph_id INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    finished_at TEXT,
                    error_message TEXT
                )
            """)
    
    # Graphs
    def save_graph(self, name: str, graph_json: Dict) -> int:
        """Save or update graph."""
        now = datetime.now().isoformat()
        try:
            graph_json_str = json.dumps(graph_json)
        except Exception as e:
            print(f"Cannot serialize graph_json: {e}, type: {type(graph_json)}")
            raise
        
        # Check if graph exists
        existing = self.fetch_one(
            "SELECT graph_id FROM graphs WHERE name = ?",
            (name,)
        )
        
        if existing:
            self.execute(
                "UPDATE graphs SET graph_json = ?, updated_at = ? WHERE name = ?",
                (graph_json_str, now, name)
            )
            return existing["graph_id"]
        else:
            cursor = self.execute(
                "INSERT INTO graphs (name, graph_json, updated_at) VALUES (?, ?, ?)",
                (name, graph_json_str, now)
            )
            return cursor.lastrowid
    
    def load_graph(self, name: str) -> Optional[Dict]:
        """Load graph by name."""
        row = self.fetch_one(
            "SELECT graph_json FROM graphs WHERE name = ?",
            (name,)
        )
        if row:
            return json.loads(row["graph_json"])
        return None
    
    def get_graph_id(self, name: str) -> Optional[int]:
        """Get graph ID by name."""
        row = self.fetch_one(
            "SELECT graph_id FROM graphs WHERE name = ?",
            (name,)
        )
        return row["graph_id"] if row else None
    
    # Node settings
    def save_node_settings(self, graph_id: int, node_uid: str, settings: Dict):
        """Save node settings."""
        now = datetime.now().isoformat()
        
        params_json = json.dumps(settings.get("params", {}))
        input_var_ref = settings.get("input_var_ref")
        output_var_ref = settings.get("output_var_ref")
        error_to_fail = 1 if settings.get("error_to_fail") else 0
        breakpoint = 1 if settings.get("breakpoint") else 0
        visual_json = json.dumps(settings.get("visual", {}))
        
        self.execute("""
            INSERT OR REPLACE INTO node_settings 
            (graph_id, node_uid, plugin_id, params_json, input_var_ref, output_var_ref, 
             error_to_fail, breakpoint, visual_json, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            graph_id, node_uid, settings.get("plugin_id", ""),
            params_json, input_var_ref, output_var_ref,
            error_to_fail, breakpoint, visual_json, now
        ))
    
    def get_node_settings(self, graph_id: int) -> Dict[str, Dict]:
        """Get all node settings for a graph."""
        rows = self.fetch_all(
            "SELECT * FROM node_settings WHERE graph_id = ?",
            (graph_id,)
        )
        result = {}
        for row in rows:
            result[row["node_uid"]] = {
                "plugin_id": row["plugin_id"],
                "params": json.loads(row["params_json"]),
                "input_var_ref": row["input_var_ref"],
                "output_var_ref": row["output_var_ref"],
                "error_to_fail": bool(row["error_to_fail"]),
                "breakpoint": bool(row["breakpoint"]),
                "visual": json.loads(row["visual_json"] or "{}"),
                "updated_at": row["updated_at"]
            }
        return result
    
    # Project variables
    def create_project_var(self, base_name: str, description: str = "") -> Dict:
        """Create a new project variable."""
        now = datetime.now().isoformat()
        with self.get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO project_vars_def (base_name, title, description, created_at) VALUES (?, ?, ?, ?)",
                (base_name, "", description, now)
            )
            var_id = cursor.lastrowid
            
            # Generate title
            title = f"{var_id}Value_{base_name}"
            conn.execute(
                "UPDATE project_vars_def SET title = ? WHERE var_id = ?",
                (title, var_id)
            )
            
            # Create value entry
            conn.execute(
                "INSERT INTO project_vars_val (var_id, value_json, updated_at) VALUES (?, ?, ?)",
                (var_id, "null", now)
            )
            
            return {"var_id": var_id, "title": title}
    
    def get_project_vars(self) -> List[Dict]:
        """Get all project variables with values."""
        rows = self.fetch_all("""
            SELECT v_def.var_id, v_def.base_name, v_def.title, v_def.description,
                   v_val.value_json, v_val.updated_at
            FROM project_vars_def v_def
            JOIN project_vars_val v_val ON v_def.var_id = v_val.var_id
        """)
        return [
            {
                "var_id": row["var_id"],
                "base_name": row["base_name"],
                "title": row["title"],
                "description": row["description"],
                "value_json": row["value_json"],
                "updated_at": row["updated_at"]
            }
            for row in rows
        ]
    
    def set_project_var_value(self, var_id: int, value: Any):
        """Set project variable value."""
        value_json = json.dumps(value)
        now = datetime.now().isoformat()
        self.execute(
            "UPDATE project_vars_val SET value_json = ?, updated_at = ? WHERE var_id = ?",
            (value_json, now, var_id)
        )
    
    def get_project_var(self, var_id: int) -> Optional[Dict]:
        """Get a specific project variable."""
        row = self.fetch_one("""
            SELECT v_def.var_id, v_def.base_name, v_def.title, v_def.description,
                   v_val.value_json, v_val.updated_at
            FROM project_vars_def v_def
            JOIN project_vars_val v_val ON v_def.var_id = v_val.var_id
            WHERE v_def.var_id = ?
        """, (var_id,))
        if row:
            return {
                "var_id": row["var_id"],
                "base_name": row["base_name"],
                "title": row["title"],
                "description": row["description"],
                "value_json": row["value_json"],
                "updated_at": row["updated_at"]
            }
        return None
    
    # Runs
    def start_run(self, run_id: str, graph_id: int):
        """Start a new run."""
        now = datetime.now().isoformat()
        self.execute(
            "INSERT INTO runs (run_id, graph_id, status, started_at) VALUES (?, ?, ?, ?)",
            (run_id, graph_id, "running", now)
        )
    
    def finish_run(self, run_id: str, status: str, error_message: str = None):
        """Finish a run."""
        now = datetime.now().isoformat()
        self.execute(
            "UPDATE runs SET status = ?, finished_at = ?, error_message = ? WHERE run_id = ?",
            (status, now, error_message, run_id)
        )
    
    def get_runs(self) -> List[Dict]:
        """Get all runs."""
        rows = self.fetch_all("SELECT * FROM runs ORDER BY started_at DESC")
        return [dict(row) for row in rows]
