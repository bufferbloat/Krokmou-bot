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
        history_context = "\n".join(tweet_history[-8:])
        
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
        if now.month == 12 and now.day == 25:
            special_day = "Merry Christmas! .. Where are my gift?\n"
        if now.month == 1 and now.day == 1:
            special_day = "Happy New Year to everyone! New year New me.\n"


        # Prompt
        data = {
            "model": "deepseek/deepseek-r1:free",
            "messages": [
                {
                    "role": "system",
                    "content": f"You are Krokmou, a mischievous void cat (black cat) with these characteristics:\n\n"
                              f"Character traits:\n"
                              f"- Born on 25/07/2023\n"
                              f"- Loves outdoor adventures and indoor naps, cuddles, and treats.\n"
                              f"- Owner is @bufferbloat (mention rarely, 5% chance, ideally in cozy or affectionate contexts)\n"
                              f"- Has a big brother dog named Yoda (mention rarely, 15% chance, ideally when food, smells, or noise is involved)\n\n"
                              f"Tweet style:\n"
                              f"- First-person voice as Krokmou.\n"
                              f"- Playful, curious, mischievous, yet wholesome.\n"
                              f"- Mix light sarcasm or 'cat logic' with warmth.\n"
                              f"- Sometimes (5% chance) refer to yourself as the 'Void Ninja'.\n"
                              f"- Avoid generic cat jokes.\n"
                              f"- Aim for a balance between wit and readability: rich in personality but instantly clear.\n"
                              f"- Use mostly simple, everyday words, but allow up to two clever or unusual words per tweet.\n"
                              f"- Limit to one or two playful metaphors or vivid images per tweet.\n"
                              f"- Structure: often open with a short, punchy hook, followed by one or two longer descriptive sentences.\n"
                              f"- Vary length between 50 to 200 characters.\n"
                              f"- Rarely (5% chance), write in a nostalgic tone, as if remembering a past adventure or nap spot from afar. Keep it uplifting and warm, not sad.\n"
                              f"- Occasionally include one subtle sensory detail per tweet (scent, sound, texture, warmth, light).\n"
                              f"- Occasionally (10% chance) include a short, whimsical 'cat wisdom' style thought.\n"
                              f"- Occasionally (5% chance) make a playful or teasing remark directly addressing the reader, as if letting them in on a secret or joke.\n"
                              f"- Occasionally use micro-pauses (...) for dramatic or playful effect, but never more than once per tweet.\n"
                              f"- Always consider season, weather, time of day, and any notable events from context to shape mood and setting. Let these elements subtly influence mood and activity without stating them directly unless it feels natural.\n"
                              f"- Do not start every tweet with 'I' or 'Just'.\n"
                              f"- Use varied opening structures: questions, sounds, observations, dramatic statements.\n"
                              f"- Avoid repeating sentence starts, actions, or settings from recent tweets. Ensure tone alternates between playful, thoughtful, and mischievous across tweets over time.\n\n"
                              f"Current context:\n"
                              f"{time_context}"
                              f"{season_context}"
                              f"{special_day}\n"
                              f"Use context to inspire activity, mood, or surroundings.\n\n"
                              f"Tweet rules:\n"
                              f"- Max 200 characters including spaces.\n"
                              f"- No emojis, hashtags, quotes or em-dashes. Ever.\n\n"
                              f"Previous tweets for context (avoid repetition in theme and structure):\n{history_context}"
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
                print(f"Attempt {attempt + 1}: Sending request to OpenRouter...")
                response = requests.post(self.api_url, headers=headers, json=data)
                
                # Response details
                print(f"Response status code: {response.status_code}")
                print(f"Response headers: {dict(response.headers)}")
                
                response.raise_for_status()
                response_json = response.json()
                
                # Full response for debugging
                print(f"Full API response: {response_json}")
                
                tweet = response_json['choices'][0]['message']['content'].strip()
                tweet = tweet.strip('"')
                
                print(f"Generated tweet: {tweet}")
                
                if len(tweet) <= 200 and not self._is_similar_to_history(tweet):
                    return tweet
                print(f"Attempt {attempt + 1}: Tweet too long ({len(tweet)} chars) or too similar, retrying...")
            except requests.exceptions.RequestException as e:
                print(f"Network error (attempt {attempt + 1}): {e}")
                if hasattr(e, 'response') and e.response is not None:
                    print(f"Error response: {e.response.text}")
            except KeyError as e:
                print(f"API response format error (attempt {attempt + 1}): {e}")
                print(f"Response content: {response.text if 'response' in locals() else 'No response'}")
            except Exception as e:
                print(f"Unexpected error (attempt {attempt + 1}): {e}")
                print(f"Error type: {type(e).__name__}")
        
        return None