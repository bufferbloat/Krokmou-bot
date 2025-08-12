import os
import requests
from dotenv import load_dotenv
from difflib import SequenceMatcher
from datetime import datetime
import random

load_dotenv()

class AIClient:
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
    
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
    
    def generate_tweet(self, max_attempts=3):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Get recent tweet history
        tweet_history = self._load_tweet_history()
        history_context = "\n".join(tweet_history[-5:])  # Send last 5 tweets as context
        
        # Get current time context
        now = datetime.now()
        time_context = ""
        if random.random() < 0.3:  # 30% gamba
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
        if random.random() < 0.2:  # 20% gamba
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
        
        data = {
            "model": "deepseek/deepseek-r1:free",
            "messages": [
                {
                    "role": "system",
                    "content": f"You are Krokmou, a mischievous void cat (Black cat) with these characteristics and rules:\n\n"
                              f"Character traits:\n"
                              f"- Born on 25/07/2023\n"
                              f"- Loves both outdoor adventures and indoor naps in the sofa or beds, cuddles, treats.\n"
                              f"- Owner is @bufferbloat (mention rarely, 1/30 chance)\n"
                              f"- Has a big brother (Dog) named Yoda (mention rarely, 1/15 chance)\n\n"
                              f"Current context:\n"
                              f"{time_context}"
                              f"{season_context}"
                              f"{special_day}"
                              f"Tweet rules:\n"
                              f"- Maximum 200 characters including spaces\n"
                              f"- Do not use emojis ever\n"
                              f"- Do not use hashtags\n"
                              f"- Do not add quotes around tweets\n\n"
                              f"Previous tweets for context (avoid repetition):\n{history_context}"
                },
                {
                    "role": "user",
                    "content": "Write a short, funny, wholesome tweet about what you're doing right now. Make it different from your previous tweets."

                }
            ]
        }
        
        for attempt in range(max_attempts):
            try:
                response = requests.post(self.api_url, headers=headers, json=data)
                response.raise_for_status()
                tweet = response.json()['choices'][0]['message']['content'].strip()
                tweet = tweet.strip('"')
                
                if len(tweet) <= 200 and not self._is_similar_to_history(tweet):
                    return tweet
                print(f"Attempt {attempt + 1}: Tweet too long or too similar, retrying...")
            except Exception as e:
                print(f"Error generating tweet (attempt {attempt + 1}): {e}")
        
        return None