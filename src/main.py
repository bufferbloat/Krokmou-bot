import os
import time
import schedule
import pytz
import logging
from datetime import datetime
from dotenv import load_dotenv
from ai_client import AIClient
from twitter_client import TwitterClient

load_dotenv()

# Log
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler('krokmou_bot.log')  # File output
    ]
)
logger = logging.getLogger(__name__)

def post_tweet():
    logger.info("Starting tweet generation and posting process")
    try:
        ai = AIClient()
        twitter = TwitterClient()
        
        logger.info("Generating tweet")
        tweet_text = ai.generate_tweet()
        
        if tweet_text:
            logger.info(f"Generated tweet: {tweet_text}")
            logger.info("Attempting to post tweet")
            twitter.post_tweet(tweet_text)
            logger.info("Tweet successfully posted")
        else:
            logger.error("Failed to generate tweet text")
    except Exception as e:
        logger.error(f"Error in post_tweet: {str(e)}")

def main():
    # Get configured timezone
    timezone = os.getenv('TIMEZONE', 'Europe/Paris')
    logger.info(f"Bot starting in timezone: {timezone}")
    
    try:
        # Schedule three daily tweets
        schedule.every().day.at("05:00").do(post_tweet)
        schedule.every().day.at("14:00").do(post_tweet)
        schedule.every().day.at("22:00").do(post_tweet)
        logger.info(f"Bot scheduled to tweet daily at 05:00, 14:00, and 22:00 {timezone}")
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    except Exception as e:
        logger.error(f"Error in main loop: {str(e)}")
        raise

if __name__ == "__main__":
    logger.info("=== Krokmou Bot Starting ===")
    main()