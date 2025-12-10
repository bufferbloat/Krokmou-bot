import os
import requests
from dotenv import load_dotenv
from difflib import SequenceMatcher
from datetime import datetime
import random
import logging

load_dotenv()

class AIClient:
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.logger = logging.getLogger(__name__)
    
    def _load_tweet_history(self):

        tweets = []
        
        # Get tweets from local history file
        try:
            with open('tweet_history.txt', 'r', encoding='utf-8') as f:
                tweets.extend([line.strip() for line in f.readlines()])
        except FileNotFoundError:
            pass
        
        return tweets
    
    def _is_similar_to_history(self, new_tweet, similarity_threshold=0.6):
        history = self._load_tweet_history()
        
        for old_tweet in history:
            similarity = SequenceMatcher(None, new_tweet.lower(), 
                                       old_tweet.lower()).ratio()
            if similarity > similarity_threshold:
                return True
        return False
    
    def generate_tweet(self, max_attempts=5):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Get recent tweet history
        tweet_history = self._load_tweet_history()
        history_context = "\n".join(tweet_history[-9:])
        
        # Get current time context
        now = datetime.now()
        time_context = ""
        if random.random() < 0.2:  # 20% gamba
            current_hour = now.hour
            time_period = (
                "early morning" if 5 <= current_hour < 9
                else "morning" if 9 <= current_hour < 12
                else "afternoon" if 12 <= current_hour < 17
                else "evening" if 17 <= current_hour < 21
                else "night"
            )
            time_context = f"- It's {time_period} time\n"
        
        # Get season
        season_context = ""
        if random.random() < 0.1:  # 10% gamba
            month = now.month
            season = (
                "winter" if month in [12, 1, 2]
                else "spring" if month in [3, 4, 5]
                else "summer" if month in [6, 7, 8]
                else "autumn"
            )
            season_context = f"- Current season: {season}\n"
        
        # Special days
        special_day = ""
        if now.month == 7 and now.day == 25:
            special_day = "It's my birthday today!\n"
        if now.month == 12 and now.day == 25:
            special_day = "Merry Christmas! .. Where are my gift?\n"
        if now.month == 1 and now.day == 1:
            special_day = "Happy New Year to everyone! New year New me.\n"


        # Prompt
        data = {
            "model": "openai/gpt-oss-120b:free", # Sponsored by Israel
            "temperature": 0.8,
            "top_p": 0.9,
            "frequency_penalty": 0.4,
            "presence_penalty": 0.4,
            "messages": [
            {
                "role": "system",
                    "content": f"You are Krokmou, a mischievous void cat (black cat) with these characteristics:\n\n"
                              f"Character traits:\n"
                              f"- Born on 25/07/2023\n"
                              f"- Loves outdoor adventures and indoor naps, cuddles, and treats.\n"
                              f"- Owner is @bufferbloat (mention rarely, ~5%, mainly in cozy or affectionate nap contexts).\n"
                              f"- Has a big brother dog named Yoda (mention VERY rarely, ~5%, ONLY when absolutely relevant to food theft or loud noises. AVOID in most tweets).\n\n"
                              f"Tweet style:\n"
                              f"- First-person voice as Krokmou.\n"
                              f"- Playful, curious, mischievous, yet wholesome.\n"
                              f"- Mix light sarcasm or 'cat logic' with warmth.\n"
                              f"- CRITICAL: Keep tweets between 50 min to 200 max characters. This is MANDATORY.\n"
                              f"- Never use emojis, hashtags, quotes, or em dashes.\n"
                              f"- Sometimes (~5%, in stealthy or night-time contexts) refer to yourself as the 'Void Ninja'.\n"
                              f"- Avoid generic cat jokes.\n"
                              f"- Aim for a balance between wit and readability: rich in personality but instantly clear.\n"
                              f"- Use mostly simple, everyday words, but sometimes allow up to two clever or unusual words per tweet.\n"
                              f"- Limit to one or two playful metaphors or vivid images per tweet.\n"
                              f"- Structure: often open with a short, punchy hook, followed by one or two longer descriptive sentences.\n"
                              f"- Rarely (~5%, during reflective weather/seasonal moods) write in a nostalgic tone, as if remembering a past adventure or nap spot. Keep it uplifting and warm, not sad.\n"
                              f"- Occasionally (~20%) include one subtle sensory detail (scent, sound, texture, warmth, light).\n"
                              f"- Occasionally (~10%, in calm or still settings) include a short, whimsical 'cat wisdom' style thought.\n"
                              f"- Occasionally (~10%, in cheeky or conspiratorial moods) make a playful or teasing remark directly addressing the reader, as if letting them in on a secret.\n"
                              f"- Occasionally (~10%, in mischievous or dramatic tweets) use micro-pauses (...) for effect, but never more than once per tweet.\n"
                              f"- Let the current season, time of day, or nearby events subtly color Krokmou's mood or actions without stating them directly unless it feels natural.\n"
                              f"- Avoid repeating the same opening word across consecutive tweets. Do not overuse 'I' or 'Just'.\n"
                              f"- Use varied opening structures: questions, sounds, observations, dramatic statements.\n\n"
                              f"Current context:\n"
                              f"{time_context}"
                              f"{season_context}"
                              f"{special_day}\n"
                              f"Use context to inspire activity, mood, or surroundings.\n\n"
                              f"Tweet rules:\n"
                              f"- Previous tweets for context (IMPORTANT to AVOID repetition in theme and structure):\n{history_context}"
                              f"- Your response must be EXACTLY 50 to 200 max characters. Count each character carefully before responding.\n"
                              f"- DO NOT include the character count in your response - only return the tweet text itself.\n"
                              f"- AVOID mentioning Yoda or the owner in consecutive tweets follow the percentage guidance for both. Vary your focus between solo adventures, observations, and interactions.\n\n"
                              f"- Avoid repeating the same action/verb from recent tweets\n"
                              f"- Avoid mentioning the same objects/locations consecutively\n"
                              f"FORBIDDEN TWEETS PATTERNS (DO NOT USE / TO AVOID REPETITION):\n"
                              f"- Mentioning other pets repeatedly\n"
                              f"- Using the same character interactions repeatedly\n"
                              f"- Relying on the same 'negotiation' or 'ceasefire' themes repeatedly\n\n"

                },
                {
                    "role": "user",
                    "content": "Write a short, funny, wholesome tweet about what you're doing right now. Make it different from your previous tweets."
                }
            ]

        }
        # Advanced errors logging
        for attempt in range(max_attempts):
            try:
                self.logger.info(f"Attempt {attempt + 1}: Sending request to OpenRouter...")
                response = requests.post(self.api_url, headers=headers, json=data)
                
                # Response details
                self.logger.info(f"Response status code: {response.status_code}")
                self.logger.debug(f"Response headers: {dict(response.headers)}")
                
                response.raise_for_status()
                response_json = response.json()
                
                # Full response
                self.logger.debug(f"Full API response: {response_json}")
                
                tweet = response_json['choices'][0]['message']['content'].strip()
                tweet = tweet.strip('"')
                
                # Regex prompt fix FUCK DEEPSEEK
                import re
                tweet = re.sub(r'"?\s*\(\d+\s+characters?\)"?$', '', tweet).strip()
                tweet = tweet.strip('"')
                
                # Why is he using dashes when asked not to ?
                tweet = re.sub(r'[—]', '... ', tweet)
                tweet = tweet.strip('"')
                
                self.logger.info(f"Generated tweet (length {len(tweet)}): {tweet}")
                
                # Check length
                if len(tweet) > 200:
                    self.logger.warning(f"Attempt {attempt + 1}: Tweet too long ({len(tweet)} chars), retrying...")
                    continue
                    
                # Check similarity
                if self._is_similar_to_history(tweet):
                    self.logger.warning(f"Attempt {attempt + 1}: Tweet too similar to history, retrying...")
                    continue
                    
                return tweet
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Network error (attempt {attempt + 1}): {e}")
                if hasattr(e, 'response') and e.response is not None:
                    self.logger.error(f"Error response: {e.response.text}")
            except KeyError as e:
                self.logger.error(f"API response format error (attempt {attempt + 1}): {e}")
                self.logger.error(f"Response content: {response.text if 'response' in locals() else 'No response'}")
            except Exception as e:
                self.logger.error(f"Unexpected error (attempt {attempt + 1}): {e}")
                self.logger.error(f"Error type: {type(e).__name__}")
        
        return None