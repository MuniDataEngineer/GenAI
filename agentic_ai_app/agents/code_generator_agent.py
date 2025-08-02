"""
Code Generator Agent - Generates code based on user stories and requirements
"""

import asyncio
import logging
import json
import os
import shutil
import tempfile
from typing import Dict, Any, List, Optional
from datetime import datetime
import subprocess

from openai import AsyncOpenAI
import git

from core.config import settings

logger = logging.getLogger(__name__)

class CodeGeneratorAgent:
    """AI agent for generating code based on user stories"""
    
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.active_projects = {}
        self._initialized = False
    
    async def initialize(self):
        """Initialize the code generator agent"""
        if self._initialized:
            return
        
        logger.info("Initializing Code Generator Agent...")
        
        try:
            # Create directories
            os.makedirs(settings.CODE_OUTPUT_PATH, exist_ok=True)
            
            self._initialized = True
            logger.info("Code Generator Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Code Generator Agent: {str(e)}")
            raise
    
    async def generate_code(self, user_story: str, project_type: str = "web", framework: str = "react") -> Dict[str, Any]:
        """
        Generate code based on user story
        
        Args:
            user_story: The user story description
            project_type: Type of project (web, api, mobile, etc.)
            framework: Framework to use (react, vue, flask, etc.)
            
        Returns:
            Dict containing generated code information
        """
        project_id = f"{project_type}_{framework}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            logger.info(f"Starting code generation: {project_id}")
            
            # Store project info
            self.active_projects[project_id] = {
                "user_story": user_story,
                "project_type": project_type,
                "framework": framework,
                "start_time": datetime.now(),
                "status": "analyzing"
            }
            
            # Analyze user story and create project plan
            project_plan = await self._analyze_user_story(user_story, project_type, framework)
            
            # Generate project structure
            project_path = await self._create_project_structure(project_id, project_plan)
            
            # Generate code files
            generated_files = await self._generate_code_files(project_path, project_plan)
            
            # Create Git repository
            repository_info = await self._create_git_repository(project_path, project_id)
            
            # Update project status
            self.active_projects[project_id].update({
                "status": "completed",
                "project_path": project_path,
                "project_plan": project_plan,
                "generated_files": generated_files,
                "repository_info": repository_info,
                "completion_time": datetime.now()
            })
            
            return {
                "project_id": project_id,
                "project_path": project_path,
                "project_plan": project_plan,
                "generated_files": generated_files,
                "repository_info": repository_info,
                "user_story": user_story,
                "project_type": project_type,
                "framework": framework
            }
            
        except Exception as e:
            logger.error(f"Error generating code for project {project_id}: {str(e)}")
            if project_id in self.active_projects:
                self.active_projects[project_id]["status"] = "failed"
                self.active_projects[project_id]["error"] = str(e)
            raise
    
    async def generate_from_story(self, story: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code from a Jira story"""
        user_story = f"As a {story.get('assignee', 'user')}, {story.get('summary', '')}\n\n{story.get('description', '')}"
        
        # Determine project type and framework based on story labels/components
        project_type = self._determine_project_type(story)
        framework = self._determine_framework(story, project_type)
        
        return await self.generate_code(user_story, project_type, framework)
    
    async def _analyze_user_story(self, user_story: str, project_type: str, framework: str) -> Dict[str, Any]:
        """Analyze user story and create a project plan"""
        prompt = f"""
        Analyze this user story and create a detailed project plan for a {project_type} application using {framework}:
        
        User Story: {user_story}
        
        Create a project plan including:
        1. Project structure (folders and files)
        2. Required components/modules
        3. API endpoints (if applicable)
        4. Database schema (if applicable)
        5. Dependencies
        6. Key features to implement
        7. Testing strategy
        
        Respond in JSON format:
        {{
            "project_name": "...",
            "description": "...",
            "structure": {{
                "folders": [...],
                "main_files": [...]
            }},
            "components": [...],
            "api_endpoints": [...],
            "database_schema": {{...}},
            "dependencies": [...],
            "features": [...],
            "testing": {{
                "unit_tests": [...],
                "integration_tests": [...]
            }}
        }}
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            plan = json.loads(response.choices[0].message.content)
            return plan
            
        except Exception as e:
            logger.error(f"Error analyzing user story: {str(e)}")
            # Fallback to basic plan
            return self._create_fallback_plan(user_story, project_type, framework)
    
    async def _create_project_structure(self, project_id: str, project_plan: Dict[str, Any]) -> str:
        """Create the project directory structure"""
        project_path = os.path.join(settings.CODE_OUTPUT_PATH, project_id)
        
        try:
            # Create main project directory
            os.makedirs(project_path, exist_ok=True)
            
            # Create folder structure
            for folder in project_plan.get("structure", {}).get("folders", []):
                folder_path = os.path.join(project_path, folder)
                os.makedirs(folder_path, exist_ok=True)
            
            logger.info(f"Created project structure at: {project_path}")
            return project_path
            
        except Exception as e:
            logger.error(f"Error creating project structure: {str(e)}")
            raise
    
    async def _generate_code_files(self, project_path: str, project_plan: Dict[str, Any]) -> List[str]:
        """Generate code files based on the project plan"""
        generated_files = []
        
        try:
            # Generate package.json for web projects
            if "package.json" in project_plan.get("structure", {}).get("main_files", []):
                package_json = await self._generate_package_json(project_plan)
                package_path = os.path.join(project_path, "package.json")
                with open(package_path, 'w') as f:
                    json.dump(package_json, f, indent=2)
                generated_files.append("package.json")
            
            # Generate README
            readme_content = await self._generate_readme(project_plan)
            readme_path = os.path.join(project_path, "README.md")
            with open(readme_path, 'w') as f:
                f.write(readme_content)
            generated_files.append("README.md")
            
            # Generate main application file
            main_file = await self._generate_main_file(project_plan)
            main_file_name = self._get_main_file_name(project_plan)
            main_file_path = os.path.join(project_path, main_file_name)
            with open(main_file_path, 'w') as f:
                f.write(main_file)
            generated_files.append(main_file_name)
            
            # Generate components
            for component in project_plan.get("components", []):
                component_content = await self._generate_component(component, project_plan)
                component_file_name = self._get_component_file_name(component, project_plan)
                component_path = os.path.join(project_path, "src", "components", component_file_name)
                os.makedirs(os.path.dirname(component_path), exist_ok=True)
                with open(component_path, 'w') as f:
                    f.write(component_content)
                generated_files.append(f"src/components/{component_file_name}")
            
            # Generate API routes (if applicable)
            for endpoint in project_plan.get("api_endpoints", []):
                route_content = await self._generate_api_route(endpoint, project_plan)
                route_file_name = self._get_route_file_name(endpoint)
                route_path = os.path.join(project_path, "src", "routes", route_file_name)
                os.makedirs(os.path.dirname(route_path), exist_ok=True)
                with open(route_path, 'w') as f:
                    f.write(route_content)
                generated_files.append(f"src/routes/{route_file_name}")
            
            # Generate tests
            for test in project_plan.get("testing", {}).get("unit_tests", []):
                test_content = await self._generate_test_file(test, project_plan)
                test_file_name = self._get_test_file_name(test)
                test_path = os.path.join(project_path, "tests", test_file_name)
                os.makedirs(os.path.dirname(test_path), exist_ok=True)
                with open(test_path, 'w') as f:
                    f.write(test_content)
                generated_files.append(f"tests/{test_file_name}")
            
            logger.info(f"Generated {len(generated_files)} files")
            return generated_files
            
        except Exception as e:
            logger.error(f"Error generating code files: {str(e)}")
            raise
    
    async def _create_git_repository(self, project_path: str, project_id: str) -> Dict[str, Any]:
        """Create a Git repository for the generated code"""
        try:
            # Initialize Git repository
            repo = git.Repo.init(project_path)
            
            # Create .gitignore
            gitignore_content = self._generate_gitignore()
            gitignore_path = os.path.join(project_path, ".gitignore")
            with open(gitignore_path, 'w') as f:
                f.write(gitignore_content)
            
            # Add all files
            repo.git.add(A=True)
            
            # Initial commit
            repo.index.commit("Initial commit - Generated by AI Agent")
            
            repository_info = {
                "local_path": project_path,
                "initialized": True,
                "initial_commit": True,
                "branch": "main"
            }
            
            # Push to remote if GitHub token is available
            if settings.GITHUB_TOKEN:
                repository_info.update(await self._push_to_github(repo, project_id))
            
            return repository_info
            
        except Exception as e:
            logger.error(f"Error creating Git repository: {str(e)}")
            return {"local_path": project_path, "error": str(e)}
    
    async def _push_to_github(self, repo: git.Repo, project_id: str) -> Dict[str, Any]:
        """Push repository to GitHub"""
        try:
            # This would create a GitHub repository and push to it
            # For demo purposes, we'll simulate this
            remote_url = f"https://github.com/ai-agent/{project_id}.git"
            
            # In a real implementation, you would:
            # 1. Create repository via GitHub API
            # 2. Add remote origin
            # 3. Push to remote
            
            return {
                "remote_url": remote_url,
                "pushed_to_remote": True,
                "repository_created": True
            }
            
        except Exception as e:
            logger.error(f"Error pushing to GitHub: {str(e)}")
            return {"error": str(e)}
    
    async def _generate_package_json(self, project_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate package.json file"""
        return {
            "name": project_plan.get("project_name", "ai-generated-app").lower().replace(" ", "-"),
            "version": "1.0.0",
            "description": project_plan.get("description", "AI-generated application"),
            "main": "src/index.js",
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test",
                "eject": "react-scripts eject"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-scripts": "5.0.1"
            },
            "browserslist": {
                "production": [
                    ">0.2%",
                    "not dead",
                    "not op_mini all"
                ],
                "development": [
                    "last 1 chrome version",
                    "last 1 firefox version",
                    "last 1 safari version"
                ]
            }
        }
    
    async def _generate_readme(self, project_plan: Dict[str, Any]) -> str:
        """Generate README.md file"""
        return f"""# {project_plan.get('project_name', 'AI Generated Application')}

{project_plan.get('description', 'This application was generated by an AI agent based on user story requirements.')}

## Features

{chr(10).join(f"- {feature}" for feature in project_plan.get('features', []))}

## Installation

```bash
npm install
```

## Usage

```bash
npm start
```

## Testing

```bash
npm test
```

## Generated by AI Agent

This project was automatically generated based on the following user story:
- Project Type: {project_plan.get('project_type', 'Unknown')}
- Framework: {project_plan.get('framework', 'Unknown')}
- Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    async def _generate_main_file(self, project_plan: Dict[str, Any]) -> str:
        """Generate main application file"""
        # This would generate different content based on framework
        # For React example:
        return """import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
"""
    
    async def _generate_component(self, component: str, project_plan: Dict[str, Any]) -> str:
        """Generate a React component"""
        component_name = component.replace(" ", "")
        return f"""import React from 'react';

const {component_name} = () => {{
  return (
    <div className="{component_name.lower()}">
      <h2>{component}</h2>
      <p>This is the {component} component.</p>
    </div>
  );
}};

export default {component_name};
"""
    
    async def _generate_api_route(self, endpoint: Dict[str, Any], project_plan: Dict[str, Any]) -> str:
        """Generate API route file"""
        return f"""// API Route: {endpoint.get('path', '/api')}
// Method: {endpoint.get('method', 'GET')}

const handler = async (req, res) => {{
  try {{
    // Implementation for {endpoint.get('path', '/api')}
    res.status(200).json({{ message: 'Success' }});
  }} catch (error) {{
    res.status(500).json({{ error: error.message }});
  }}
}};

export default handler;
"""
    
    async def _generate_test_file(self, test: str, project_plan: Dict[str, Any]) -> str:
        """Generate test file"""
        return f"""import {{ render, screen }} from '@testing-library/react';
import App from '../App';

test('{test}', () => {{
  render(<App />);
  // Add your test implementation here
  expect(screen.getByText(/learn react/i)).toBeInTheDocument();
}});
"""
    
    def _get_main_file_name(self, project_plan: Dict[str, Any]) -> str:
        """Get main file name based on project type"""
        return "src/index.js"
    
    def _get_component_file_name(self, component: str, project_plan: Dict[str, Any]) -> str:
        """Get component file name"""
        return f"{component.replace(' ', '')}.js"
    
    def _get_route_file_name(self, endpoint: Dict[str, Any]) -> str:
        """Get route file name"""
        path = endpoint.get('path', '/api').replace('/', '_')
        return f"{path}.js"
    
    def _get_test_file_name(self, test: str) -> str:
        """Get test file name"""
        return f"{test.replace(' ', '_').lower()}.test.js"
    
    def _generate_gitignore(self) -> str:
        """Generate .gitignore file"""
        return """# Dependencies
node_modules/
/.pnp
.pnp.js

# Testing
/coverage

# Production
/build

# Misc
.DS_Store
.env.local
.env.development.local
.env.test.local
.env.production.local

# Logs
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# IDE
.vscode/
.idea/
"""
    
    def _determine_project_type(self, story: Dict[str, Any]) -> str:
        """Determine project type from story"""
        labels = story.get('labels', [])
        description = story.get('description', '').lower()
        
        if any(label in ['web', 'frontend', 'ui'] for label in labels):
            return "web"
        elif any(label in ['api', 'backend', 'service'] for label in labels):
            return "api"
        elif any(label in ['mobile', 'ios', 'android'] for label in labels):
            return "mobile"
        elif 'dashboard' in description or 'ui' in description:
            return "web"
        else:
            return "web"  # Default
    
    def _determine_framework(self, story: Dict[str, Any], project_type: str) -> str:
        """Determine framework from story"""
        labels = story.get('labels', [])
        description = story.get('description', '').lower()
        
        if project_type == "web":
            if any(label in ['react', 'reactjs'] for label in labels):
                return "react"
            elif any(label in ['vue', 'vuejs'] for label in labels):
                return "vue"
            elif any(label in ['angular'] for label in labels):
                return "angular"
            else:
                return "react"  # Default
        elif project_type == "api":
            if any(label in ['flask', 'python'] for label in labels):
                return "flask"
            elif any(label in ['express', 'nodejs'] for label in labels):
                return "express"
            elif any(label in ['fastapi'] for label in labels):
                return "fastapi"
            else:
                return "express"  # Default
        
        return "react"  # Fallback
    
    def _create_fallback_plan(self, user_story: str, project_type: str, framework: str) -> Dict[str, Any]:
        """Create a fallback project plan"""
        return {
            "project_name": f"AI Generated {project_type.title()} App",
            "description": f"Application generated from user story using {framework}",
            "structure": {
                "folders": ["src", "src/components", "src/routes", "tests", "public"],
                "main_files": ["package.json", "README.md", "src/index.js"]
            },
            "components": ["Header", "Main", "Footer"],
            "api_endpoints": [],
            "database_schema": {},
            "dependencies": ["react", "react-dom"],
            "features": ["Basic UI", "Responsive Design"],
            "testing": {
                "unit_tests": ["renders without crashing"],
                "integration_tests": []
            }
        }
    
    async def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """Get status of a code generation project"""
        if project_id not in self.active_projects:
            return {"error": "Project not found"}
        
        return self.active_projects[project_id]
    
    async def list_active_projects(self) -> List[Dict[str, Any]]:
        """List all active code generation projects"""
        return [
            {
                "project_id": project_id,
                "status": project_info["status"],
                "project_type": project_info.get("project_type"),
                "framework": project_info.get("framework"),
                "start_time": project_info["start_time"].isoformat()
            }
            for project_id, project_info in self.active_projects.items()
        ]
    
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "status": "active" if self._initialized else "inactive",
            "active_projects": len([
                p for p in self.active_projects.values() 
                if p["status"] in ["analyzing", "generating"]
            ]),
            "total_projects": len(self.active_projects),
            "capabilities": {
                "web_development": True,
                "api_development": True,
                "mobile_development": True,
                "testing": True,
                "git_integration": True,
                "github_integration": bool(settings.GITHUB_TOKEN)
            }
        }
    
    async def cleanup(self):
        """Cleanup agent resources"""
        logger.info("Cleaning up Code Generator Agent...")
        # No specific cleanup needed
        logger.info("Code Generator Agent cleanup completed")