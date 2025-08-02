"""
Agentic AI Application - Main Orchestrator
Coordinates all AI agents for meeting attendance, Jira management, code generation, and deployment
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agents.meeting_agent import MeetingAgent
from agents.jira_agent import JiraAgent
from agents.code_generator_agent import CodeGeneratorAgent
from agents.deployment_agent import DeploymentAgent
from core.orchestrator import AgentOrchestrator
from core.config import settings
from api.routes import router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for API requests
class TaskRequest(BaseModel):
    task_type: str
    description: str
    parameters: Dict[str, Any] = {}

class MeetingRequest(BaseModel):
    meeting_url: str
    meeting_type: str  # "zoom" or "teams"
    duration: int = 60  # minutes

class JiraRequest(BaseModel):
    action: str  # "get_story", "update_story", "create_story"
    story_id: str = None
    story_data: Dict[str, Any] = {}

class CodeGenerationRequest(BaseModel):
    user_story: str
    project_type: str = "web"
    framework: str = "react"

class DeploymentRequest(BaseModel):
    repository_url: str
    branch: str = "main"
    environment: str = "dev"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup application resources"""
    # Initialize orchestrator and agents
    app.state.orchestrator = AgentOrchestrator()
    await app.state.orchestrator.initialize()
    logger.info("Agentic AI Application started successfully")
    
    yield
    
    # Cleanup
    await app.state.orchestrator.cleanup()
    logger.info("Agentic AI Application shut down")

# Create FastAPI application
app = FastAPI(
    title="Agentic AI Assistant",
    description="AI-powered agent that can attend meetings, manage Jira, generate code, and deploy applications",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Agentic AI Assistant is running", "status": "healthy"}

@app.post("/api/v1/execute-task")
async def execute_task(request: TaskRequest, background_tasks: BackgroundTasks):
    """Execute a general task using the appropriate agent"""
    try:
        orchestrator = app.state.orchestrator
        task_id = await orchestrator.execute_task(
            task_type=request.task_type,
            description=request.description,
            parameters=request.parameters
        )
        
        return {"task_id": task_id, "status": "started", "message": "Task execution started"}
    
    except Exception as e:
        logger.error(f"Error executing task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/attend-meeting")
async def attend_meeting(request: MeetingRequest, background_tasks: BackgroundTasks):
    """Join a meeting and extract updates"""
    try:
        orchestrator = app.state.orchestrator
        task_id = await orchestrator.attend_meeting(
            meeting_url=request.meeting_url,
            meeting_type=request.meeting_type,
            duration=request.duration
        )
        
        return {"task_id": task_id, "status": "joining", "message": "Joining meeting and will extract updates"}
    
    except Exception as e:
        logger.error(f"Error attending meeting: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/jira-action")
async def jira_action(request: JiraRequest):
    """Perform Jira operations"""
    try:
        orchestrator = app.state.orchestrator
        result = await orchestrator.handle_jira_action(
            action=request.action,
            story_id=request.story_id,
            story_data=request.story_data
        )
        
        return {"result": result, "status": "completed"}
    
    except Exception as e:
        logger.error(f"Error with Jira action: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/generate-code")
async def generate_code(request: CodeGenerationRequest, background_tasks: BackgroundTasks):
    """Generate code based on user story"""
    try:
        orchestrator = app.state.orchestrator
        task_id = await orchestrator.generate_code(
            user_story=request.user_story,
            project_type=request.project_type,
            framework=request.framework
        )
        
        return {"task_id": task_id, "status": "generating", "message": "Code generation started"}
    
    except Exception as e:
        logger.error(f"Error generating code: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/deploy")
async def deploy_application(request: DeploymentRequest, background_tasks: BackgroundTasks):
    """Deploy application to specified environment"""
    try:
        orchestrator = app.state.orchestrator
        task_id = await orchestrator.deploy_application(
            repository_url=request.repository_url,
            branch=request.branch,
            environment=request.environment
        )
        
        return {"task_id": task_id, "status": "deploying", "message": "Deployment started"}
    
    except Exception as e:
        logger.error(f"Error deploying application: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/task/{task_id}/status")
async def get_task_status(task_id: str):
    """Get the status of a running task"""
    try:
        orchestrator = app.state.orchestrator
        status = await orchestrator.get_task_status(task_id)
        return status
    
    except Exception as e:
        logger.error(f"Error getting task status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/agents/status")
async def get_agents_status():
    """Get status of all agents"""
    try:
        orchestrator = app.state.orchestrator
        status = await orchestrator.get_agents_status()
        return status
    
    except Exception as e:
        logger.error(f"Error getting agents status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )