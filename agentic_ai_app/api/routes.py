"""
API Routes for Agentic AI Application
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import json

router = APIRouter()

# Additional API endpoints beyond the main ones in main.py

@router.get("/features", response_model=Dict[str, Any])
async def get_available_features():
    """Get list of available features based on configuration"""
    from core.config import get_available_features
    
    features = get_available_features()
    return {
        "features": features,
        "total_features": len([f for f in features.values() if f]),
        "configured_features": [k for k, v in features.items() if v]
    }

@router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the web dashboard"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Agentic AI Assistant Dashboard</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            
            .header {
                text-align: center;
                margin-bottom: 40px;
                color: white;
            }
            
            .header h1 {
                font-size: 3rem;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            
            .header p {
                font-size: 1.2rem;
                opacity: 0.9;
            }
            
            .cards {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 25px;
                margin-bottom: 40px;
            }
            
            .card {
                background: white;
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            
            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 40px rgba(0,0,0,0.15);
            }
            
            .card h3 {
                color: #667eea;
                margin-bottom: 15px;
                font-size: 1.4rem;
            }
            
            .card p {
                margin-bottom: 20px;
                line-height: 1.6;
                color: #666;
            }
            
            .btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 25px;
                cursor: pointer;
                font-size: 1rem;
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
            }
            
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            
            .workflow-section {
                background: white;
                border-radius: 15px;
                padding: 30px;
                margin-top: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            }
            
            .workflow-section h2 {
                color: #667eea;
                margin-bottom: 20px;
                text-align: center;
            }
            
            .workflow-steps {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }
            
            .step {
                text-align: center;
                padding: 20px;
                background: #f8f9ff;
                border-radius: 10px;
                border-left: 4px solid #667eea;
            }
            
            .step-number {
                background: #667eea;
                color: white;
                width: 30px;
                height: 30px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 10px;
                font-weight: bold;
            }
            
            .form-group {
                margin-bottom: 20px;
            }
            
            .form-group label {
                display: block;
                margin-bottom: 5px;
                font-weight: 600;
                color: #333;
            }
            
            .form-group input,
            .form-group select,
            .form-group textarea {
                width: 100%;
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 8px;
                font-size: 1rem;
            }
            
            .form-group textarea {
                height: 100px;
                resize: vertical;
            }
            
            .status-indicator {
                display: inline-block;
                width: 10px;
                height: 10px;
                border-radius: 50%;
                margin-right: 8px;
            }
            
            .status-active { background-color: #10b981; }
            .status-inactive { background-color: #ef4444; }
            .status-pending { background-color: #f59e0b; }
            
            .modal {
                display: none;
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.5);
            }
            
            .modal-content {
                background-color: white;
                margin: 5% auto;
                padding: 30px;
                border-radius: 15px;
                width: 90%;
                max-width: 600px;
                max-height: 80vh;
                overflow-y: auto;
            }
            
            .close {
                color: #aaa;
                float: right;
                font-size: 28px;
                font-weight: bold;
                cursor: pointer;
            }
            
            .close:hover {
                color: #000;
            }
            
            .task-status {
                padding: 20px;
                margin-top: 20px;
                background: #f8f9ff;
                border-radius: 10px;
                display: none;
            }
            
            .loading {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid #f3f3f3;
                border-top: 3px solid #667eea;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Agentic AI Assistant</h1>
                <p>Your AI-powered meeting assistant, Jira manager, code generator, and deployment automation tool</p>
            </div>
            
            <div class="cards">
                <div class="card">
                    <h3>🎯 Meeting Assistant</h3>
                    <p>Join Zoom or Teams meetings, extract action items, and automatically update Jira stories based on discussions.</p>
                    <button class="btn" onclick="openModal('meetingModal')">Attend Meeting</button>
                </div>
                
                <div class="card">
                    <h3>📋 Jira Manager</h3>
                    <p>Get story information, update tickets, create new stories, and manage your project workflow seamlessly.</p>
                    <button class="btn" onclick="openModal('jiraModal')">Manage Jira</button>
                </div>
                
                <div class="card">
                    <h3>💻 Code Generator</h3>
                    <p>Generate complete applications from user stories with modern frameworks and best practices.</p>
                    <button class="btn" onclick="openModal('codeModal')">Generate Code</button>
                </div>
                
                <div class="card">
                    <h3>🚀 Deployment</h3>
                    <p>Deploy applications to development, staging, or production environments with Docker and Kubernetes.</p>
                    <button class="btn" onclick="openModal('deployModal')">Deploy App</button>
                </div>
            </div>
            
            <div class="workflow-section">
                <h2>Complete Workflow</h2>
                <p style="text-align: center; margin-bottom: 20px;">Execute the full AI-powered development workflow from meeting to deployment</p>
                
                <div class="workflow-steps">
                    <div class="step">
                        <div class="step-number">1</div>
                        <h4>Attend Meeting</h4>
                        <p>AI joins your meeting and captures discussion</p>
                    </div>
                    <div class="step">
                        <div class="step-number">2</div>
                        <h4>Update Jira</h4>
                        <p>Automatically updates stories and creates new ones</p>
                    </div>
                    <div class="step">
                        <div class="step-number">3</div>
                        <h4>Generate Code</h4>
                        <p>Creates applications based on requirements</p>
                    </div>
                    <div class="step">
                        <div class="step-number">4</div>
                        <h4>Deploy</h4>
                        <p>Deploys to development environment</p>
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <button class="btn" onclick="openModal('workflowModal')">Start Full Workflow</button>
                </div>
            </div>
        </div>
        
        <!-- Meeting Modal -->
        <div id="meetingModal" class="modal">
            <div class="modal-content">
                <span class="close" onclick="closeModal('meetingModal')">&times;</span>
                <h2>Attend Meeting</h2>
                <form id="meetingForm">
                    <div class="form-group">
                        <label for="meetingUrl">Meeting URL:</label>
                        <input type="url" id="meetingUrl" name="meetingUrl" placeholder="https://zoom.us/j/1234567890" required>
                    </div>
                    <div class="form-group">
                        <label for="meetingType">Meeting Type:</label>
                        <select id="meetingType" name="meetingType" required>
                            <option value="zoom">Zoom</option>
                            <option value="teams">Microsoft Teams</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="meetingDuration">Duration (minutes):</label>
                        <input type="number" id="meetingDuration" name="meetingDuration" value="60" min="1" max="480">
                    </div>
                    <button type="submit" class="btn">Join Meeting</button>
                </form>
                <div id="meetingStatus" class="task-status"></div>
            </div>
        </div>
        
        <!-- Jira Modal -->
        <div id="jiraModal" class="modal">
            <div class="modal-content">
                <span class="close" onclick="closeModal('jiraModal')">&times;</span>
                <h2>Jira Management</h2>
                <form id="jiraForm">
                    <div class="form-group">
                        <label for="jiraAction">Action:</label>
                        <select id="jiraAction" name="jiraAction" required>
                            <option value="get_story">Get Story</option>
                            <option value="update_story">Update Story</option>
                            <option value="create_story">Create Story</option>
                            <option value="search_stories">Search Stories</option>
                        </select>
                    </div>
                    <div class="form-group" id="storyIdGroup">
                        <label for="storyId">Story ID:</label>
                        <input type="text" id="storyId" name="storyId" placeholder="PROJ-123">
                    </div>
                    <div class="form-group" id="storyDataGroup" style="display: none;">
                        <label for="storyData">Story Data (JSON):</label>
                        <textarea id="storyData" name="storyData" placeholder='{"summary": "New feature", "description": "..."}'></textarea>
                    </div>
                    <button type="submit" class="btn">Execute</button>
                </form>
                <div id="jiraStatus" class="task-status"></div>
            </div>
        </div>
        
        <!-- Code Generation Modal -->
        <div id="codeModal" class="modal">
            <div class="modal-content">
                <span class="close" onclick="closeModal('codeModal')">&times;</span>
                <h2>Generate Code</h2>
                <form id="codeForm">
                    <div class="form-group">
                        <label for="userStory">User Story:</label>
                        <textarea id="userStory" name="userStory" placeholder="As a user, I want to..." required></textarea>
                    </div>
                    <div class="form-group">
                        <label for="projectType">Project Type:</label>
                        <select id="projectType" name="projectType" required>
                            <option value="web">Web Application</option>
                            <option value="api">API Service</option>
                            <option value="mobile">Mobile App</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="framework">Framework:</label>
                        <select id="framework" name="framework" required>
                            <option value="react">React</option>
                            <option value="vue">Vue.js</option>
                            <option value="angular">Angular</option>
                            <option value="flask">Flask</option>
                            <option value="fastapi">FastAPI</option>
                            <option value="express">Express.js</option>
                        </select>
                    </div>
                    <button type="submit" class="btn">Generate Code</button>
                </form>
                <div id="codeStatus" class="task-status"></div>
            </div>
        </div>
        
        <!-- Deployment Modal -->
        <div id="deployModal" class="modal">
            <div class="modal-content">
                <span class="close" onclick="closeModal('deployModal')">&times;</span>
                <h2>Deploy Application</h2>
                <form id="deployForm">
                    <div class="form-group">
                        <label for="repositoryUrl">Repository URL:</label>
                        <input type="url" id="repositoryUrl" name="repositoryUrl" placeholder="https://github.com/user/repo.git" required>
                    </div>
                    <div class="form-group">
                        <label for="branch">Branch:</label>
                        <input type="text" id="branch" name="branch" value="main">
                    </div>
                    <div class="form-group">
                        <label for="environment">Environment:</label>
                        <select id="environment" name="environment" required>
                            <option value="dev">Development</option>
                            <option value="staging">Staging</option>
                            <option value="prod">Production</option>
                        </select>
                    </div>
                    <button type="submit" class="btn">Deploy</button>
                </form>
                <div id="deployStatus" class="task-status"></div>
            </div>
        </div>
        
        <!-- Full Workflow Modal -->
        <div id="workflowModal" class="modal">
            <div class="modal-content">
                <span class="close" onclick="closeModal('workflowModal')">&times;</span>
                <h2>Full Workflow</h2>
                <form id="workflowForm">
                    <div class="form-group">
                        <label for="workflowMeetingUrl">Meeting URL:</label>
                        <input type="url" id="workflowMeetingUrl" name="meetingUrl" placeholder="https://zoom.us/j/1234567890" required>
                    </div>
                    <div class="form-group">
                        <label for="workflowMeetingType">Meeting Type:</label>
                        <select id="workflowMeetingType" name="meetingType" required>
                            <option value="zoom">Zoom</option>
                            <option value="teams">Microsoft Teams</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="workflowDuration">Duration (minutes):</label>
                        <input type="number" id="workflowDuration" name="duration" value="60" min="1" max="480">
                    </div>
                    <button type="submit" class="btn">Start Workflow</button>
                </form>
                <div id="workflowStatus" class="task-status"></div>
            </div>
        </div>
        
        <script>
            // Modal functions
            function openModal(modalId) {
                document.getElementById(modalId).style.display = 'block';
            }
            
            function closeModal(modalId) {
                document.getElementById(modalId).style.display = 'none';
            }
            
            // Close modal when clicking outside
            window.onclick = function(event) {
                if (event.target.classList.contains('modal')) {
                    event.target.style.display = 'none';
                }
            }
            
            // Form submissions
            document.getElementById('meetingForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const data = Object.fromEntries(formData);
                
                showTaskStatus('meetingStatus', 'Joining meeting...', true);
                
                try {
                    const response = await fetch('/api/v1/attend-meeting', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            meeting_url: data.meetingUrl,
                            meeting_type: data.meetingType,
                            duration: parseInt(data.meetingDuration)
                        })
                    });
                    
                    const result = await response.json();
                    if (response.ok) {
                        showTaskStatus('meetingStatus', `Meeting joined! Task ID: ${result.task_id}`, false);
                        pollTaskStatus(result.task_id, 'meetingStatus');
                    } else {
                        showTaskStatus('meetingStatus', `Error: ${result.detail}`, false);
                    }
                } catch (error) {
                    showTaskStatus('meetingStatus', `Error: ${error.message}`, false);
                }
            });
            
            document.getElementById('jiraForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const data = Object.fromEntries(formData);
                
                showTaskStatus('jiraStatus', 'Processing Jira action...', true);
                
                try {
                    let storyData = {};
                    if (data.storyData) {
                        storyData = JSON.parse(data.storyData);
                    }
                    
                    const response = await fetch('/api/v1/jira-action', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            action: data.jiraAction,
                            story_id: data.storyId,
                            story_data: storyData
                        })
                    });
                    
                    const result = await response.json();
                    if (response.ok) {
                        showTaskStatus('jiraStatus', `Success! Result: ${JSON.stringify(result.result, null, 2)}`, false);
                    } else {
                        showTaskStatus('jiraStatus', `Error: ${result.detail}`, false);
                    }
                } catch (error) {
                    showTaskStatus('jiraStatus', `Error: ${error.message}`, false);
                }
            });
            
            document.getElementById('codeForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const data = Object.fromEntries(formData);
                
                showTaskStatus('codeStatus', 'Generating code...', true);
                
                try {
                    const response = await fetch('/api/v1/generate-code', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            user_story: data.userStory,
                            project_type: data.projectType,
                            framework: data.framework
                        })
                    });
                    
                    const result = await response.json();
                    if (response.ok) {
                        showTaskStatus('codeStatus', `Code generation started! Task ID: ${result.task_id}`, false);
                        pollTaskStatus(result.task_id, 'codeStatus');
                    } else {
                        showTaskStatus('codeStatus', `Error: ${result.detail}`, false);
                    }
                } catch (error) {
                    showTaskStatus('codeStatus', `Error: ${error.message}`, false);
                }
            });
            
            document.getElementById('deployForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const data = Object.fromEntries(formData);
                
                showTaskStatus('deployStatus', 'Starting deployment...', true);
                
                try {
                    const response = await fetch('/api/v1/deploy', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            repository_url: data.repositoryUrl,
                            branch: data.branch,
                            environment: data.environment
                        })
                    });
                    
                    const result = await response.json();
                    if (response.ok) {
                        showTaskStatus('deployStatus', `Deployment started! Task ID: ${result.task_id}`, false);
                        pollTaskStatus(result.task_id, 'deployStatus');
                    } else {
                        showTaskStatus('deployStatus', `Error: ${result.detail}`, false);
                    }
                } catch (error) {
                    showTaskStatus('deployStatus', `Error: ${error.message}`, false);
                }
            });
            
            document.getElementById('workflowForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const data = Object.fromEntries(formData);
                
                showTaskStatus('workflowStatus', 'Starting full workflow...', true);
                
                try {
                    const response = await fetch('/api/v1/execute-task', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            task_type: 'full_workflow',
                            description: 'Complete workflow from meeting to deployment',
                            parameters: {
                                meeting_url: data.meetingUrl,
                                meeting_type: data.meetingType,
                                duration: parseInt(data.duration)
                            }
                        })
                    });
                    
                    const result = await response.json();
                    if (response.ok) {
                        showTaskStatus('workflowStatus', `Workflow started! Task ID: ${result.task_id}`, false);
                        pollTaskStatus(result.task_id, 'workflowStatus');
                    } else {
                        showTaskStatus('workflowStatus', `Error: ${result.detail}`, false);
                    }
                } catch (error) {
                    showTaskStatus('workflowStatus', `Error: ${error.message}`, false);
                }
            });
            
            // Jira action change handler
            document.getElementById('jiraAction').addEventListener('change', function(e) {
                const action = e.target.value;
                const storyIdGroup = document.getElementById('storyIdGroup');
                const storyDataGroup = document.getElementById('storyDataGroup');
                
                if (action === 'get_story' || action === 'update_story') {
                    storyIdGroup.style.display = 'block';
                } else {
                    storyIdGroup.style.display = 'none';
                }
                
                if (action === 'update_story' || action === 'create_story') {
                    storyDataGroup.style.display = 'block';
                } else {
                    storyDataGroup.style.display = 'none';
                }
            });
            
            function showTaskStatus(elementId, message, loading) {
                const element = document.getElementById(elementId);
                element.style.display = 'block';
                element.innerHTML = loading ? 
                    `<div class="loading"></div> ${message}` : 
                    `<pre>${message}</pre>`;
            }
            
            async function pollTaskStatus(taskId, statusElementId) {
                try {
                    const response = await fetch(`/api/v1/task/${taskId}/status`);
                    const status = await response.json();
                    
                    if (response.ok) {
                        const message = `Status: ${status.status}\\nProgress: ${status.progress}%\\n\\nResult: ${JSON.stringify(status.result || status.error || 'In progress...', null, 2)}`;
                        showTaskStatus(statusElementId, message, status.status === 'running');
                        
                        if (status.status === 'running') {
                            setTimeout(() => pollTaskStatus(taskId, statusElementId), 3000);
                        }
                    }
                } catch (error) {
                    console.error('Error polling task status:', error);
                }
            }
        </script>
    </body>
    </html>
    """

@router.get("/status")
async def get_system_status():
    """Get overall system status"""
    # This would be implemented to check the orchestrator status
    return {
        "status": "running",
        "version": "1.0.0",
        "timestamp": "2024-01-01T00:00:00Z",
        "uptime": "24h"
    }