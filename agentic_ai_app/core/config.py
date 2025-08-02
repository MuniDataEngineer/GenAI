"""
Configuration management for Agentic AI Application
"""

import os
from typing import Optional
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application settings
    APP_NAME: str = "Agentic AI Assistant"
    DEBUG: bool = Field(default=False, description="Debug mode")
    
    # API Keys
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API key for LLM operations")
    
    # Meeting Integration
    ZOOM_API_KEY: Optional[str] = Field(default=None, description="Zoom API key")
    ZOOM_API_SECRET: Optional[str] = Field(default=None, description="Zoom API secret")
    MICROSOFT_CLIENT_ID: Optional[str] = Field(default=None, description="Microsoft Graph API client ID")
    MICROSOFT_CLIENT_SECRET: Optional[str] = Field(default=None, description="Microsoft Graph API client secret")
    MICROSOFT_TENANT_ID: Optional[str] = Field(default=None, description="Microsoft tenant ID")
    
    # Jira Integration
    JIRA_SERVER: Optional[str] = Field(default=None, description="Jira server URL")
    JIRA_USERNAME: Optional[str] = Field(default=None, description="Jira username")
    JIRA_API_TOKEN: Optional[str] = Field(default=None, description="Jira API token")
    JIRA_PROJECT_KEY: Optional[str] = Field(default=None, description="Default Jira project key")
    
    # Code Repository
    GITHUB_TOKEN: Optional[str] = Field(default=None, description="GitHub personal access token")
    GITLAB_TOKEN: Optional[str] = Field(default=None, description="GitLab access token")
    
    # Deployment
    DOCKER_REGISTRY: Optional[str] = Field(default="docker.io", description="Docker registry URL")
    KUBERNETES_CONFIG_PATH: Optional[str] = Field(default=None, description="Kubernetes config file path")
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, description="AWS access key")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, description="AWS secret key")
    AWS_REGION: str = Field(default="us-east-1", description="AWS region")
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql://user:password@localhost:5432/agentic_ai",
        description="Database connection URL"
    )
    
    # Redis for task queue
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for task queue"
    )
    
    # Security
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT tokens"
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Access token expiration time")
    
    # Meeting Recording
    MEETING_RECORDINGS_PATH: str = Field(
        default="./recordings",
        description="Path to store meeting recordings"
    )
    
    # Generated Code
    CODE_OUTPUT_PATH: str = Field(
        default="./generated_code",
        description="Path to store generated code"
    )
    
    # Agent Configuration
    MAX_CONCURRENT_TASKS: int = Field(default=5, description="Maximum concurrent tasks")
    TASK_TIMEOUT_MINUTES: int = Field(default=30, description="Task timeout in minutes")
    
    # LLM Configuration
    LLM_MODEL: str = Field(default="gpt-4", description="Default LLM model")
    LLM_TEMPERATURE: float = Field(default=0.7, description="LLM temperature")
    LLM_MAX_TOKENS: int = Field(default=4000, description="LLM max tokens")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Global settings instance
settings = Settings()

# Validation functions
def validate_meeting_config() -> bool:
    """Validate meeting integration configuration"""
    zoom_configured = all([
        settings.ZOOM_API_KEY,
        settings.ZOOM_API_SECRET
    ])
    
    teams_configured = all([
        settings.MICROSOFT_CLIENT_ID,
        settings.MICROSOFT_CLIENT_SECRET,
        settings.MICROSOFT_TENANT_ID
    ])
    
    return zoom_configured or teams_configured

def validate_jira_config() -> bool:
    """Validate Jira integration configuration"""
    return all([
        settings.JIRA_SERVER,
        settings.JIRA_USERNAME,
        settings.JIRA_API_TOKEN
    ])

def validate_deployment_config() -> bool:
    """Validate deployment configuration"""
    return settings.KUBERNETES_CONFIG_PATH is not None or all([
        settings.AWS_ACCESS_KEY_ID,
        settings.AWS_SECRET_ACCESS_KEY
    ])

def get_available_features() -> dict:
    """Get list of available features based on configuration"""
    return {
        "meeting_attendance": validate_meeting_config(),
        "jira_integration": validate_jira_config(),
        "code_generation": bool(settings.OPENAI_API_KEY),
        "deployment": validate_deployment_config(),
        "github_integration": bool(settings.GITHUB_TOKEN),
        "gitlab_integration": bool(settings.GITLAB_TOKEN)
    }