"""
🧘 PSYCHOLOGY & THERAPY HUB™ - Mental Health Support for Traders
CamboAI TraderStation: Trade with Vision, Learn with Purpose, Evolve with AI
Professional-grade AI therapy and psychological support system
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import logging
from dataclasses import dataclass
import json
import openai
from anthropic import Anthropic
import google.generativeai as genai
from textblob import TextBlob
import nltk
from transformers import pipeline

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.download('vader_lexicon', quiet=True)
    nltk.download('punkt', quiet=True)
except:
    pass

class EmotionalState(Enum):
    """Emotional states for classification"""
    CALM = "CALM"
    ANXIOUS = "ANXIOUS" 
    FEARFUL = "FEARFUL"
    GREEDY = "GREEDY"
    FRUSTRATED = "FRUSTRATED"
    CONFIDENT = "CONFIDENT"
    DEPRESSED = "DEPRESSED"
    MANIC = "MANIC"
    OVERWHELMED = "OVERWHELMED"
    REGRETFUL = "REGRETFUL"

class TherapyType(Enum):
    """Types of therapy approaches"""
    COGNITIVE_BEHAVIORAL = "CBT"
    MINDFULNESS = "MINDFULNESS"
    ACCEPTANCE_COMMITMENT = "ACT"
    DIALECTICAL_BEHAVIORAL = "DBT"
    PSYCHODYNAMIC = "PSYCHODYNAMIC"
    CRISIS_INTERVENTION = "CRISIS"

class RiskLevel(Enum):
    """Risk levels for psychological assessment"""
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

@dataclass
class PsychologicalProfile:
    """Comprehensive psychological profile of trader"""
    user_id: str
    emotional_patterns: Dict[str, float]
    stress_triggers: List[str]
    coping_mechanisms: List[str]
    trading_psychology_type: str
    risk_tolerance: float
    impulsivity_score: float
    anxiety_level: float
    confidence_level: float
    last_updated: datetime

@dataclass
class TherapySession:
    """Individual therapy session record"""
    session_id: str
    user_id: str
    session_type: TherapyType
    emotional_state: EmotionalState
    risk_level: RiskLevel
    session_notes: str
    interventions_used: List[str]
    homework_assigned: Optional[str]
    follow_up_needed: bool
    duration_minutes: int
    timestamp: datetime

@dataclass
class CrisisAlert:
    """Crisis intervention alert"""
    alert_id: str
    user_id: str
    risk_level: RiskLevel
    trigger_indicators: List[str]
    immediate_actions: List[str]
    emergency_contacts: List[str]
    timestamp: datetime

class TradingTherapyBot:
    """
    AI-powered therapy bot specialized in trading psychology
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Initialize AI models for different therapy approaches
        self.ai_therapists = {
            "cbt_therapist": openai.OpenAI(api_key=config.get("openai_key")),
            "mindfulness_guide": genai.GenerativeModel('gemini-pro'),
            "crisis_counselor": Anthropic(api_key=config.get("anthropic_key")),
            "behavioral_analyst": pipeline("sentiment-analysis", model="j-hartmann/emotion-english-distilroberta-base")
        }
        
        # Therapy session management
        self.active_sessions = {}
        self.user_profiles = {}
        self.therapy_history = {}
        self.crisis_protocols = {}
        
        # Initialize therapeutic protocols
        self.initialize_therapy_protocols()
    
    def initialize_therapy_protocols(self):
        """
        Initialize evidence-based therapy protocols
        """
        self.therapy_protocols = {
            TherapyType.COGNITIVE_BEHAVIORAL: {
                "techniques": [
                    "thought_challenging",
                    "behavioral_activation", 
                    "exposure_therapy",
                    "cognitive_restructuring"
                ],
                "homework_exercises": [
                    "thought_record",
                    "behavioral_experiment",
                    "mindful_trading_log",
                    "grounding_techniques"
                ]
            },
            TherapyType.MINDFULNESS: {
                "techniques": [
                    "mindful_breathing",
                    "body_scan_meditation",
                    "present_moment_awareness",
                    "observing_thoughts"
                ],
                "homework_exercises": [
                    "daily_meditation",
                    "mindful_trading_practice",
                    "emotional_awareness_log"
                ]
            },
            TherapyType.CRISIS_INTERVENTION: {
                "techniques": [
                    "safety_planning",
                    "grounding_techniques",
                    "immediate_coping_strategies",
                    "emergency_contact_activation"
                ],
                "immediate_actions": [
                    "assess_immediate_safety",
                    "pause_all_trading",
                    "activate_support_network",
                    "implement_crisis_plan"
                ]
            }
        }
    
    async def start_therapy_session(self, user_id: str, presenting_issue: str) -> TherapySession:
        """
        Start a new therapy session based on user's presenting issue
        """
        try:
            # Assess emotional state and risk level
            emotional_assessment = await self.assess_emotional_state(user_id, presenting_issue)
            
            # Determine appropriate therapy type
            therapy_type = await self.determine_therapy_approach(emotional_assessment)
            
            # Check for crisis indicators
            crisis_risk = await self.assess_crisis_risk(emotional_assessment)
            
            # Create session
            session = TherapySession(
                session_id=str(uuid.uuid4()),
                user_id=user_id,
                session_type=therapy_type,
                emotional_state=emotional_assessment["primary_emotion"],
                risk_level=crisis_risk,
                session_notes="",
                interventions_used=[],
                homework_assigned=None,
                follow_up_needed=False,
                duration_minutes=0,
                timestamp=datetime.now()
            )
            
            # Handle crisis situations immediately
            if crisis_risk == RiskLevel.CRITICAL:
                await self.initiate_crisis_intervention(user_id, session)
            
            # Store active session
            self.active_sessions[session.session_id] = session
            
            # Begin therapeutic intervention
            therapeutic_response = await self.conduct_therapy_session(session, presenting_issue)
            
            return session
            
        except Exception as e:
            logger.error(f"Error starting therapy session: {e}")
            # Create emergency session for system errors
            return await self.create_emergency_support_session(user_id, str(e))
    
    async def assess_emotional_state(self, user_id: str, text_input: str) -> Dict[str, Any]:
        """
        Comprehensive emotional state assessment
        """
        try:
            # Sentiment analysis
            blob = TextBlob(text_input)
            sentiment_polarity = blob.sentiment.polarity
            
            # Emotion detection using transformer model
            emotions = self.ai_therapists["behavioral_analyst"](text_input)
            
            # Analyze trading-specific emotional patterns
            trading_emotions = await self.analyze_trading_emotions(text_input)
            
            # Stress level assessment
            stress_indicators = await self.detect_stress_indicators(text_input)
            
            # Risk assessment
            risk_markers = await self.identify_risk_markers(text_input)
            
            return {
                "primary_emotion": self.classify_primary_emotion(emotions),
                "sentiment_score": sentiment_polarity,
                "stress_level": stress_indicators["level"],
                "risk_markers": risk_markers,
                "trading_specific_emotions": trading_emotions,
                "confidence": emotions[0]["score"] if emotions else 0.5
            }
            
        except Exception as e:
            logger.error(f"Error assessing emotional state: {e}")
            return {
                "primary_emotion": EmotionalState.ANXIOUS,
                "sentiment_score": 0.0,
                "stress_level": "MODERATE",
                "risk_markers": [],
                "confidence": 0.0
            }
    
    async def conduct_therapy_session(self, session: TherapySession, issue: str) -> str:
        """
        Conduct appropriate therapy session based on type and needs
        """
        try:
            if session.session_type == TherapyType.COGNITIVE_BEHAVIORAL:
                return await self.cbt_session(session, issue)
            elif session.session_type == TherapyType.MINDFULNESS:
                return await self.mindfulness_session(session, issue)
            elif session.session_type == TherapyType.CRISIS_INTERVENTION:
                return await self.crisis_intervention_session(session, issue)
            else:
                return await self.general_therapy_session(session, issue)
                
        except Exception as e:
            logger.error(f"Error conducting therapy session: {e}")
            return "I'm here to support you. Let's take this step by step."
    
    async def cbt_session(self, session: TherapySession, issue: str) -> str:
        """
        Cognitive Behavioral Therapy session
        """
        prompt = f"""
        You are a licensed CBT therapist specializing in trading psychology. 
        Conduct a CBT session for this trader's issue:
        
        Issue: {issue}
        Emotional State: {session.emotional_state.value}
        Risk Level: {session.risk_level.value}
        
        Use CBT techniques:
        1. Identify unhelpful thought patterns
        2. Challenge cognitive distortions
        3. Develop coping strategies
        4. Assign behavioral experiments
        
        Provide:
        - Empathetic response
        - Specific CBT intervention
        - Homework assignment
        - Coping strategies for trading stress
        
        Be professional, supportive, and evidence-based.
        """
        
        response = await self.query_ai_therapist("cbt_therapist", prompt)
        
        # Track intervention used
        session.interventions_used.append("CBT_THOUGHT_CHALLENGING")
        
        return response
    
    async def mindfulness_session(self, session: TherapySession, issue: str) -> str:
        """
        Mindfulness-based therapy session
        """
        prompt = f"""
        You are a mindfulness-based therapist helping a trader with emotional regulation.
        
        Issue: {issue}
        Current State: {session.emotional_state.value}
        
        Provide:
        1. Mindfulness-based response
        2. Breathing exercise for immediate relief
        3. Present-moment awareness technique
        4. Mindful trading practice
        
        Guide them through a 5-minute mindfulness exercise.
        Be calm, grounding, and present-focused.
        """
        
        response = await self.query_ai_therapist("mindfulness_guide", prompt)
        
        # Track intervention
        session.interventions_used.append("MINDFULNESS_EXERCISE")
        
        return response
    
    async def crisis_intervention_session(self, session: TherapySession, issue: str) -> str:
        """
        Crisis intervention session for high-risk situations
        """
        prompt = f"""
        CRISIS INTERVENTION PROTOCOL - IMMEDIATE RESPONSE NEEDED
        
        Issue: {issue}
        Risk Level: {session.risk_level.value}
        
        Provide immediate crisis intervention:
        1. Ensure immediate safety
        2. Validate their experience
        3. Provide grounding techniques
        4. Create safety plan
        5. Identify support resources
        
        CRITICAL: This person needs immediate professional support.
        Be direct, supportive, and action-oriented.
        """
        
        response = await self.query_ai_therapist("crisis_counselor", prompt)
        
        # Implement crisis protocols
        await self.activate_crisis_protocols(session.user_id)
        
        session.interventions_used.append("CRISIS_INTERVENTION")
        session.follow_up_needed = True
        
        return response
    
    async def provide_coping_strategies(self, emotional_state: EmotionalState, trading_context: str) -> List[str]:
        """
        Provide specific coping strategies based on emotional state
        """
        strategies = {
            EmotionalState.ANXIOUS: [
                "Deep breathing exercise (4-7-8 technique)",
                "Progressive muscle relaxation",
                "Challenge catastrophic thoughts",
                "Focus on process, not outcomes",
                "Take a 10-minute break from screens"
            ],
            EmotionalState.FEARFUL: [
                "Ground yourself with 5-4-3-2-1 technique",
                "Remind yourself of past successful trades",
                "Review your risk management rules",
                "Connect with your trading mentor",
                "Use smaller position sizes until confidence returns"
            ],
            EmotionalState.GREEDY: [
                "Review your trading plan",
                "Calculate maximum acceptable loss",
                "Take profits according to plan",
                "Remind yourself: 'Pigs get slaughtered'",
                "Step away and reassess market objectively"
            ],
            EmotionalState.FRUSTRATED: [
                "Acknowledge the frustration without judgment",
                "Review what you learned from recent trades",
                "Take a longer break from trading",
                "Journal about your frustrations",
                "Focus on process improvements, not just profits"
            ],
            EmotionalState.OVERWHELMED: [
                "Simplify your trading approach",
                "Focus on one market/strategy at a time",
                "Use trading checklists",
                "Delegate or automate routine tasks",
                "Practice saying 'no' to marginal opportunities"
            ]
        }
        
        return strategies.get(emotional_state, [
            "Take deep breaths",
            "Focus on the present moment", 
            "Review your trading rules",
            "Consider taking a break"
        ])
    
    async def mood_tracking_system(self, user_id: str) -> Dict[str, Any]:
        """
        Daily mood and emotional tracking system
        """
        try:
            # Get recent mood data
            recent_moods = await self.get_recent_mood_data(user_id)
            
            # Analyze patterns
            mood_patterns = await self.analyze_mood_patterns(recent_moods)
            
            # Identify triggers
            triggers = await self.identify_emotional_triggers(user_id, recent_moods)
            
            # Generate insights
            insights = await self.generate_mood_insights(mood_patterns, triggers)
            
            return {
                "current_mood_score": recent_moods[-1] if recent_moods else 5.0,
                "mood_trend": mood_patterns.get("trend", "stable"),
                "identified_triggers": triggers,
                "insights": insights,
                "recommendations": await self.get_mood_recommendations(mood_patterns)
            }
            
        except Exception as e:
            logger.error(f"Error in mood tracking: {e}")
            return {"error": str(e)}
    
    async def generate_personalized_affirmations(self, user_id: str) -> List[str]:
        """
        Generate personalized positive affirmations for trader
        """
        user_profile = await self.get_user_psychological_profile(user_id)
        
        affirmations = [
            "I trust my trading plan and stick to my rules",
            "I am calm and confident in my decision-making",
            "Losses are part of trading, and I learn from each one",
            "I control my emotions, they don't control me",
            "I am patient and wait for high-probability setups",
            "My risk management protects my capital",
            "I am grateful for the opportunities the market provides",
            "I continuously improve my trading skills",
            "I maintain perspective and don't let one trade define me",
            "I am disciplined, focused, and successful"
        ]
        
        # Personalize based on user's specific challenges
        if user_profile and user_profile.get("common_issues"):
            if "FOMO" in user_profile["common_issues"]:
                affirmations.extend([
                    "There will always be another opportunity",
                    "I only trade setups that match my criteria",
                    "Patience is my competitive advantage"
                ])
            
            if "OVERTRADING" in user_profile["common_issues"]:
                affirmations.extend([
                    "Quality over quantity in my trading decisions",
                    "I wait for my best setups",
                    "Less is more when it comes to trading"
                ])
        
        return affirmations
    
    async def breathing_exercise_guide(self, exercise_type: str = "4-7-8") -> Dict[str, Any]:
        """
        Provide guided breathing exercises for stress relief
        """
        exercises = {
            "4-7-8": {
                "name": "4-7-8 Calming Breath",
                "description": "Inhale 4, hold 7, exhale 8 - repeat 4 times",
                "steps": [
                    "Sit comfortably with straight back",
                    "Exhale completely through mouth",
                    "Inhale through nose for 4 counts",
                    "Hold breath for 7 counts",
                    "Exhale through mouth for 8 counts",
                    "Repeat cycle 3 more times"
                ],
                "duration_minutes": 2,
                "benefits": ["Reduces anxiety", "Promotes calm", "Improves focus"]
            },
            "box_breathing": {
                "name": "Box Breathing",
                "description": "4-4-4-4 pattern for focus and control",
                "steps": [
                    "Inhale for 4 counts",
                    "Hold for 4 counts", 
                    "Exhale for 4 counts",
                    "Hold empty for 4 counts",
                    "Repeat for 5-10 cycles"
                ],
                "duration_minutes": 3,
                "benefits": ["Improves focus", "Builds mental discipline", "Reduces stress"]
            },
            "coherent_breathing": {
                "name": "Coherent Breathing",
                "description": "5-second inhale, 5-second exhale for balance",
                "steps": [
                    "Breathe in slowly for 5 counts",
                    "Breathe out slowly for 5 counts",
                    "Continue for 10-20 cycles",
                    "Focus on smooth, even breaths"
                ],
                "duration_minutes": 5,
                "benefits": ["Heart rate variability", "Emotional balance", "Stress relief"]
            }
        }
        
        return exercises.get(exercise_type, exercises["4-7-8"])
    
    async def query_ai_therapist(self, therapist_type: str, prompt: str) -> str:
        """
        Query appropriate AI therapist based on type
        """
        try:
            if therapist_type == "cbt_therapist":
                response = await self.ai_therapists[therapist_type].chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a licensed CBT therapist specializing in trading psychology. Provide evidence-based therapeutic interventions."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                return response.choices[0].message.content
                
            elif therapist_type == "crisis_counselor":
                response = await self.ai_therapists[therapist_type].messages.create(
                    model="claude-3-opus-20240229",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
                
            elif therapist_type == "mindfulness_guide":
                response = await self.ai_therapists[therapist_type].generate_content(prompt)
                return response.text
                
        except Exception as e:
            logger.error(f"Error querying AI therapist: {e}")
            return "I'm here to support you. Let's work through this together."
    
    async def activate_crisis_protocols(self, user_id: str):
        """
        Activate crisis intervention protocols
        """
        try:
            # Create crisis alert
            alert = CrisisAlert(
                alert_id=str(uuid.uuid4()),
                user_id=user_id,
                risk_level=RiskLevel.CRITICAL,
                trigger_indicators=["Crisis_intervention_activated"],
                immediate_actions=[
                    "Pause all trading activities",
                    "Activate support network",
                    "Provide crisis resources",
                    "Schedule follow-up session"
                ],
                emergency_contacts=[],
                timestamp=datetime.now()
            )
            
            # Log crisis event
            logger.critical(f"Crisis intervention activated for user: {user_id}")
            
            # Pause trading if integrated with trading system
            await self.pause_trading_activities(user_id)
            
            # Send emergency notifications
            await self.send_crisis_notifications(user_id, alert)
            
        except Exception as e:
            logger.error(f"Error activating crisis protocols: {e}")
    
    def classify_primary_emotion(self, emotions: List[Dict]) -> EmotionalState:
        """
        Classify primary emotion from analysis results
        """
        if not emotions:
            return EmotionalState.CALM
            
        emotion_mapping = {
            "fear": EmotionalState.FEARFUL,
            "anxiety": EmotionalState.ANXIOUS,
            "anger": EmotionalState.FRUSTRATED,
            "sadness": EmotionalState.DEPRESSED,
            "joy": EmotionalState.CONFIDENT,
            "neutral": EmotionalState.CALM
        }
        
        primary_emotion = emotions[0]["label"].lower()
        return emotion_mapping.get(primary_emotion, EmotionalState.ANXIOUS)
    
    async def generate_therapy_report(self, user_id: str, timeframe_days: int = 30) -> Dict[str, Any]:
        """
        Generate comprehensive therapy progress report
        """
        return {
            "sessions_completed": 0,
            "primary_issues_addressed": [],
            "therapeutic_progress": 0.0,
            "coping_skills_developed": [],
            "emotional_stability_trend": "improving",
            "recommendations": [],
            "next_session_recommended": datetime.now() + timedelta(days=7)
        }

# Integration with main CamboStation system
class PsychologyHub:
    """
    Main psychology hub integrating all mental health features
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.therapy_bot = TradingTherapyBot(config)
        self.mood_tracker = {}
        self.crisis_system = {}
        
    async def provide_comprehensive_support(self, user_id: str, issue: str) -> Dict[str, Any]:
        """
        Provide comprehensive psychological support
        """
        # Start therapy session
        session = await self.therapy_bot.start_therapy_session(user_id, issue)
        
        # Get coping strategies
        coping_strategies = await self.therapy_bot.provide_coping_strategies(
            session.emotional_state, issue
        )
        
        # Generate affirmations
        affirmations = await self.therapy_bot.generate_personalized_affirmations(user_id)
        
        # Provide breathing exercise
        breathing_exercise = await self.therapy_bot.breathing_exercise_guide()
        
        return {
            "therapy_session": session,
            "coping_strategies": coping_strategies,
            "affirmations": affirmations[:3],  # Top 3 affirmations
            "breathing_exercise": breathing_exercise,
            "follow_up_needed": session.follow_up_needed,
            "emergency_resources": self.get_emergency_resources()
        }
    
    def get_emergency_resources(self) -> Dict[str, str]:
        """
        Provide emergency mental health resources
        """
        return {
            "crisis_text_line": "Text HOME to 741741",
            "suicide_prevention": "988 Suicide & Crisis Lifeline",
            "emergency_services": "911 (US) or your local emergency number",
            "online_therapy": "BetterHelp, Talkspace, or local providers",
            "support_groups": "Trading psychology support groups"
        }

# Example usage
async def main():
    """
    Example implementation of Psychology & Therapy Hub
    """
    config = {
        "openai_key": "your-openai-key",
        "anthropic_key": "your-anthropic-key",
        "google_key": "your-google-key"
    }
    
    therapy_bot = TradingTherapyBot(config)
    
    # Example therapy session
    issue = "I lost $5000 today and feel like a failure. I can't stop thinking about it."
    session = await therapy_bot.start_therapy_session("trader_456", issue)
    
    print(f"Session type: {session.session_type}")
    print(f"Emotional state: {session.emotional_state}")
    print(f"Risk level: {session.risk_level}")

if __name__ == "__main__":
    asyncio.run(main())