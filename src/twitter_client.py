import os
import tweepy
import logging
from dotenv import load_dotenv

load_dotenv()

class TwitterClient:
    def __init__(self):
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        self.client = self._setup_client()
        self.user_id = os.getenv('TWITTER_USER_ID')
        self.logger = logging.getLogger(__name__)
    
    def _setup_client(self):
        client = tweepy.Client(
            consumer_key=self.api_key,
            consumer_secret=self.api_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret
        )
        return client
    
    def get_recent_tweets(self, limit=30):
        try:
            tweets = self.client.get_users_tweets(
                id=self.user_id,
                max_results=limit,
                tweet_fields=['text', 'created_at']
            )
            return [tweet.text for tweet in tweets.data] if tweets.data else []
        except Exception as e:
            print(f"Error fetching tweets: {e}")
            return []
    
    def post_tweet(self, text):
        try:
            response = self.client.create_tweet(text=text)
            tweet_id = response.data['id']
            tweet_url = f"https://twitter.com/KrokmouVoid/status/{tweet_id}"
            print(f"Tweet URL: {tweet_url}")
            # Save to history file
            self._save_tweet_to_history(text)
            return tweet_url
        except Exception as e:
            print(f"Error posting tweet: {e}")
            return False
    
    def _save_tweet_to_history(self, text):
        with open('tweet_history.txt', 'a', encoding='utf-8') as f:
            f.write(f"{text}\n")