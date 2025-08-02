# 🤖 Agentic AI Assistant

A comprehensive AI-powered automation platform that can attend meetings, manage Jira projects, generate code, and deploy applications autonomously.

## ✨ Features

### 🎯 Meeting Assistant
- **Zoom/Teams Integration**: Automatically join meetings and record conversations
- **Real-time Transcription**: Convert meeting audio to text using OpenAI Whisper
- **Smart Analysis**: Extract action items, decisions, and participant insights
- **Automatic Updates**: Update Jira stories based on meeting discussions

### 📋 Jira Management
- **Story Operations**: Create, read, update, and search Jira stories
- **Smart Processing**: AI-powered analysis of action items to determine Jira updates
- **Workflow Automation**: Automatically transition stories based on meeting outcomes
- **Bulk Operations**: Handle multiple tickets efficiently

### 💻 Code Generation
- **Multi-Framework Support**: React, Vue, Angular, Flask, FastAPI, Express.js
- **Complete Projects**: Generate full application structure with tests
- **Git Integration**: Automatically create repositories and commit initial code
- **Best Practices**: Modern development patterns and project structure

### 🚀 Deployment Automation
- **Multi-Environment**: Deploy to development, staging, and production
- **Container Support**: Docker and Kubernetes deployment strategies
- **Cloud Integration**: AWS, Azure, and local deployment options
- **Monitoring**: Track deployment status and health

### 🔄 Complete Workflow
Execute the full development lifecycle:
1. **Attend Meeting** → Extract requirements
2. **Update Jira** → Create/update stories
3. **Generate Code** → Build applications
4. **Deploy** → Push to environments

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker (optional, for containerized deployment)
- OpenAI API key
- Git

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd agentic_ai_app
```

2. **Set up environment**:
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

3. **Configure environment variables**:
```bash
# Copy example configuration
cp .env.example .env

# Edit .env with your API keys and settings
# At minimum, set OPENAI_API_KEY
```

4. **Run the application**:
```bash
# Development mode
uvicorn main:app --reload

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000
```

5. **Access the dashboard**:
Open your browser to `http://localhost:8000/api/v1/dashboard`

### Docker Deployment

1. **Using Docker Compose** (recommended):
```bash
# Copy environment file
cp .env.example .env
# Edit .env with your settings

# Start services
docker-compose up -d

# View logs
docker-compose logs -f agentic-ai
```

2. **Manual Docker build**:
```bash
# Build image
docker build -t agentic-ai .

# Run container
docker run -p 8000:8000 --env-file .env agentic-ai
```

## 📊 API Documentation

### Core Endpoints

#### Health Check
```http
GET /
```

#### Feature Status
```http
GET /api/v1/features
```

#### Meeting Operations
```http
POST /api/v1/attend-meeting
Content-Type: application/json

{
  "meeting_url": "https://zoom.us/j/1234567890",
  "meeting_type": "zoom",
  "duration": 60
}
```

#### Jira Operations
```http
POST /api/v1/jira-action
Content-Type: application/json

{
  "action": "get_story",
  "story_id": "PROJ-123"
}
```

#### Code Generation
```http
POST /api/v1/generate-code
Content-Type: application/json

{
  "user_story": "As a user, I want to...",
  "project_type": "web",
  "framework": "react"
}
```

#### Deployment
```http
POST /api/v1/deploy
Content-Type: application/json

{
  "repository_url": "https://github.com/user/repo.git",
  "branch": "main",
  "environment": "dev"
}
```

#### Task Management
```http
GET /api/v1/task/{task_id}/status
GET /api/v1/agents/status
```

### Interactive Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## ⚙️ Configuration

### Required Settings
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Optional Integrations

#### Meeting Platforms
```env
# Zoom
ZOOM_API_KEY=your_zoom_api_key
ZOOM_API_SECRET=your_zoom_api_secret

# Microsoft Teams
MICROSOFT_CLIENT_ID=your_microsoft_client_id
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret
MICROSOFT_TENANT_ID=your_microsoft_tenant_id
```

#### Project Management
```env
# Jira
JIRA_SERVER=https://your-domain.atlassian.net
JIRA_USERNAME=your_jira_email@example.com
JIRA_API_TOKEN=your_jira_api_token
JIRA_PROJECT_KEY=PROJ
```

#### Code Repository
```env
# GitHub
GITHUB_TOKEN=your_github_personal_access_token

# GitLab
GITLAB_TOKEN=your_gitlab_access_token
```

#### Deployment
```env
# Docker
DOCKER_REGISTRY=docker.io

# Kubernetes
KUBERNETES_CONFIG_PATH=/path/to/kubeconfig

# AWS
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
```

## 🏗️ Architecture

### Components
- **Main Orchestrator**: Coordinates all agents and manages workflows
- **Meeting Agent**: Handles meeting attendance and transcription
- **Jira Agent**: Manages project tracking and story operations
- **Code Generator Agent**: Creates applications from requirements
- **Deployment Agent**: Handles application deployment
- **Task Manager**: Tracks asynchronous operations

### Data Flow
```
Meeting → Transcription → Analysis → Jira Updates → Code Generation → Deployment
```

