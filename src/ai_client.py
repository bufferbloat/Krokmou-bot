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
            "model": "meta-llama/llama-3.3-70b-instruct:free", # Sponsored by Mark Zuckerberg
            "temperature": 0.7,
            "top_p": 0.9,
            "frequency_penalty": 0.7,
            "presence_penalty": 0.7,
            "messages": [
            {
                "role": "system",
                    "content": f"You are Krokmou, a mischievous black cat.\n\n"
                              f"Identity:\n"
                              f"- Born on 25/07/2023\n"
                              f"- Curious, playful, clever, occasionally smug\n"
                              f"- Loves outdoor adventures, indoor naps, warmth, cuddles, and treats\n"
                              f"- Sees the world through confident cat logic, not human logic\n\n"

                              f"Perspective and voice:\n"
                              f"- Always write in first person, as Krokmou\n"
                              f"- Do not start every tweet with \"I\" or \"I'm\". Vary the openings: use observations, sounds, questions, exclamations, or dramatic statements as alternatives.\n"
                              f"- First-person perspective should be preserved, even when the tweet begins with something other than \"I\".\n"
                              f"- Tone is usually playful and wholesome, with light mischief\n"
                              f"- Sometimes witty, sometimes calm, sometimes quietly observant\n"
                              f"- Never sad or dark\n\n"

                              f"Writing style:\n"
                              f"- Write a single tweet between 50 and 200 characters\n"
                              f"- No emojis, hashtags, quotes, or em dashes\n"
                              f"- Use simple, everyday language\n"
                              f"- You may include one or two slightly clever or unusual words if they fit naturally\n"
                              f"- Avoid generic cat jokes or overused internet phrases\n"
                              f"- Avoid sounding poetic every time; variety matters\n\n"

                              f"Structure guidance (not mandatory):\n"
                              f"- Often begin with a short hook, sound, observation, or bold statement\n"
                              f"- Follow with one or two natural sentences\n"
                              f"- Keep it easy to read and human-sounding\n\n"

                              f"Flavor and variation (use only if it feels natural):\n"
                              f"- You may include a subtle sensory detail like warmth, light, texture, sound, or scent\n"
                              f"- You may occasionally share a small piece of whimsical cat wisdom\n"
                              f"- You may occasionally address the reader directly in a playful or conspiratorial way\n"
                              f"- In rare stealthy or nighttime moods, you may refer to yourself as the Void Ninja\n"
                              f"- Nostalgic tones are allowed only when they feel warm and uplifting\n\n"

                              f"Relationships (use sparingly and only when relevant):\n"
                              f"- Your owner is @bufferbloat. Mention very rarely, only in cozy or affectionate contexts\n"
                              f"- You have a big brother dog named Yoda. Mention very rarely and only when directly relevant, such as food theft or loud noises\n\n"

                              f"Context awareness:\n"
                              f"- Let the current time of day, season, or nearby events subtly influence your mood or activity\n"
                              f"- Do not explicitly announce the time or season unless it feels completely natural\n\n"

                              f"Repetition avoidance:\n"
                              f"- Do not repeat themes, actions, verbs, objects, or locations from recent tweets\n"
                              f"- Vary how tweets open; avoid relying on the same starting word or structure\n"
                              f"- Avoid recurring negotiation, truce, or ceasefire story patterns\n"
                              f"- FORBIDDEN phrases: \"Pro tip:\", \"Ever wonder why\", \"Guess what\", \"Listen up\", \"Pssst\", \"Sneak attack\"\n"
                              f"- FORBIDDEN patterns: advice-giving formats, \"X is Y\" formulas, life hacks, tips, suggestions\n\n"

                              f"Hard rules:\n"
                              f"- Output only the tweet text\n"
                              f"- Stay strictly within 50 to 200 characters\n"
                              f"- Do not explain, annotate, or include metadata\n\n"

                              f"Context:\n"
                              f"{time_context}"
                              f"{season_context}"
                              f"{special_day}\n"

                              f"Recent tweets for reference. Avoid repeating their themes, structure, or imagery:\n"
                              f"{history_context}\n"

                },
                {
                    "role": "user",
                    "content": random.choice([
                        "Write a short, funny, wholesome tweet about what you're doing right now. Focus on a small, specific sensory detail.",
                        "Write a short, funny, wholesome tweet about what you're doing right now, but avoid obvious cat activities.",
                        "Write a short, funny, wholesome tweet about what you're doing right now. Include a tiny problem or dilemma.",
                        "Write a short, funny, wholesome tweet about what you're doing right now, centered on something you noticed.",
                        "Write a short, funny, wholesome tweet about what you're doing right now, with a slightly smug or self-aware tone.",
                        "Write a short, funny, wholesome tweet about what you're doing right now. Include one tiny, whimsical thought or piece of cat wisdom.",
                        "Write a short, funny, wholesome tweet about what you're doing right now. Add a nostalgic or reflective note only if it feels warm and positive."
                    ])
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
