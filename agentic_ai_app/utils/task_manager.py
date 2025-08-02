"""
Task Manager - Handles task lifecycle and status tracking
"""

import asyncio
import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import uuid

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskManager:
    """Manages task lifecycle and status tracking"""
    
    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self._initialized = False
    
    async def initialize(self):
        """Initialize the task manager"""
        if self._initialized:
            return
        
        logger.info("Initializing Task Manager...")
        self._initialized = True
        logger.info("Task Manager initialized successfully")
    
    async def create_task(self, task_id: str, task_type: str, description: str, 
                         parameters: Dict[str, Any]) -> str:
        """Create a new task"""
        task_data = {
            "task_id": task_id,
            "task_type": task_type,
            "description": description,
            "parameters": parameters,
            "status": TaskStatus.PENDING,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "progress": 0,
            "result": None,
            "error": None,
            "logs": []
        }
        
        self.tasks[task_id] = task_data
        logger.info(f"Created task: {task_id}")
        return task_id
    
    async def update_task_status(self, task_id: str, status: TaskStatus, 
                               progress: Optional[int] = None, 
                               result: Optional[Any] = None,
                               error: Optional[str] = None):
        """Update task status"""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        task["status"] = status
        task["updated_at"] = datetime.now()
        
        if progress is not None:
            task["progress"] = progress
        
        if result is not None:
            task["result"] = result
        
        if error is not None:
            task["error"] = error
        
        logger.info(f"Updated task {task_id} status to {status.value}")
    
    async def complete_task(self, task_id: str, result: Any):
        """Mark task as completed"""
        await self.update_task_status(task_id, TaskStatus.COMPLETED, progress=100, result=result)
        
        # Remove from running tasks if present
        if task_id in self.running_tasks:
            del self.running_tasks[task_id]
    
    async def fail_task(self, task_id: str, error: str):
        """Mark task as failed"""
        await self.update_task_status(task_id, TaskStatus.FAILED, error=error)
        
        # Remove from running tasks if present
        if task_id in self.running_tasks:
            del self.running_tasks[task_id]
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        
        # Cancel the asyncio task if it's running
        if task_id in self.running_tasks:
            running_task = self.running_tasks[task_id]
            running_task.cancel()
            del self.running_tasks[task_id]
        
        await self.update_task_status(task_id, TaskStatus.CANCELLED)
        logger.info(f"Cancelled task: {task_id}")
        return True
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status and details"""
        if task_id not in self.tasks:
            return {"error": "Task not found"}
        
        task = self.tasks[task_id]
        return {
            "task_id": task["task_id"],
            "task_type": task["task_type"],
            "description": task["description"],
            "status": task["status"].value,
            "progress": task["progress"],
            "created_at": task["created_at"].isoformat(),
            "updated_at": task["updated_at"].isoformat(),
            "result": task["result"],
            "error": task["error"],
            "logs": task["logs"]
        }
    
    async def list_tasks(self, status: Optional[TaskStatus] = None, 
                        task_type: Optional[str] = None) -> list:
        """List tasks with optional filtering"""
        tasks = []
        
        for task in self.tasks.values():
            # Apply filters
            if status and task["status"] != status:
                continue
            
            if task_type and task["task_type"] != task_type:
                continue
            
            tasks.append({
                "task_id": task["task_id"],
                "task_type": task["task_type"],
                "description": task["description"],
                "status": task["status"].value,
                "progress": task["progress"],
                "created_at": task["created_at"].isoformat(),
                "updated_at": task["updated_at"].isoformat()
            })
        
        return tasks
    
    async def add_task_log(self, task_id: str, log_message: str):
        """Add a log message to a task"""
        if task_id not in self.tasks:
            return
        
        self.tasks[task_id]["logs"].append({
            "timestamp": datetime.now().isoformat(),
            "message": log_message
        })
    
    async def cleanup_completed_tasks(self, max_age_hours: int = 24):
        """Clean up old completed tasks"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        tasks_to_remove = []
        
        for task_id, task in self.tasks.items():
            if (task["status"] in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED] and
                task["updated_at"] < cutoff_time):
                tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            del self.tasks[task_id]
            logger.info(f"Cleaned up old task: {task_id}")
        
        return len(tasks_to_remove)
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get task statistics"""
        stats = {
            "total_tasks": len(self.tasks),
            "by_status": {},
            "by_type": {},
            "running_tasks": len(self.running_tasks)
        }
        
        # Count by status
        for status in TaskStatus:
            count = sum(1 for task in self.tasks.values() if task["status"] == status)
            stats["by_status"][status.value] = count
        
        # Count by type
        type_counts = {}
        for task in self.tasks.values():
            task_type = task["task_type"]
            type_counts[task_type] = type_counts.get(task_type, 0) + 1
        
        stats["by_type"] = type_counts
        
        return stats
    
    async def cleanup(self):
        """Cleanup task manager resources"""
        logger.info("Cleaning up Task Manager...")
        
        # Cancel all running tasks
        for task_id in list(self.running_tasks.keys()):
            await self.cancel_task(task_id)
        
        logger.info("Task Manager cleanup completed")