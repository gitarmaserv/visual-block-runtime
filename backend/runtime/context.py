"""Logging module for writing to log.txt."""
import os
from datetime import datetime
from typing import Optional
import json


class Logger:
    """Logger that writes to log.txt file."""
    
    def __init__(self, log_path: str):
        self.log_path = log_path
        self._ensure_log_exists()
    
    def _ensure_log_exists(self):
        """Create log file if not exists."""
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        if not os.path.exists(self.log_path):
            with open(self.log_path, 'w') as f:
                pass
    
    def _write(self, level: str, message: str, run_id: str = None, 
               node_uid: str = None, node_title: str = None, details: dict = None):
        """Write a log line to file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        # Format: YYYY-MM-DD HH:MM:SS.mmm | run=<run_id> | node=<node_uid> | title="<node_title>" | lvl=<LEVEL> | msg=<message>
        
        parts = [f"{timestamp}"]
        
        if run_id:
            parts.append(f"run={run_id}")
        else:
            parts.append("run=-")
        
        if node_uid:
            parts.append(f"node={node_uid}")
        else:
            parts.append("node=-")
        
        if node_title:
            parts.append(f'title="{node_title}"')
        else:
            parts.append('title="-"')
        
        parts.append(f"lvl={level}")
        
        # Escape newlines in message
        escaped_msg = message.replace('\n', '\\n').replace('\r', '\\r')
        parts.append(f"msg={escaped_msg}")
        
        if details:
            details_str = json.dumps(details)
            parts.append(f"details={details_str}")
        
        line = " | ".join(parts) + "\n"
        
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(line)
    
    def info(self, message: str, run_id: str = None, node_uid: str = None, 
             node_title: str = None, details: dict = None):
        """Log INFO level message."""
        self._write("INFO", message, run_id, node_uid, node_title, details)
    
    def debug(self, message: str, run_id: str = None, node_uid: str = None,
              node_title: str = None, details: dict = None):
        """Log DEBUG level message."""
        self._write("DEBUG", message, run_id, node_uid, node_title, details)
    
    def warn(self, message: str, run_id: str = None, node_uid: str = None,
             node_title: str = None, details: dict = None):
        """Log WARN level message."""
        self._write("WARN", message, run_id, node_uid, node_title, details)
    
    def error(self, message: str, run_id: str = None, node_uid: str = None,
              node_title: str = None, details: dict = None):
        """Log ERROR level message."""
        self._write("ERROR", message, run_id, node_uid, node_title, details)
    
    def tail(self, lines: int = 100, filter_level: str = None) -> list:
        """
        Get last N lines from log file.
        
        Args:
            lines: Number of lines to return
            filter_level: Optional level filter (INFO, DEBUG, WARN, ERROR)
        """
        if not os.path.exists(self.log_path):
            return []
        
        with open(self.log_path, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
        
        # Filter by level if specified
        if filter_level:
            filtered = []
            for line in all_lines:
                if f"lvl={filter_level}" in line or f"| lvl={filter_level}" in line:
                    filtered.append(line.strip())
            all_lines = filtered
        
        # Return last N lines
        return [line.strip() for line in all_lines[-lines:]]


class RuntimeContext:
    """Context object passed to plugin run() function."""
    
    def __init__(self, run_id: str, node_uid: str, node_title: str, 
                 logger: Logger, project_dir: str = None, artifacts_dir: str = None):
        self.run_id = run_id
        self.node_uid = node_uid
        self.node_title = node_title
        self._logger = logger
        self.project_dir = project_dir
        self.artifacts_dir = artifacts_dir
    
    def log(self, level: str, message: str, details: dict = None):
        """Log a message with context."""
        self._logger._write(
            level=level,
            message=message,
            run_id=self.run_id,
            node_uid=self.node_uid,
            node_title=self.node_title,
            details=details
        )
    
    def info(self, message: str, details: dict = None):
        """Log INFO message."""
        self.log("INFO", message, details)
    
    def debug(self, message: str, details: dict = None):
        """Log DEBUG message."""
        self.log("DEBUG", message, details)
    
    def warn(self, message: str, details: dict = None):
        """Log WARN message."""
        self.log("WARN", message, details)
    
    def error(self, message: str, details: dict = None):
        """Log ERROR message."""
        self.log("ERROR", message, details)
    
    @property
    def project_dir(self) -> str:
        """Get project directory."""
        return self._project_dir
    
    @project_dir.setter
    def project_dir(self, value: str):
        self._project_dir = value
    
    @property
    def artifacts_dir(self) -> str:
        """Get artifacts directory."""
        if self._artifacts_dir is None and self._project_dir:
            return os.path.join(self._project_dir, "artifacts")
        return self._artifacts_dir
    
    @artifacts_dir.setter
    def artifacts_dir(self, value: str):
        self._artifacts_dir = value
