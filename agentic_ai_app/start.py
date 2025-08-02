#!/usr/bin/env python3
"""
Startup script for Agentic AI Application
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.11 or higher"""
    if sys.version_info < (3, 11):
        print("❌ Python 3.11 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'fastapi', 'uvicorn', 'openai', 'pydantic', 'requests'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_file = Path('.env')
    if not env_file.exists():
        print("⚠️  .env file not found")
        print("Copy .env.example to .env and configure your settings")
        
        # Create basic .env file
        with open('.env', 'w') as f:
            f.write("# Agentic AI Configuration\n")
            f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
            f.write("DEBUG=true\n")
        
        print("✅ Created basic .env file")
        return False
    
    # Check for OpenAI API key
    with open('.env', 'r') as f:
        content = f.read()
        if 'OPENAI_API_KEY=your_openai_api_key_here' in content:
            print("⚠️  Please set your OPENAI_API_KEY in .env file")
            return False
        elif 'OPENAI_API_KEY=' in content:
            print("✅ OpenAI API key configured")
            return True
    
    print("⚠️  OPENAI_API_KEY not found in .env file")
    return False

def create_directories():
    """Create necessary directories"""
    directories = ['recordings', 'generated_code', 'logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def start_application(port=8000, reload=True):
    """Start the FastAPI application"""
    cmd = [
        "uvicorn", 
        "main:app", 
        "--host", "0.0.0.0", 
        "--port", str(port)
    ]
    
    if reload:
        cmd.append("--reload")
    
    print(f"\n🚀 Starting Agentic AI Application on port {port}...")
    print(f"Dashboard: http://localhost:{port}/api/v1/dashboard")
    print(f"API Docs: http://localhost:{port}/docs")
    print("\nPress Ctrl+C to stop the application\n")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 Application stopped")

def main():
    """Main startup function"""
    print("🤖 Agentic AI Application Startup")
    print("=" * 40)
    
    # Check requirements
    if not check_python_version():
        sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    env_configured = check_env_file()
    
    # Create directories
    create_directories()
    
    if not env_configured:
        print("\n⚠️  Environment not fully configured")
        print("The application will start but some features may not work")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Please configure your .env file and try again")
            sys.exit(1)
    
    # Parse command line arguments
    port = 8000
    reload = True
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--prod':
            reload = False
            print("Starting in production mode")
        elif sys.argv[1].startswith('--port='):
            port = int(sys.argv[1].split('=')[1])
    
    # Start application
    start_application(port, reload)

if __name__ == "__main__":
    main()