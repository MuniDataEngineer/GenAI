#!/usr/bin/env python3
"""
Basic test script to verify the application structure and imports
"""

def test_imports():
    """Test that all modules can be imported"""
    try:
        print("Testing imports...")
        
        # Test core modules
        from core.config import settings
        print("✅ core.config imported")
        
        from core.orchestrator import AgentOrchestrator
        print("✅ core.orchestrator imported")
        
        # Test agents
        from agents.meeting_agent import MeetingAgent
        print("✅ agents.meeting_agent imported")
        
        from agents.jira_agent import JiraAgent
        print("✅ agents.jira_agent imported")
        
        from agents.code_generator_agent import CodeGeneratorAgent
        print("✅ agents.code_generator_agent imported")
        
        from agents.deployment_agent import DeploymentAgent
        print("✅ agents.deployment_agent imported")
        
        # Test utils
        from utils.task_manager import TaskManager
        print("✅ utils.task_manager imported")
        
        from utils.audio_processor import AudioProcessor
        print("✅ utils.audio_processor imported")
        
        from utils.transcript_analyzer import TranscriptAnalyzer
        print("✅ utils.transcript_analyzer imported")
        
        # Test API
        from api.routes import router
        print("✅ api.routes imported")
        
        print("\n🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {str(e)}")
        return False

def test_configuration():
    """Test configuration loading"""
    try:
        from core.config import settings, get_available_features
        
        print("\nTesting configuration...")
        print(f"App name: {settings.APP_NAME}")
        print(f"Debug mode: {settings.DEBUG}")
        print(f"LLM model: {settings.LLM_MODEL}")
        
        features = get_available_features()
        print(f"Available features: {list(features.keys())}")
        
        print("✅ Configuration loaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {str(e)}")
        return False

def test_agent_initialization():
    """Test that agents can be instantiated"""
    try:
        print("\nTesting agent initialization...")
        
        from agents.meeting_agent import MeetingAgent
        meeting_agent = MeetingAgent()
        print("✅ MeetingAgent created")
        
        from agents.jira_agent import JiraAgent
        jira_agent = JiraAgent()
        print("✅ JiraAgent created")
        
        from agents.code_generator_agent import CodeGeneratorAgent
        code_agent = CodeGeneratorAgent()
        print("✅ CodeGeneratorAgent created")
        
        from agents.deployment_agent import DeploymentAgent
        deploy_agent = DeploymentAgent()
        print("✅ DeploymentAgent created")
        
        print("✅ All agents initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Agent initialization error: {str(e)}")
        return False

def main():
    """Run basic tests"""
    print("🧪 Running basic tests for Agentic AI Application")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_configuration,
        test_agent_initialization
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! The application structure is correct.")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)