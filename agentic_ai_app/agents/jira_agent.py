"""
Jira Agent - Handles Jira integration for story management and project tracking
"""

import asyncio
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from jira import JIRA
from openai import AsyncOpenAI

from core.config import settings

logger = logging.getLogger(__name__)

class JiraAgent:
    """AI agent for Jira integration and story management"""
    
    def __init__(self):
        self.jira_client = None
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self._initialized = False
    
    async def initialize(self):
        """Initialize the Jira agent"""
        if self._initialized:
            return
        
        logger.info("Initializing Jira Agent...")
        
        try:
            if all([settings.JIRA_SERVER, settings.JIRA_USERNAME, settings.JIRA_API_TOKEN]):
                # Initialize Jira client
                self.jira_client = JIRA(
                    server=settings.JIRA_SERVER,
                    basic_auth=(settings.JIRA_USERNAME, settings.JIRA_API_TOKEN)
                )
                
                # Test connection
                user = self.jira_client.current_user()
                logger.info(f"Connected to Jira as: {user}")
                
            else:
                logger.warning("Jira credentials not configured, running in simulation mode")
            
            self._initialized = True
            logger.info("Jira Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Jira Agent: {str(e)}")
            # Continue in simulation mode
            self._initialized = True
    
    async def get_story(self, story_id: str) -> Dict[str, Any]:
        """Get a Jira story by ID"""
        try:
            if self.jira_client:
                issue = self.jira_client.issue(story_id)
                return self._format_issue(issue)
            else:
                # Simulation mode
                return self._simulate_story(story_id)
                
        except Exception as e:
            logger.error(f"Error getting story {story_id}: {str(e)}")
            raise
    
    async def create_story(self, story_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Jira story"""
        try:
            if self.jira_client:
                issue_dict = {
                    'project': {'key': story_data.get('project', settings.JIRA_PROJECT_KEY)},
                    'summary': story_data['summary'],
                    'description': story_data.get('description', ''),
                    'issuetype': {'name': story_data.get('issue_type', 'Story')},
                }
                
                # Add optional fields
                if 'assignee' in story_data:
                    issue_dict['assignee'] = {'name': story_data['assignee']}
                
                if 'priority' in story_data:
                    issue_dict['priority'] = {'name': story_data['priority']}
                
                if 'labels' in story_data:
                    issue_dict['labels'] = story_data['labels']
                
                new_issue = self.jira_client.create_issue(fields=issue_dict)
                
                logger.info(f"Created Jira story: {new_issue.key}")
                return self._format_issue(new_issue)
                
            else:
                # Simulation mode
                return self._simulate_create_story(story_data)
                
        except Exception as e:
            logger.error(f"Error creating story: {str(e)}")
            raise
    
    async def update_story(self, story_id: str, story_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing Jira story"""
        try:
            if self.jira_client:
                issue = self.jira_client.issue(story_id)
                
                # Update fields
                update_fields = {}
                
                if 'summary' in story_data:
                    update_fields['summary'] = story_data['summary']
                
                if 'description' in story_data:
                    update_fields['description'] = story_data['description']
                
                if 'assignee' in story_data:
                    update_fields['assignee'] = {'name': story_data['assignee']}
                
                if 'priority' in story_data:
                    update_fields['priority'] = {'name': story_data['priority']}
                
                if 'labels' in story_data:
                    update_fields['labels'] = story_data['labels']
                
                if update_fields:
                    issue.update(fields=update_fields)
                
                # Handle status transitions
                if 'status' in story_data:
                    await self._transition_issue(issue, story_data['status'])
                
                # Add comment if provided
                if 'comment' in story_data:
                    self.jira_client.add_comment(issue, story_data['comment'])
                
                logger.info(f"Updated Jira story: {story_id}")
                return self._format_issue(issue)
                
            else:
                # Simulation mode
                return self._simulate_update_story(story_id, story_data)
                
        except Exception as e:
            logger.error(f"Error updating story {story_id}: {str(e)}")
            raise
    
    async def search_stories(self, jql: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Search for stories using JQL"""
        try:
            if self.jira_client:
                issues = self.jira_client.search_issues(jql, maxResults=max_results)
                return [self._format_issue(issue) for issue in issues]
            else:
                # Simulation mode
                return self._simulate_search_stories(jql)
                
        except Exception as e:
            logger.error(f"Error searching stories with JQL '{jql}': {str(e)}")
            raise
    
    async def get_project_info(self, project_key: str = None) -> Dict[str, Any]:
        """Get project information"""
        project_key = project_key or settings.JIRA_PROJECT_KEY
        
        try:
            if self.jira_client:
                project = self.jira_client.project(project_key)
                return {
                    "key": project.key,
                    "name": project.name,
                    "description": getattr(project, 'description', ''),
                    "lead": getattr(project.lead, 'displayName', 'Unknown'),
                    "project_type": getattr(project, 'projectTypeKey', 'unknown')
                }
            else:
                # Simulation mode
                return {
                    "key": project_key,
                    "name": f"Demo Project {project_key}",
                    "description": "Demo project for testing",
                    "lead": "Demo User",
                    "project_type": "software"
                }
                
        except Exception as e:
            logger.error(f"Error getting project info for {project_key}: {str(e)}")
            raise
    
    async def process_action_item(self, action_item: Dict[str, Any]) -> Dict[str, Any]:
        """Process an action item from a meeting"""
        try:
            # Use AI to analyze and categorize the action item
            analysis = await self._analyze_action_item(action_item)
            
            result = {"action_item": action_item, "analysis": analysis}
            
            # Determine action based on analysis
            if analysis.get("action") == "create_story":
                story_data = {
                    "summary": analysis["story_summary"],
                    "description": analysis["story_description"],
                    "priority": analysis.get("priority", "Medium"),
                    "assignee": analysis.get("assignee"),
                    "labels": analysis.get("labels", [])
                }
                
                created_story = await self.create_story(story_data)
                result["created_story"] = created_story
                
            elif analysis.get("action") == "update_story":
                story_id = analysis["story_id"]
                update_data = analysis["update_data"]
                
                updated_story = await self.update_story(story_id, update_data)
                result["updated_story"] = updated_story
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing action item: {str(e)}")
            raise
    
    async def _analyze_action_item(self, action_item: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to analyze an action item and determine appropriate action"""
        prompt = f"""
        Analyze this action item from a meeting and determine what Jira action should be taken:
        
        Action Item: {action_item.get('description', '')}
        Assignee: {action_item.get('assignee', 'Unknown')}
        Context: {action_item.get('context', '')}
        
        Determine:
        1. Should this create a new story, update an existing story, or no action?
        2. If creating a story, what should be the summary and description?
        3. What priority should it have (High, Medium, Low)?
        4. Are there any relevant labels or components?
        5. If updating a story, what is the story ID and what fields should be updated?
        
        Respond in JSON format:
        {{
            "action": "create_story|update_story|no_action",
            "story_summary": "...",
            "story_description": "...",
            "priority": "High|Medium|Low",
            "assignee": "...",
            "labels": [...],
            "story_id": "...",  // if updating
            "update_data": {{...}}  // if updating
        }}
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            analysis = json.loads(response.choices[0].message.content)
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing action item with AI: {str(e)}")
            # Fallback to basic analysis
            return {
                "action": "create_story",
                "story_summary": action_item.get('description', 'Action item from meeting'),
                "story_description": f"Action item: {action_item.get('description', '')}\nAssignee: {action_item.get('assignee', '')}",
                "priority": "Medium",
                "assignee": action_item.get('assignee'),
                "labels": ["meeting-action-item"]
            }
    
    async def _transition_issue(self, issue, target_status: str):
        """Transition an issue to a target status"""
        try:
            transitions = self.jira_client.transitions(issue)
            
            for transition in transitions:
                if transition['to']['name'].lower() == target_status.lower():
                    self.jira_client.transition_issue(issue, transition['id'])
                    logger.info(f"Transitioned {issue.key} to {target_status}")
                    return
            
            logger.warning(f"No transition found to status '{target_status}' for {issue.key}")
            
        except Exception as e:
            logger.error(f"Error transitioning issue {issue.key}: {str(e)}")
    
    def _format_issue(self, issue) -> Dict[str, Any]:
        """Format a Jira issue for API response"""
        return {
            "id": issue.id,
            "key": issue.key,
            "summary": issue.fields.summary,
            "description": getattr(issue.fields, 'description', ''),
            "status": issue.fields.status.name,
            "priority": getattr(issue.fields.priority, 'name', 'None') if issue.fields.priority else 'None',
            "assignee": getattr(issue.fields.assignee, 'displayName', 'Unassigned') if issue.fields.assignee else 'Unassigned',
            "reporter": getattr(issue.fields.reporter, 'displayName', 'Unknown') if issue.fields.reporter else 'Unknown',
            "created": issue.fields.created,
            "updated": issue.fields.updated,
            "project": issue.fields.project.key,
            "issue_type": issue.fields.issuetype.name,
            "labels": getattr(issue.fields, 'labels', []),
            "url": f"{settings.JIRA_SERVER}/browse/{issue.key}"
        }
    
    def _simulate_story(self, story_id: str) -> Dict[str, Any]:
        """Simulate getting a story (for demo purposes)"""
        return {
            "id": "12345",
            "key": story_id,
            "summary": f"Demo story {story_id}",
            "description": "This is a simulated story for demo purposes",
            "status": "To Do",
            "priority": "Medium",
            "assignee": "Demo User",
            "reporter": "Demo Reporter",
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
            "project": "DEMO",
            "issue_type": "Story",
            "labels": ["demo"],
            "url": f"http://demo-jira.com/browse/{story_id}"
        }
    
    def _simulate_create_story(self, story_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate creating a story (for demo purposes)"""
        story_id = f"DEMO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return {
            "id": "12346",
            "key": story_id,
            "summary": story_data['summary'],
            "description": story_data.get('description', ''),
            "status": "To Do",
            "priority": story_data.get('priority', 'Medium'),
            "assignee": story_data.get('assignee', 'Unassigned'),
            "reporter": "AI Agent",
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
            "project": "DEMO",
            "issue_type": story_data.get('issue_type', 'Story'),
            "labels": story_data.get('labels', []),
            "url": f"http://demo-jira.com/browse/{story_id}"
        }
    
    def _simulate_update_story(self, story_id: str, story_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate updating a story (for demo purposes)"""
        base_story = self._simulate_story(story_id)
        
        # Update fields
        if 'summary' in story_data:
            base_story['summary'] = story_data['summary']
        if 'status' in story_data:
            base_story['status'] = story_data['status']
        if 'assignee' in story_data:
            base_story['assignee'] = story_data['assignee']
        
        base_story['updated'] = datetime.now().isoformat()
        return base_story
    
    def _simulate_search_stories(self, jql: str) -> List[Dict[str, Any]]:
        """Simulate searching stories (for demo purposes)"""
        return [
            self._simulate_story("DEMO-001"),
            self._simulate_story("DEMO-002"),
            self._simulate_story("DEMO-003")
        ]
    
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "status": "active" if self._initialized else "inactive",
            "jira_connected": self.jira_client is not None,
            "jira_server": settings.JIRA_SERVER,
            "simulation_mode": self.jira_client is None,
            "capabilities": {
                "create_stories": True,
                "update_stories": True,
                "search_stories": True,
                "process_action_items": True,
                "ai_analysis": True
            }
        }
    
    async def cleanup(self):
        """Cleanup agent resources"""
        logger.info("Cleaning up Jira Agent...")
        # No specific cleanup needed for Jira client
        logger.info("Jira Agent cleanup completed")