"""
Transcript Analyzer - Analyzes meeting transcripts to extract insights and action items
"""

import asyncio
import logging
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

from openai import AsyncOpenAI

from core.config import settings

logger = logging.getLogger(__name__)

class TranscriptAnalyzer:
    """Analyzes meeting transcripts and extracts structured information"""
    
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self._initialized = False
    
    async def initialize(self):
        """Initialize the transcript analyzer"""
        if self._initialized:
            return
        
        logger.info("Initializing Transcript Analyzer...")
        self._initialized = True
        logger.info("Transcript Analyzer initialized successfully")
    
    async def analyze_transcript(self, transcript: str) -> Dict[str, Any]:
        """
        Analyze meeting transcript and extract structured information
        
        Args:
            transcript: The meeting transcript text
            
        Returns:
            Dict containing analysis results
        """
        try:
            logger.info("Analyzing transcript...")
            
            # Perform multiple analyses in parallel
            analyses = await asyncio.gather(
                self._extract_summary(transcript),
                self._extract_action_items(transcript),
                self._extract_key_decisions(transcript),
                self._identify_participants(transcript),
                self._extract_jira_references(transcript),
                self._extract_next_meeting_info(transcript),
                return_exceptions=True
            )
            
            # Combine results
            result = {
                "summary": analyses[0] if not isinstance(analyses[0], Exception) else "Failed to generate summary",
                "action_items": analyses[1] if not isinstance(analyses[1], Exception) else [],
                "key_decisions": analyses[2] if not isinstance(analyses[2], Exception) else [],
                "participants": analyses[3] if not isinstance(analyses[3], Exception) else [],
                "jira_updates": analyses[4] if not isinstance(analyses[4], Exception) else [],
                "next_meeting": analyses[5] if not isinstance(analyses[5], Exception) else None,
                "analyzed_at": datetime.now().isoformat(),
                "transcript_length": len(transcript),
                "word_count": len(transcript.split())
            }
            
            # Extract new stories that should be created
            result["new_stories"] = await self._extract_new_story_requirements(transcript, result)
            
            logger.info("Transcript analysis completed")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing transcript: {str(e)}")
            # Return fallback analysis
            return self._create_fallback_analysis(transcript)
    
    async def _extract_summary(self, transcript: str) -> str:
        """Extract meeting summary"""
        prompt = f"""
        Analyze this meeting transcript and provide a concise summary (2-3 paragraphs):
        
        Transcript: {transcript}
        
        Focus on:
        1. Main topics discussed
        2. Key outcomes and decisions
        3. Overall meeting purpose and results
        
        Provide a clear, professional summary.
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error extracting summary: {str(e)}")
            return "Unable to generate summary due to analysis error."
    
    async def _extract_action_items(self, transcript: str) -> List[Dict[str, Any]]:
        """Extract action items from transcript"""
        prompt = f"""
        Extract action items from this meeting transcript. For each action item, identify:
        1. The task/action to be performed
        2. Who is responsible (assignee)
        3. Any deadline mentioned
        4. Priority level (High/Medium/Low)
        5. Context or additional details
        
        Transcript: {transcript}
        
        Return as JSON array:
        [
            {{
                "description": "task description",
                "assignee": "person name",
                "deadline": "deadline if mentioned",
                "priority": "High/Medium/Low",
                "context": "additional context"
            }}
        ]
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            
            action_items = json.loads(response.choices[0].message.content)
            return action_items if isinstance(action_items, list) else []
            
        except Exception as e:
            logger.error(f"Error extracting action items: {str(e)}")
            # Fallback extraction using regex
            return self._extract_action_items_fallback(transcript)
    
    async def _extract_key_decisions(self, transcript: str) -> List[Dict[str, Any]]:
        """Extract key decisions made during the meeting"""
        prompt = f"""
        Identify key decisions made in this meeting transcript:
        
        Transcript: {transcript}
        
        For each decision, extract:
        1. The decision made
        2. Who made the decision
        3. Rationale if provided
        4. Impact or consequences
        
        Return as JSON array:
        [
            {{
                "decision": "what was decided",
                "decision_maker": "who decided",
                "rationale": "reasoning behind decision",
                "impact": "expected impact"
            }}
        ]
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            
            decisions = json.loads(response.choices[0].message.content)
            return decisions if isinstance(decisions, list) else []
            
        except Exception as e:
            logger.error(f"Error extracting key decisions: {str(e)}")
            return []
    
    async def _identify_participants(self, transcript: str) -> List[Dict[str, Any]]:
        """Identify meeting participants"""
        prompt = f"""
        Identify the participants in this meeting transcript:
        
        Transcript: {transcript}
        
        For each participant, extract:
        1. Name
        2. Role (if mentioned)
        3. Key contributions or topics they discussed
        
        Return as JSON array:
        [
            {{
                "name": "participant name",
                "role": "their role if mentioned",
                "contributions": ["key topics they discussed"]
            }}
        ]
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            
            participants = json.loads(response.choices[0].message.content)
            return participants if isinstance(participants, list) else []
            
        except Exception as e:
            logger.error(f"Error identifying participants: {str(e)}")
            # Fallback: extract names that appear to be speaking
            return self._identify_participants_fallback(transcript)
    
    async def _extract_jira_references(self, transcript: str) -> List[Dict[str, Any]]:
        """Extract Jira ticket references and required updates"""
        # First, find Jira ticket patterns
        jira_patterns = [
            r'\b([A-Z]+-\d+)\b',  # Standard Jira format like PROJ-123
            r'\bticket\s+([A-Z]+-\d+)\b',
            r'\bissue\s+([A-Z]+-\d+)\b',
            r'\bstory\s+([A-Z]+-\d+)\b'
        ]
        
        jira_refs = set()
        for pattern in jira_patterns:
            matches = re.finditer(pattern, transcript, re.IGNORECASE)
            for match in matches:
                jira_refs.add(match.group(1).upper())
        
        # Now analyze what updates are needed for each ticket
        jira_updates = []
        for ticket_id in jira_refs:
            update_info = await self._analyze_jira_update_needed(transcript, ticket_id)
            if update_info:
                jira_updates.append({
                    "ticket_id": ticket_id,
                    **update_info
                })
        
        return jira_updates
    
    async def _analyze_jira_update_needed(self, transcript: str, ticket_id: str) -> Optional[Dict[str, Any]]:
        """Analyze what updates are needed for a specific Jira ticket"""
        prompt = f"""
        Analyze this meeting transcript for references to Jira ticket {ticket_id} and determine what updates are needed:
        
        Transcript: {transcript}
        
        Focus on mentions of {ticket_id} and identify:
        1. Status changes needed (To Do, In Progress, Done, etc.)
        2. New comments to add
        3. Assignee changes
        4. Priority changes
        5. Any other field updates
        
        Return as JSON:
        {{
            "status_change": "new status if mentioned",
            "comment": "comment to add based on discussion",
            "assignee_change": "new assignee if mentioned",
            "priority_change": "new priority if mentioned",
            "other_updates": {{}}
        }}
        
        Return null if no updates are needed for this ticket.
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            
            content = response.choices[0].message.content.strip()
            if content.lower() == "null" or not content:
                return None
            
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"Error analyzing Jira update for {ticket_id}: {str(e)}")
            return None
    
    async def _extract_next_meeting_info(self, transcript: str) -> Optional[Dict[str, Any]]:
        """Extract information about the next meeting"""
        prompt = f"""
        Look for information about the next meeting in this transcript:
        
        Transcript: {transcript}
        
        Extract:
        1. Date/time of next meeting
        2. Meeting type or purpose
        3. Attendees mentioned
        4. Agenda items or topics to cover
        
        Return as JSON:
        {{
            "datetime": "date/time if mentioned",
            "type": "meeting type or purpose",
            "attendees": ["list of attendees"],
            "agenda": ["agenda items or topics"]
        }}
        
        Return null if no next meeting information is found.
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            
            content = response.choices[0].message.content.strip()
            if content.lower() == "null" or not content:
                return None
            
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"Error extracting next meeting info: {str(e)}")
            return None
    
    async def _extract_new_story_requirements(self, transcript: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract requirements for new stories that should be created"""
        prompt = f"""
        Based on this meeting transcript and analysis, identify new user stories or features that should be created in Jira:
        
        Transcript: {transcript}
        
        Analysis summary: {analysis.get('summary', '')}
        Action items: {analysis.get('action_items', [])}
        
        Look for:
        1. New features discussed
        2. Technical debt items
        3. Bug fixes needed
        4. Improvements suggested
        
        For each new story, provide:
        {{
            "title": "concise story title",
            "description": "detailed description",
            "acceptance_criteria": ["list of acceptance criteria"],
            "priority": "High/Medium/Low",
            "story_points": "estimated story points (1-13)",
            "assignee": "suggested assignee if mentioned",
            "labels": ["relevant labels"]
        }}
        
        Return as JSON array of stories.
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            stories = json.loads(response.choices[0].message.content)
            return stories if isinstance(stories, list) else []
            
        except Exception as e:
            logger.error(f"Error extracting new story requirements: {str(e)}")
            return []
    
    def _extract_action_items_fallback(self, transcript: str) -> List[Dict[str, Any]]:
        """Fallback method to extract action items using regex patterns"""
        action_patterns = [
            r'(?:action|todo|task):\s*(.+?)(?:\n|$)',
            r'([A-Za-z\s]+)\s+(?:will|should|needs?\s+to)\s+(.+?)(?:\n|$)',
            r'(?:assigned?\s+to\s+)?([A-Za-z\s]+):\s*(.+?)(?:\n|$)'
        ]
        
        action_items = []
        for pattern in action_patterns:
            matches = re.finditer(pattern, transcript, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if len(match.groups()) == 2:
                    assignee, description = match.groups()
                    action_items.append({
                        "description": description.strip(),
                        "assignee": assignee.strip(),
                        "deadline": None,
                        "priority": "Medium",
                        "context": "Extracted using pattern matching"
                    })
                else:
                    action_items.append({
                        "description": match.group(1).strip(),
                        "assignee": "Unknown",
                        "deadline": None,
                        "priority": "Medium",
                        "context": "Extracted using pattern matching"
                    })
        
        return action_items[:10]  # Limit to 10 items
    
    def _identify_participants_fallback(self, transcript: str) -> List[Dict[str, Any]]:
        """Fallback method to identify participants using patterns"""
        # Look for speaker patterns like "Name:" or "Name said"
        speaker_patterns = [
            r'^([A-Za-z\s]+):\s',
            r'([A-Za-z\s]+)\s+said',
            r'([A-Za-z\s]+)\s+mentioned'
        ]
        
        participants = set()
        for pattern in speaker_patterns:
            matches = re.finditer(pattern, transcript, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                name = match.group(1).strip()
                if len(name) > 1 and len(name) < 50:  # Reasonable name length
                    participants.add(name)
        
        return [
            {
                "name": name,
                "role": "Unknown",
                "contributions": ["Participated in discussion"]
            }
            for name in list(participants)[:10]  # Limit to 10 participants
        ]
    
    def _create_fallback_analysis(self, transcript: str) -> Dict[str, Any]:
        """Create a fallback analysis when AI processing fails"""
        word_count = len(transcript.split())
        
        return {
            "summary": f"Meeting transcript analyzed (fallback mode). Contains {word_count} words of discussion.",
            "action_items": self._extract_action_items_fallback(transcript),
            "key_decisions": [],
            "participants": self._identify_participants_fallback(transcript),
            "jira_updates": [],
            "next_meeting": None,
            "new_stories": [],
            "analyzed_at": datetime.now().isoformat(),
            "transcript_length": len(transcript),
            "word_count": word_count,
            "analysis_mode": "fallback"
        }
    
    async def analyze_sentiment(self, transcript: str) -> Dict[str, Any]:
        """Analyze the sentiment and tone of the meeting"""
        prompt = f"""
        Analyze the sentiment and tone of this meeting transcript:
        
        Transcript: {transcript}
        
        Provide:
        1. Overall sentiment (Positive/Neutral/Negative)
        2. Team morale indicators
        3. Collaboration level
        4. Any tension or conflict indicators
        5. Energy level of the meeting
        
        Return as JSON:
        {{
            "overall_sentiment": "Positive/Neutral/Negative",
            "morale": "High/Medium/Low",
            "collaboration": "High/Medium/Low",
            "tension_indicators": ["any signs of tension"],
            "energy_level": "High/Medium/Low",
            "key_emotions": ["emotions detected"]
        }}
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return {
                "overall_sentiment": "Neutral",
                "morale": "Medium",
                "collaboration": "Medium",
                "tension_indicators": [],
                "energy_level": "Medium",
                "key_emotions": []
            }
    
    async def cleanup(self):
        """Cleanup transcript analyzer resources"""
        logger.info("Cleaning up Transcript Analyzer...")
        # No specific cleanup needed
        logger.info("Transcript Analyzer cleanup completed")