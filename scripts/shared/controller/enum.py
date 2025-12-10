from enum import Enum
from dataclasses import dataclass
from typing import Any

class TaskStatus(Enum):
    SUCCESS = "success"
    PENDING = "pending" # for tasks that are loading
    FAILED = "failed"
    INTERRUPTED = "interrupted"
    UNKNOWN = "unknown"
    ERROR = "error"