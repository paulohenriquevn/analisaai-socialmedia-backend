"""
Task queue service for handling background tasks and async operations.
"""
import threading
import queue
import logging
import time
import os
from datetime import datetime
import uuid
from functools import wraps

logger = logging.getLogger(__name__)

# Global task queue
task_queue = queue.Queue()

# Task status storage
task_status = {}

# Number of worker threads
NUM_WORKERS = 2

# Task queue running flag
queue_running = False

class Task:
    """Represents a background task with metadata."""
    
    def __init__(self, func, args=None, kwargs=None, task_id=None, description=None):
        """Initialize a new task."""
        self.func = func
        self.args = args or []
        self.kwargs = kwargs or {}
        self.task_id = task_id or str(uuid.uuid4())
        self.description = description or f"Task {self.task_id}"
        self.created_at = datetime.utcnow()
        self.started_at = None
        self.completed_at = None
        self.status = "pending"
        self.result = None
        self.error = None
    
    def execute(self):
        """Execute the task and store the result or error."""
        self.started_at = datetime.utcnow()
        self.status = "running"
        
        try:
            logger.info(f"Executing task {self.task_id}: {self.description}")
            self.result = self.func(*self.args, **self.kwargs)
            self.status = "completed"
            logger.info(f"Task {self.task_id} completed successfully")
        except Exception as e:
            logger.error(f"Task {self.task_id} failed with error: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            self.error = str(e)
            self.status = "failed"
        
        self.completed_at = datetime.utcnow()
        return self.result

def worker():
    """Worker thread that processes tasks from the queue."""
    global queue_running
    
    while queue_running:
        try:
            # Get a task from the queue with a timeout
            # This allows workers to exit when queue_running is set to False
            task = task_queue.get(timeout=1)
            
            # Update task status
            task_status[task.task_id] = task
            
            # Execute the task directly
            # This will work for independent functions that don't need Flask context
            # For functions that need context, we'll handle that in the task decorator
            logger.info(f"Executing task {task.task_id}")
            task.execute()
            
            # Update task status after execution
            task_status[task.task_id] = task
            
            # Mark task as done in the queue
            task_queue.task_done()
            
        except queue.Empty:
            # Queue is empty, just continue waiting
            continue
        except Exception as e:
            logger.error(f"Error in worker thread: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())

def start_workers():
    """Start worker threads to process tasks."""
    global queue_running
    if not queue_running:
        queue_running = True
        for i in range(NUM_WORKERS):
            t = threading.Thread(target=worker)
            t.daemon = True
            t.start()
            logger.info(f"Started worker thread {i+1}")

def stop_workers():
    """Stop worker threads."""
    global queue_running
    queue_running = False
    logger.info("Stopping worker threads...")

def enqueue_task(func, args=None, kwargs=None, task_id=None, description=None):
    """
    Add a task to the queue for asynchronous execution.
    
    Args:
        func: The function to execute
        args: List of positional arguments for the function
        kwargs: Dictionary of keyword arguments for the function
        task_id: Optional unique identifier for the task
        description: Optional description of the task
        
    Returns:
        str: The task ID
    """
    # Ensure workers are running
    if not queue_running:
        start_workers()
    
    # Create a new task
    task = Task(func, args, kwargs, task_id, description)
    
    # Add task to status tracking
    task_status[task.task_id] = task
    
    # Add to queue
    task_queue.put(task)
    
    logger.info(f"Enqueued task {task.task_id}: {task.description}")
    
    return task.task_id

def get_task_status(task_id):
    """
    Get the status of a task.
    
    Args:
        task_id: The ID of the task
        
    Returns:
        dict: The task status information
    """
    task = task_status.get(task_id)
    if not task:
        return {
            "task_id": task_id,
            "status": "unknown",
            "error": "Task not found"
        }
    
    # Format timestamps for JSON serialization
    created_at = task.created_at.isoformat() if task.created_at else None
    started_at = task.started_at.isoformat() if task.started_at else None
    completed_at = task.completed_at.isoformat() if task.completed_at else None
    
    # Calculate task duration if applicable
    duration = None
    if task.started_at and task.completed_at:
        duration = (task.completed_at - task.started_at).total_seconds()
    
    return {
        "task_id": task.task_id,
        "description": task.description,
        "status": task.status,
        "created_at": created_at,
        "started_at": started_at,
        "completed_at": completed_at,
        "duration": duration,
        "error": task.error
    }

def wait_for_task(task_id, timeout=None):
    """
    Wait for a task to complete.
    
    Args:
        task_id: The ID of the task
        timeout: Maximum time to wait in seconds
        
    Returns:
        dict: The task result or status
    """
    start_time = time.time()
    while True:
        status = get_task_status(task_id)
        
        if status['status'] in ['completed', 'failed']:
            return status
        
        # Check timeout
        if timeout and (time.time() - start_time) > timeout:
            return {
                "task_id": task_id,
                "status": "timeout",
                "error": f"Timed out waiting for task completion after {timeout} seconds"
            }
        
        # Sleep briefly to avoid CPU spinning
        time.sleep(0.1)

def get_queue_info():
    """
    Get information about the task queue.
    
    Returns:
        dict: Queue statistics
    """
    return {
        "queue_size": task_queue.qsize(),
        "active_tasks": len([t for t in task_status.values() if t.status == "running"]),
        "pending_tasks": len([t for t in task_status.values() if t.status == "pending"]),
        "completed_tasks": len([t for t in task_status.values() if t.status == "completed"]),
        "failed_tasks": len([t for t in task_status.values() if t.status == "failed"]),
        "workers_running": queue_running,
        "num_workers": NUM_WORKERS
    }

def cleanup_old_tasks(max_age_hours=24):
    """
    Remove old completed tasks from status tracking.
    
    Args:
        max_age_hours: Maximum age in hours for completed tasks
        
    Returns:
        int: Number of tasks removed
    """
    now = datetime.utcnow()
    to_remove = []
    
    for task_id, task in task_status.items():
        if task.status in ['completed', 'failed']:
            if task.completed_at:
                age = (now - task.completed_at).total_seconds() / 3600  # Hours
                if age > max_age_hours:
                    to_remove.append(task_id)
    
    # Remove tasks
    for task_id in to_remove:
        del task_status[task_id]
    
    return len(to_remove)

def async_task(description=None):
    """
    Decorator to run a function asynchronously.
    
    Args:
        description: Optional description for the task
        
    Returns:
        The task ID
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            task_description = description or f"{func.__name__} async task"
            return enqueue_task(func, args, kwargs, description=task_description)
        return wrapper
    return decorator