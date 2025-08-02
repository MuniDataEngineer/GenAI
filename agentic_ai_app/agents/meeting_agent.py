"""
Meeting Agent - Handles Zoom/Teams meeting attendance and information extraction
"""

import asyncio
import logging
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import tempfile
import subprocess

import aiohttp
import requests
from openai import AsyncOpenAI

from core.config import settings
from utils.audio_processor import AudioProcessor
from utils.transcript_analyzer import TranscriptAnalyzer

logger = logging.getLogger(__name__)

class MeetingAgent:
    """AI agent for attending meetings and extracting information"""
    
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.audio_processor = AudioProcessor()
        self.transcript_analyzer = TranscriptAnalyzer()
        self.active_sessions = {}
        self._initialized = False
    
    async def initialize(self):
        """Initialize the meeting agent"""
        if self._initialized:
            return
        
        logger.info("Initializing Meeting Agent...")
        
        try:
            # Create directories
            os.makedirs(settings.MEETING_RECORDINGS_PATH, exist_ok=True)
            
            # Initialize audio processor
            await self.audio_processor.initialize()
            
            # Initialize transcript analyzer
            await self.transcript_analyzer.initialize()
            
            self._initialized = True
            logger.info("Meeting Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Meeting Agent: {str(e)}")
            raise
    
    async def attend_meeting(self, meeting_url: str, meeting_type: str, duration: int = 60) -> Dict[str, Any]:
        """
        Attend a meeting and extract information
        
        Args:
            meeting_url: URL of the meeting
            meeting_type: "zoom" or "teams"
            duration: Duration in minutes
            
        Returns:
            Dict containing meeting summary, action items, and extracted information
        """
        session_id = f"{meeting_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            logger.info(f"Starting meeting attendance: {session_id}")
            
            # Store session info
            self.active_sessions[session_id] = {
                "meeting_url": meeting_url,
                "meeting_type": meeting_type,
                "start_time": datetime.now(),
                "duration": duration,
                "status": "connecting"
            }
            
            if meeting_type.lower() == "zoom":
                result = await self._attend_zoom_meeting(session_id, meeting_url, duration)
            elif meeting_type.lower() == "teams":
                result = await self._attend_teams_meeting(session_id, meeting_url, duration)
            else:
                raise ValueError(f"Unsupported meeting type: {meeting_type}")
            
            # Update session status
            self.active_sessions[session_id]["status"] = "completed"
            self.active_sessions[session_id]["result"] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Error attending meeting {session_id}: {str(e)}")
            if session_id in self.active_sessions:
                self.active_sessions[session_id]["status"] = "failed"
                self.active_sessions[session_id]["error"] = str(e)
            raise
    
    async def _attend_zoom_meeting(self, session_id: str, meeting_url: str, duration: int) -> Dict[str, Any]:
        """Attend a Zoom meeting"""
        logger.info(f"Joining Zoom meeting: {meeting_url}")
        
        # Extract meeting ID from URL
        meeting_id = self._extract_zoom_meeting_id(meeting_url)
        
        # For demo purposes, we'll simulate meeting attendance
        # In a real implementation, you would use Zoom SDK or API
        recording_path = await self._simulate_meeting_recording(session_id, duration)
        
        # Process the recording
        transcript = await self.audio_processor.transcribe_audio(recording_path)
        
        # Analyze transcript
        analysis = await self.transcript_analyzer.analyze_transcript(transcript)
        
        return {
            "session_id": session_id,
            "meeting_type": "zoom",
            "meeting_id": meeting_id,
            "duration": duration,
            "transcript": transcript,
            "summary": analysis["summary"],
            "action_items": analysis["action_items"],
            "key_decisions": analysis["key_decisions"],
            "participants": analysis["participants"],
            "next_meeting": analysis.get("next_meeting"),
            "jira_updates": analysis.get("jira_updates", []),
            "new_stories": analysis.get("new_stories", []),
            "recording_path": recording_path
        }
    
    async def _attend_teams_meeting(self, session_id: str, meeting_url: str, duration: int) -> Dict[str, Any]:
        """Attend a Microsoft Teams meeting"""
        logger.info(f"Joining Teams meeting: {meeting_url}")
        
        # Extract meeting details from URL
        meeting_details = self._extract_teams_meeting_details(meeting_url)
        
        # For demo purposes, we'll simulate meeting attendance
        # In a real implementation, you would use Microsoft Graph API
        recording_path = await self._simulate_meeting_recording(session_id, duration)
        
        # Process the recording
        transcript = await self.audio_processor.transcribe_audio(recording_path)
        
        # Analyze transcript
        analysis = await self.transcript_analyzer.analyze_transcript(transcript)
        
        return {
            "session_id": session_id,
            "meeting_type": "teams",
            "meeting_details": meeting_details,
            "duration": duration,
            "transcript": transcript,
            "summary": analysis["summary"],
            "action_items": analysis["action_items"],
            "key_decisions": analysis["key_decisions"],
            "participants": analysis["participants"],
            "next_meeting": analysis.get("next_meeting"),
            "jira_updates": analysis.get("jira_updates", []),
            "new_stories": analysis.get("new_stories", []),
            "recording_path": recording_path
        }
    
    async def _simulate_meeting_recording(self, session_id: str, duration: int) -> str:
        """
        Simulate meeting recording for demo purposes
        In production, this would capture actual meeting audio
        """
        recording_path = os.path.join(
            settings.MEETING_RECORDINGS_PATH,
            f"{session_id}_recording.wav"
        )
        
        # Create a sample audio file (silence) for demo
        # In real implementation, this would be actual meeting audio
        sample_text = """
        Welcome to our daily standup meeting. Let's go around and share our updates.
        
        John: Yesterday I completed the user authentication feature. Today I'm working on 
        the dashboard component. I'm blocked on the API integration for user profiles.
        
        Sarah: I finished the database schema updates and deployed them to staging. 
        Today I'll be working on the user story PROJ-123 for the shopping cart feature.
        I need to update the Jira ticket status to In Progress.
        
        Mike: I completed the code review for the payment integration. Today I'm starting
        work on PROJ-124 for the notification system. No blockers currently.
        
        Team Lead: Great updates everyone. John, I'll help you with the API integration 
        after this meeting. Sarah, make sure to update PROJ-123 status. Mike, create 
        a new story for the email notification feature we discussed.
        
        Action items:
        1. John to get help with API integration
        2. Sarah to update PROJ-123 to In Progress
        3. Mike to create new story for email notifications
        4. Next meeting same time tomorrow
        
        Meeting ended.
        """
        
        # Save sample transcript as a file
        with open(recording_path.replace('.wav', '_transcript.txt'), 'w') as f:
            f.write(sample_text)
        
        # Create empty audio file for demo
        with open(recording_path, 'wb') as f:
            f.write(b'')  # Empty file for demo
        
        return recording_path
    
    def _extract_zoom_meeting_id(self, meeting_url: str) -> str:
        """Extract meeting ID from Zoom URL"""
        import re
        
        # Pattern to match Zoom meeting IDs
        patterns = [
            r'/j/(\d+)',  # https://zoom.us/j/1234567890
            r'meeting_id=(\d+)',  # ?meeting_id=1234567890
            r'/(\d{9,11})(?:\?|$)',  # Direct ID in URL
        ]
        
        for pattern in patterns:
            match = re.search(pattern, meeting_url)
            if match:
                return match.group(1)
        
        return "unknown"
    
    def _extract_teams_meeting_details(self, meeting_url: str) -> Dict[str, str]:
        """Extract meeting details from Teams URL"""
        import re
        from urllib.parse import urlparse, parse_qs
        
        parsed = urlparse(meeting_url)
        query_params = parse_qs(parsed.query)
        
        return {
            "domain": parsed.netloc,
            "thread_id": query_params.get("threadId", ["unknown"])[0],
            "message_id": query_params.get("messageId", ["unknown"])[0],
            "tenant_id": query_params.get("tenantId", ["unknown"])[0]
        }
    
    async def get_meeting_status(self, session_id: str) -> Dict[str, Any]:
        """Get status of a meeting session"""
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}
        
        return self.active_sessions[session_id]
    
    async def list_active_meetings(self) -> List[Dict[str, Any]]:
        """List all active meeting sessions"""
        return [
            {
                "session_id": session_id,
                "status": session_info["status"],
                "meeting_type": session_info["meeting_type"],
                "start_time": session_info["start_time"].isoformat(),
                "duration": session_info["duration"]
            }
            for session_id, session_info in self.active_sessions.items()
        ]
    
    async def end_meeting(self, session_id: str) -> bool:
        """End a meeting session early"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["status"] = "ended"
            self.active_sessions[session_id]["end_time"] = datetime.now()
            return True
        return False
    
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "status": "active" if self._initialized else "inactive",
            "active_meetings": len([
                s for s in self.active_sessions.values() 
                if s["status"] in ["connecting", "recording"]
            ]),
            "total_sessions": len(self.active_sessions),
            "capabilities": {
                "zoom": bool(settings.ZOOM_API_KEY),
                "teams": bool(settings.MICROSOFT_CLIENT_ID),
                "audio_processing": True,
                "transcript_analysis": True
            }
        }
    
    async def cleanup(self):
        """Cleanup agent resources"""
        logger.info("Cleaning up Meeting Agent...")
        
        # End all active meetings
        for session_id in list(self.active_sessions.keys()):
            await self.end_meeting(session_id)
        
        # Cleanup processors
        if hasattr(self.audio_processor, 'cleanup'):
            await self.audio_processor.cleanup()
        
        if hasattr(self.transcript_analyzer, 'cleanup'):
            await self.transcript_analyzer.cleanup()
        
        logger.info("Meeting Agent cleanup completed")