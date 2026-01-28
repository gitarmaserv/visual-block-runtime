"""API routes for logs."""
from fastapi import APIRouter
from typing import Optional

from backend.runtime.context import Logger

router = APIRouter(prefix="/log", tags=["logs"])


@router.get("/tail")
def get_log_tail(path: str, lines: int = 100, level: Optional[str] = None):
    """Get last N lines from log file."""
    log_path = f"{path}/log.txt"
    logger = Logger(log_path)
    
    tail_lines = logger.tail(lines, level)
    
    return {"lines": tail_lines}


@router.get("/tail_lines")
def get_log_tail_lines(path: str, lines: int = 100):
    """Get last N lines from log file."""
    log_path = f"{path}/log.txt"
    logger = Logger(log_path)
    
    tail_lines = logger.tail(lines)
    
    return {"lines": tail_lines}
