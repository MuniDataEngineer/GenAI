# 🚀 Quick Start Guide

Get your Agentic AI Assistant up and running in 5 minutes!

## 📋 Prerequisites

- Python 3.11 or higher
- OpenAI API key
- Git (optional, for deployment features)

## ⚡ Fast Setup

### 1. Install Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env file and add your OpenAI API key
# At minimum, set: OPENAI_API_KEY=your_actual_api_key_here
```

### 3. Start the Application
```bash
# Use the startup script (recommended)
python3 start.py

# OR start manually
uvicorn main:app --reload
```

### 4. Access the Dashboard
Open your browser to: `http://localhost:8000/api/v1/dashboard`

## 🎯 Quick Test

Try the meeting simulation:

```bash
curl -X POST http://localhost:8000/api/v1/attend-meeting \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_url": "https://zoom.us/j/demo",
    "meeting_type": "zoom",
    "duration": 5
  }'
```

## 🔧 Minimal Configuration

For basic functionality, only the OpenAI API key is required:

```env
OPENAI_API_KEY=your_openai_api_key_here
DEBUG=true
```

## 🚨 Troubleshooting

### Missing Dependencies
```bash
pip install fastapi uvicorn openai pydantic requests aiohttp
```

### Python Version
```bash
python3 --version  # Should be 3.11+
```

### Port Already in Use
```bash
python3 start.py --port=8001
```

## 🎉 What's Next?

1. **Configure Integrations**: Add Jira, GitHub, and meeting platform credentials to `.env`
2. **Explore Features**: Use the web dashboard to test different agents
3. **Run Full Workflow**: Try the complete meeting → Jira → code → deploy pipeline
4. **Deploy**: Use Docker Compose for production deployment

## 📚 Full Documentation

See `README.md` for complete setup instructions, configuration options, and usage examples.

---

**Need help?** Check the troubleshooting section in the main README or create an issue on GitHub.