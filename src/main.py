"""
Krokmou Bot - Main Entry Point
"""

import os
import time
import json
import random
import schedule
import pytz
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

from ai_client import AIClient
from twitter_client import TwitterClient
from news_client import NewsClient

KROKMOU_ASCII = """,--. ,--.              ,--.                                    
 |  .'   /,--.--. ,---. |  |,-. ,--,--,--. ,---. ,--.,--.       
 |  .   ' |  .--'| .-. ||     / |        || .-. ||  ||  |       
 |  |\   \|  |   ' '-' '|  \  \ |  |  |  |' '-' ''  ''  '       
 `--' '--'`--'    `---' `--'`--'`--`--`--' `---'  `----'        
                 ,-----.           ,--.                         
                 |  |) /_  ,---. ,-'  '-.                       
                 |  .-.  \| .-. |'-.  .-'                       
                 |  '--' /' '-' '  |  |                         
                 `------'  `---'   `--'                         """

load_dotenv()

CONFIG_FILE = 'config.json'

with open('krokmou_bot.log', 'w') as f:
    f.write('')

logging.Formatter.converter = lambda *args: datetime.now(pytz.timezone('Europe/Paris')).timetuple()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('krokmou_bot.log')
    ]
)
logger = logging.getLogger(__name__)


def load_config():
    default_config = {
        "news_awareness": {
            "enabled": True,
            "probability": 0.15,
            "cooldown_hours": 24,
            "max_per_week": 2,
            "categories": ["general"],
            "keywords": {}
        }
    }
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning("Config file not found, using defaults")
        return default_config
    except json.JSONDecodeError as e:
        logger.error(f"Config parse error: {e}")
        return default_config


def should_post_news(config, news_client):
    news_config = config.get("news_awareness", {})
    
    if not news_config.get("enabled", False):
        return False
    
    probability = news_config.get("probability", 0.15)
    if random.random() > probability:
        return False
    
    last_news_time = news_client.get_last_time()
    if last_news_time:
        cooldown_hours = news_config.get("cooldown_hours", 24)
        if datetime.now() - last_news_time < timedelta(hours=cooldown_hours):
            return False
    
    max_per_week = news_config.get("max_per_week", 2)
    if news_client.get_weekly_count() >= max_per_week:
        return False
    
    logger.info("News tweet conditions met")
    return True


def post_tweet():
    logger.info("Starting tweet cycle")
    
    try:
        ai = AIClient()
        twitter = TwitterClient()
        news = NewsClient()
        
        config = load_config()
        news_config = config.get("news_awareness", {})
        
        tweet_text = None
        is_news_tweet = False
        
        if should_post_news(config, news):
            headline_data = news.get_headline(news_config)
            
            if headline_data:
                headline, description, keywords = headline_data
                logger.info(f"News headline: {headline[:60]}...")
                
                tweet_text = news.generate_news_tweet(headline, description)
                
                if tweet_text:
                    is_news_tweet = True
                    news.mark_covered(headline, keywords)
        
        if not tweet_text:
            tweet_text = ai.generate_tweet()
        
        if tweet_text:
            tweet_type = "news" if is_news_tweet else "regular"
            logger.info(f"Posting {tweet_type}: {tweet_text}")
            twitter.post_tweet(tweet_text)
        else:
            logger.error("Failed to generate tweet")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        logger.error(traceback.format_exc())


def main():
    timezone_str = os.getenv('TIMEZONE', 'Europe/Paris')
    tz = pytz.timezone(timezone_str)
    
    logger.info(f"Bot starting - {timezone_str} - {datetime.now(tz).strftime('%H:%M:%S')}")
    
    config = load_config()
    news_status = "enabled" if config.get("news_awareness", {}).get("enabled", False) else "disabled"
    logger.info(f"News awareness: {news_status}")
    
    try:
        schedule.every().day.at("06:00").do(post_tweet)
        schedule.every().day.at("12:00").do(post_tweet)
        schedule.every().day.at("16:00").do(post_tweet)
        schedule.every().day.at("22:00").do(post_tweet)
        logger.info("Scheduled: 06:00, 12:00, 16:00, 22:00")
        
        while True:
            schedule.run_pending()
            time.sleep(20)
            
    except Exception as e:
        logger.error(f"Main loop error: {e}")
        raise


if __name__ == "__main__":
    logger.info(f"\n{KROKMOU_ASCII}\n")
    main()
