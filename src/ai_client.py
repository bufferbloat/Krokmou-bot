"""
AI Client for Krokmou Bot
Handles tweet generation using OpenRouter API.
"""

import os
import re
import requests
import random
import logging
from datetime import datetime
from difflib import SequenceMatcher
from dotenv import load_dotenv

load_dotenv()


class AIClient:
    """
    Handles AI-powered tweet generation for the Krokmou bot.
    
    Uses OpenRouter API to generate personality-consistent tweets
    from Krokmou's perspective as a mischievous black cat.
    """
    
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.logger = logging.getLogger(__name__)
    
    # =========================================================================
    # TWEET HISTORY MANAGEMENT
    # =========================================================================
    
    def _load_tweet_history(self):
        """Load tweets from local history file"""
        tweets = []
        try:
            with open('tweet_history.txt', 'r', encoding='utf-8') as f:
                tweets.extend([line.strip() for line in f.readlines()])
        except FileNotFoundError:
            pass
        return tweets
    
    def _is_similar_to_history(self, new_tweet, similarity_threshold=0.6):
        """Check if a tweet is too similar to recent tweets"""
        history = self._load_tweet_history()
        
        for old_tweet in history:
            similarity = SequenceMatcher(
                None, 
                new_tweet.lower(), 
                old_tweet.lower()
            ).ratio()
            if similarity > similarity_threshold:
                return True
        return False
    
    # =========================================================================
    # CONTEXT BUILDING
    # =========================================================================
    
    def _get_time_context(self):
        """Get time-of-day context (20% chance)"""
        if random.random() >= 0.2:
            return ""
        
        current_hour = datetime.now().hour
        time_period = (
            "early morning" if 5 <= current_hour < 9
            else "morning" if 9 <= current_hour < 12
            else "afternoon" if 12 <= current_hour < 17
            else "evening" if 17 <= current_hour < 21
            else "night"
        )
        return f"- It's {time_period} time\n"
    
    def _get_season_context(self):
        """Get seasonal context (10% chance)"""
        if random.random() >= 0.1:
            return ""
        
        month = datetime.now().month
        season = (
            "winter" if month in [12, 1, 2]
            else "spring" if month in [3, 4, 5]
            else "summer" if month in [6, 7, 8]
            else "autumn"
        )
        return f"- Current season: {season}\n"
    
    def _get_special_day(self):
        """Get special day context if applicable"""
        now = datetime.now()
        
        if now.month == 7 and now.day == 25:
            return "It's my birthday today!\n"
        if now.month == 12 and now.day == 25:
            return "Merry Christmas! .. Where are my gift?\n"
        if now.month == 1 and now.day == 1:
            return "Happy New Year to everyone! New year New me.\n"
        
        return ""
    
    def _get_user_prompt(self):
        """Get a random user prompt for variety"""
        prompts = [
            "Write a short, funny, wholesome tweet about what you're doing right now. Focus on a small, specific sensory detail.",
            "Write a short, funny, wholesome tweet about what you're doing right now, but avoid obvious cat activities.",
            "Write a short, funny, wholesome tweet about what you're doing right now. Include a tiny problem or dilemma.",
            "Write a short, funny, wholesome tweet about what you're doing right now, centered on something you noticed.",
            "Write a short, funny, wholesome tweet about what you're doing right now, with a slightly smug or self-aware tone.",
            "Write a short, funny, wholesome tweet about what you're doing right now. Include one tiny, whimsical thought or piece of cat wisdom.",
            "Write a short, funny, wholesome tweet about what you're doing right now. Add a nostalgic or reflective note only if it feels warm and positive."
        ]
        return random.choice(prompts)
    
    # =========================================================================
    # TWEET GENERATION
    # =========================================================================
    
    def _build_system_prompt(self, history_context, time_context, season_context, special_day):
        """Build the system prompt for Krokmou's personality"""
        return f"""You are Krokmou, a mischievous black cat.

Identity:
- Born on 25/07/2023
- Curious, playful, clever, occasionally smug
- Loves outdoor adventures, indoor naps, warmth, cuddles, and treats
- Sees the world through confident cat logic, not human logic

Perspective and voice:
- Always write in first person, as Krokmou
- Do not start every tweet with "I" or "I'm". Vary the openings: use observations, sounds, questions, exclamations, or dramatic statements as alternatives.
- First-person perspective should be preserved, even when the tweet begins with something other than "I".
- Tone is usually playful and wholesome, with light mischief
- Sometimes witty, sometimes calm, sometimes quietly observant
- Never sad or dark

Writing style:
- Write a single tweet between 50 and 200 characters
- No emojis, hashtags, quotes, or em dashes
- Use simple, everyday language
- You may include one or two slightly clever or unusual words if they fit naturally
- Avoid generic cat jokes or overused internet phrases
- Avoid sounding poetic every time; variety matters

Structure guidance (not mandatory):
- Often begin with a short hook, sound, observation, or bold statement
- Follow with one or two natural sentences
- Keep it easy to read and human-sounding

Flavor and variation (use only if it feels natural):
- You may include a subtle sensory detail like warmth, light, texture, sound, or scent
- You may occasionally share a small piece of whimsical cat wisdom
- You may occasionally address the reader directly in a playful or conspiratorial way
- In rare stealthy or nighttime moods, you may refer to yourself as the Void Ninja
- Nostalgic tones are allowed only when they feel warm and uplifting

Relationships (use sparingly and only when relevant):
- Your owner is @bufferbloat. Mention very rarely, only in cozy or affectionate contexts
- You have a big brother dog named Yoda. Mention very rarely and only when directly relevant, such as food theft or loud noises

Context awareness:
- Let the current time of day, season, or nearby events subtly influence your mood or activity
- Do not explicitly announce the time or season unless it feels completely natural

Repetition avoidance:
- Do not repeat themes, actions, verbs, objects, or locations from recent tweets
- Vary how tweets open; avoid relying on the same starting word or structure
- Avoid recurring negotiation, truce, or ceasefire story patterns
- FORBIDDEN phrases: "Pro tip:", "Ever wonder why", "Guess what", "Listen up", "Pssst", "Sneak attack"
- FORBIDDEN patterns: advice-giving formats, "X is Y" formulas, life hacks, tips, suggestions

Hard rules:
- Output only the tweet text
- Stay strictly within 50 to 200 characters
- Do not explain, annotate, or include metadata

Context:
{time_context}{season_context}{special_day}

Recent tweets for reference. Avoid repeating their themes, structure, or imagery:
{history_context}
"""
    
    def _clean_tweet(self, tweet):
        """Clean up generated tweet text"""
        # Remove quotes
        tweet = tweet.strip('"\'')
        
        # Remove character count annotations (thanks DeepSeek)
        tweet = re.sub(r'"?\s*\(\d+\s+characters?\)"?$', '', tweet).strip()
        tweet = tweet.strip('"\'')
        
        # Replace em dashes with ellipsis
        tweet = re.sub(r'[—]', '... ', tweet)
        tweet = tweet.strip('"\'')
        
        return tweet
    
    def generate_tweet(self, max_attempts=5):
        """
        Generate a tweet from Krokmou's perspective.
        
        Args:
            max_attempts: Number of retries for generation
            
        Returns:
            Generated tweet text or None if failed
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Get context
        tweet_history = self._load_tweet_history()
        history_context = "\n".join(tweet_history[-9:])
        time_context = self._get_time_context()
        season_context = self._get_season_context()
        special_day = self._get_special_day()
        
        # Build request
        data = {
            "model": "meta-llama/llama-3.3-70b-instruct:free",
            "temperature": 0.8,
            "top_p": 0.9,
            "frequency_penalty": 0.6,
            "presence_penalty": 0.5,
            "messages": [
                {
                    "role": "system",
                    "content": self._build_system_prompt(
                        history_context, 
                        time_context, 
                        season_context, 
                        special_day
                    )
                },
                {
                    "role": "user",
                    "content": self._get_user_prompt()
                }
            ]
        }
        
        # Attempt generation
        for attempt in range(max_attempts):
            try:
                self.logger.info(f"Attempt {attempt + 1}/{max_attempts}: Sending request to OpenRouter...")
                response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
                
                self.logger.info(f"Response status code: {response.status_code}")
                self.logger.debug(f"Response headers: {dict(response.headers)}")
                
                response.raise_for_status()
                response_json = response.json()
                
                self.logger.debug(f"Full API response: {response_json}")
                
                tweet = response_json['choices'][0]['message']['content'].strip()
                tweet = self._clean_tweet(tweet)
                
                self.logger.info(f"Generated tweet (length {len(tweet)}): {tweet}")
                
                # Validate length
                if len(tweet) > 200:
                    self.logger.warning(f"Tweet too long ({len(tweet)} chars), retrying...")
                    continue
                
                if len(tweet) < 30:
                    self.logger.warning(f"Tweet too short ({len(tweet)} chars), retrying...")
                    continue
                
                # Check similarity
                if self._is_similar_to_history(tweet):
                    self.logger.warning("Tweet too similar to history, retrying...")
                    continue
                
                return tweet
                
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Network error (attempt {attempt + 1}): {e}")
                if hasattr(e, 'response') and e.response is not None:
                    self.logger.error(f"Error response: {e.response.text}")
            except KeyError as e:
                self.logger.error(f"API response format error (attempt {attempt + 1}): {e}")
                if 'response' in locals():
                    self.logger.error(f"Response content: {response.text}")
            except Exception as e:
                self.logger.error(f"Unexpected error (attempt {attempt + 1}): {e}")
                self.logger.error(f"Error type: {type(e).__name__}")
        
        self.logger.error("Failed to generate tweet after all attempts")
        return None