### Technologies
- **Backend**: FastAPI, Python 3.11
- **AI/ML**: OpenAI GPT-4, Whisper
- **Integrations**: Jira API, GitHub API, Zoom SDK, Teams API
- **Containerization**: Docker, Kubernetes
- **Database**: PostgreSQL (optional), SQLite (default)
- **Queue**: Redis (optional)

## 🧪 Testing

### Run Tests
```bash
# Unit tests
pytest tests/

# Integration tests
pytest tests/integration/

# Coverage report
pytest --cov=agentic_ai_app tests/
```

### Test Meeting Integration
```bash
# Simulate meeting attendance (uses demo transcript)
curl -X POST http://localhost:8000/api/v1/attend-meeting \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_url": "https://zoom.us/j/demo",
    "meeting_type": "zoom",
    "duration": 5
  }'
```

## 📋 Usage Examples

### Complete Workflow Example
```python
import requests

# Start full workflow
response = requests.post('http://localhost:8000/api/v1/execute-task', json={
    "task_type": "full_workflow",
    "description": "Complete development workflow",
    "parameters": {
        "meeting_url": "https://zoom.us/j/1234567890",
        "meeting_type": "zoom",
        "duration": 60
    }
})

task_id = response.json()['task_id']

# Monitor progress
import time
while True:
    status = requests.get(f'http://localhost:8000/api/v1/task/{task_id}/status')
    result = status.json()
    print(f"Status: {result['status']}, Progress: {result['progress']}%")
    
    if result['status'] in ['completed', 'failed']:
        break
    
    time.sleep(5)
```

### Individual Agent Usage
```python
# Generate code from user story
response = requests.post('http://localhost:8000/api/v1/generate-code', json={
    "user_story": "As a customer, I want to view product details",
    "project_type": "web",
    "framework": "react"
})

# Update Jira story
response = requests.post('http://localhost:8000/api/v1/jira-action', json={
    "action": "update_story",
    "story_id": "PROJ-123",
    "story_data": {
        "status": "In Progress",
        "comment": "Updated from meeting discussion"
    }
})

# Deploy application
response = requests.post('http://localhost:8000/api/v1/deploy', json={
    "repository_url": "https://github.com/user/myapp.git",
    "branch": "main",
    "environment": "dev"
})
```

## 🔧 Development

### Project Structure
```
agentic_ai_app/
├── agents/                 # AI agent implementations
│   ├── meeting_agent.py   # Meeting attendance and analysis
│   ├── jira_agent.py      # Jira integration
│   ├── code_generator_agent.py  # Code generation
│   └── deployment_agent.py      # Deployment automation
├── api/                   # API routes and models
├── core/                  # Core application logic
│   ├── config.py         # Configuration management
│   └── orchestrator.py   # Main orchestrator
├── utils/                 # Utility modules
│   ├── task_manager.py   # Task lifecycle management
│   ├── audio_processor.py # Audio processing
│   └── transcript_analyzer.py # Meeting analysis
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
├── docker-compose.yml    # Container orchestration
└── Dockerfile           # Container image
```

### Adding New Agents
1. Create agent class in `agents/`
2. Implement required methods: `initialize()`, `cleanup()`, `get_status()`
3. Register agent in orchestrator
4. Add API endpoints if needed

### Contributing
1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request

## 🚨 Troubleshooting

### Common Issues

#### Missing API Keys
```
ERROR: OpenAI API key not found
```
**Solution**: Set `OPENAI_API_KEY` in your `.env` file

#### Meeting Join Failures
```
ERROR: Failed to join meeting
```
**Solutions**:
- Verify meeting URL format
- Check API credentials for Zoom/Teams
- Ensure meeting is active

#### Deployment Failures
```
ERROR: Docker not available
```
**Solutions**:
- Install Docker
- Start Docker service
- Check Docker permissions

#### Jira Connection Issues
```
ERROR: Jira authentication failed
```
**Solutions**:
- Verify Jira server URL
- Check API token validity
- Confirm user permissions

### Logs and Debugging
```bash
# View application logs
docker-compose logs -f agentic-ai

# Debug mode
DEBUG=true uvicorn main:app --reload

# Increase log verbosity
export LOG_LEVEL=DEBUG
```

## 📈 Monitoring

### Health Checks
- Application: `GET /`
- Agents: `GET /api/v1/agents/status`
- Features: `GET /api/v1/features`

### Metrics
- Task completion rates
- Agent response times
- Integration success rates
- Resource utilization

## 🔒 Security

### Best Practices
- Store API keys in environment variables
- Use HTTPS in production
- Implement rate limiting
- Regular security updates

### Authentication
- JWT token support
- API key validation
- Role-based access control (future)

## 📚 Additional Resources

### Documentation
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Jira REST API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [Zoom API Documentation](https://marketplace.zoom.us/docs/api-reference)
- [Microsoft Graph API](https://docs.microsoft.com/en-us/graph/)

### Community
- GitHub Issues for bug reports
- Discussions for feature requests
- Wiki for additional documentation

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Support

For support and questions:
- Create an issue on GitHub
- Check existing documentation
- Review troubleshooting section

---

**Made with ❤️ for developers who want to automate everything**