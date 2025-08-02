"""
Main orchestrator that coordinates all AI agents
"""

import asyncio
import uuid
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum

from agents.meeting_agent import MeetingAgent
from agents.jira_agent import JiraAgent
from agents.code_generator_agent import CodeGeneratorAgent
from agents.deployment_agent import DeploymentAgent
from core.config import settings
from utils.task_manager import TaskManager, TaskStatus

logger = logging.getLogger(__name__)

class AgentType(Enum):
    MEETING = "meeting"
    JIRA = "jira"
    CODE_GENERATOR = "code_generator"
    DEPLOYMENT = "deployment"

class TaskType(Enum):
    ATTEND_MEETING = "attend_meeting"
    UPDATE_JIRA = "update_jira"
    GENERATE_CODE = "generate_code"
    DEPLOY_APP = "deploy_app"
    FULL_WORKFLOW = "full_workflow"

class AgentOrchestrator:
    """Main orchestrator for coordinating AI agents"""
    
    def __init__(self):
        self.agents: Dict[AgentType, Any] = {}
        self.task_manager = TaskManager()
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        self._initialized = False
    
    async def initialize(self):
        """Initialize all agents"""
        if self._initialized:
            return
        
        logger.info("Initializing Agentic AI Orchestrator...")
        
        try:
            # Initialize task manager
            await self.task_manager.initialize()
            
            # Initialize agents
            self.agents[AgentType.MEETING] = MeetingAgent()
            self.agents[AgentType.JIRA] = JiraAgent()
            self.agents[AgentType.CODE_GENERATOR] = CodeGeneratorAgent()
            self.agents[AgentType.DEPLOYMENT] = DeploymentAgent()
            
            # Initialize each agent
            for agent_type, agent in self.agents.items():
                await agent.initialize()
                logger.info(f"Initialized {agent_type.value} agent")
            
            self._initialized = True
            logger.info("All agents initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize orchestrator: {str(e)}")
            raise
    
    async def cleanup(self):
        """Cleanup all agents and resources"""
        logger.info("Cleaning up orchestrator...")
        
        # Cancel all active tasks
        for task_id in list(self.active_tasks.keys()):
            await self.cancel_task(task_id)
        
        # Cleanup agents
        for agent in self.agents.values():
            if hasattr(agent, 'cleanup'):
                await agent.cleanup()
        
        # Cleanup task manager
        await self.task_manager.cleanup()
        
        logger.info("Orchestrator cleanup completed")
    
    async def execute_task(self, task_type: str, description: str, parameters: Dict[str, Any]) -> str:
        """Execute a general task using the appropriate agent"""
        task_id = str(uuid.uuid4())
        
        try:
            # Register task
            await self.task_manager.create_task(
                task_id=task_id,
                task_type=task_type,
                description=description,
                parameters=parameters
            )
            
            # Start task execution in background
            asyncio.create_task(self._execute_task_async(task_id, task_type, description, parameters))
            
            return task_id
            
        except Exception as e:
            logger.error(f"Failed to start task {task_id}: {str(e)}")
            await self.task_manager.update_task_status(task_id, TaskStatus.FAILED, error=str(e))
            raise
    
    async def _execute_task_async(self, task_id: str, task_type: str, description: str, parameters: Dict[str, Any]):
        """Execute task asynchronously"""
        try:
            await self.task_manager.update_task_status(task_id, TaskStatus.RUNNING)
            
            if task_type == TaskType.FULL_WORKFLOW.value:
                result = await self._execute_full_workflow(task_id, description, parameters)
            elif task_type == TaskType.ATTEND_MEETING.value:
                result = await self._attend_meeting_task(task_id, parameters)
            elif task_type == TaskType.UPDATE_JIRA.value:
                result = await self._jira_task(task_id, parameters)
            elif task_type == TaskType.GENERATE_CODE.value:
                result = await self._code_generation_task(task_id, parameters)
            elif task_type == TaskType.DEPLOY_APP.value:
                result = await self._deployment_task(task_id, parameters)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            await self.task_manager.complete_task(task_id, result)
            
        except Exception as e:
            logger.error(f"Task {task_id} failed: {str(e)}")
            await self.task_manager.update_task_status(task_id, TaskStatus.FAILED, error=str(e))
    
    async def attend_meeting(self, meeting_url: str, meeting_type: str, duration: int = 60) -> str:
        """Join a meeting and extract updates"""
        parameters = {
            "meeting_url": meeting_url,
            "meeting_type": meeting_type,
            "duration": duration
        }
        
        return await self.execute_task(
            task_type=TaskType.ATTEND_MEETING.value,
            description=f"Attend {meeting_type} meeting for {duration} minutes",
            parameters=parameters
        )
    
    async def handle_jira_action(self, action: str, story_id: Optional[str] = None, story_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle Jira operations synchronously"""
        jira_agent = self.agents[AgentType.JIRA]
        
        if action == "get_story":
            return await jira_agent.get_story(story_id)
        elif action == "update_story":
            return await jira_agent.update_story(story_id, story_data)
        elif action == "create_story":
            return await jira_agent.create_story(story_data)
        elif action == "search_stories":
            return await jira_agent.search_stories(story_data.get("jql", ""))
        else:
            raise ValueError(f"Unknown Jira action: {action}")
    
    async def generate_code(self, user_story: str, project_type: str = "web", framework: str = "react") -> str:
        """Generate code based on user story"""
        parameters = {
            "user_story": user_story,
            "project_type": project_type,
            "framework": framework
        }
        
        return await self.execute_task(
            task_type=TaskType.GENERATE_CODE.value,
            description=f"Generate {project_type} code using {framework}",
            parameters=parameters
        )
    
    async def deploy_application(self, repository_url: str, branch: str = "main", environment: str = "dev") -> str:
        """Deploy application to specified environment"""
        parameters = {
            "repository_url": repository_url,
            "branch": branch,
            "environment": environment
        }
        
        return await self.execute_task(
            task_type=TaskType.DEPLOY_APP.value,
            description=f"Deploy {repository_url} to {environment}",
            parameters=parameters
        )
    
    async def execute_full_workflow(self, meeting_url: str, meeting_type: str, duration: int = 60) -> str:
        """Execute full workflow: attend meeting, update Jira, generate code if needed, deploy"""
        parameters = {
            "meeting_url": meeting_url,
            "meeting_type": meeting_type,
            "duration": duration,
            "workflow_type": "full"
        }
        
        return await self.execute_task(
            task_type=TaskType.FULL_WORKFLOW.value,
            description="Complete workflow from meeting to deployment",
            parameters=parameters
        )
    
    async def _execute_full_workflow(self, task_id: str, description: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the complete workflow"""
        results = {"steps": []}
        
        try:
            # Step 1: Attend meeting
            meeting_agent = self.agents[AgentType.MEETING]
            meeting_result = await meeting_agent.attend_meeting(
                meeting_url=parameters["meeting_url"],
                meeting_type=parameters["meeting_type"],
                duration=parameters["duration"]
            )
            results["steps"].append({"step": "meeting", "result": meeting_result})
            
            # Step 2: Extract action items and update Jira
            if meeting_result.get("action_items"):
                jira_agent = self.agents[AgentType.JIRA]
                for action_item in meeting_result["action_items"]:
                    jira_result = await jira_agent.process_action_item(action_item)
                    results["steps"].append({"step": "jira_update", "result": jira_result})
            
            # Step 3: Generate code for new stories
            if meeting_result.get("new_stories"):
                code_agent = self.agents[AgentType.CODE_GENERATOR]
                for story in meeting_result["new_stories"]:
                    code_result = await code_agent.generate_from_story(story)
                    results["steps"].append({"step": "code_generation", "result": code_result})
                    
                    # Step 4: Deploy if code was generated
                    if code_result.get("repository_url"):
                        deployment_agent = self.agents[AgentType.DEPLOYMENT]
                        deploy_result = await deployment_agent.deploy(
                            repository_url=code_result["repository_url"],
                            environment="dev"
                        )
                        results["steps"].append({"step": "deployment", "result": deploy_result})
            
            results["status"] = "completed"
            return results
            
        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            raise
    
    async def _attend_meeting_task(self, task_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute meeting attendance task"""
        meeting_agent = self.agents[AgentType.MEETING]
        return await meeting_agent.attend_meeting(
            meeting_url=parameters["meeting_url"],
            meeting_type=parameters["meeting_type"],
            duration=parameters["duration"]
        )
    
    async def _jira_task(self, task_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Jira task"""
        jira_agent = self.agents[AgentType.JIRA]
        action = parameters.get("action")
        
        if action == "update_story":
            return await jira_agent.update_story(
                story_id=parameters["story_id"],
                story_data=parameters["story_data"]
            )
        elif action == "create_story":
            return await jira_agent.create_story(parameters["story_data"])
        else:
            raise ValueError(f"Unknown Jira action: {action}")
    
    async def _code_generation_task(self, task_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code generation task"""
        code_agent = self.agents[AgentType.CODE_GENERATOR]
        return await code_agent.generate_code(
            user_story=parameters["user_story"],
            project_type=parameters.get("project_type", "web"),
            framework=parameters.get("framework", "react")
        )
    
    async def _deployment_task(self, task_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute deployment task"""
        deployment_agent = self.agents[AgentType.DEPLOYMENT]
        return await deployment_agent.deploy(
            repository_url=parameters["repository_url"],
            branch=parameters.get("branch", "main"),
            environment=parameters.get("environment", "dev")
        )
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status"""
        return await self.task_manager.get_task_status(task_id)
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        return await self.task_manager.cancel_task(task_id)
    
    async def get_agents_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        status = {}
        for agent_type, agent in self.agents.items():
            if hasattr(agent, 'get_status'):
                status[agent_type.value] = await agent.get_status()
            else:
                status[agent_type.value] = {"status": "active"}
        
        return {
            "agents": status,
            "active_tasks": len(self.active_tasks),
            "initialized": self._initialized
        }