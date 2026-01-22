import logging
import sys
import json
import os
from src.ai_client import AIClient
from src.twitter_client import TwitterClient
from src.news_client import NewsClient

def setup_logging():
    with open('test_debug.log', 'w', encoding='utf-8') as f:
        pass
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('test_debug.log', encoding='utf-8')
        ]
    )
    
    logging.getLogger('requests').setLevel(logging.DEBUG)
    logging.getLogger('urllib3').setLevel(logging.DEBUG)

def test_complete_workflow():
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("=== Starting Complete Workflow Test ===")
    
    try:
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            print("OPENROUTER_API_KEY not found!")
            return
        print(f"API key found: {api_key[:10]}...{api_key[-4:]}")
        
        twitter_client = TwitterClient()
        
        # Ask for tweet type
        print("\nWhat type of tweet do you want to generate?")
        print("1. Normal tweet")
        print("2. News tweet")
        tweet_type = input("Choose (1/2): ").strip()
        
        tweet = None
        
        if tweet_type == "2":
            # News tweet
            print("\nGenerating news tweet...")
            news_client = NewsClient()
            
            with open('config.json', 'r') as f:
                config = json.load(f)
            news_config = config.get("news_awareness", {})
            
            headline_data = news_client.get_headline(news_config)
            
            if not headline_data:
                print("No suitable news found. Falling back to normal tweet.")
                tweet_type = "1"
            else:
                headline, description, keywords = headline_data
                print(f"\nHeadline: {headline}")
                print(f"Keywords: {keywords}")
                
                tweet = news_client.generate_news_tweet(headline, description)
                
                if tweet:
                    news_client.mark_covered(headline, keywords)
        
        if tweet_type == "1" or not tweet:
            # Normal tweet
            print("\nGenerating normal tweet...")
            ai_client = AIClient()
            tweet = ai_client.generate_tweet()
        
        if not tweet:
            print("Failed to generate tweet")
            return
        
        print("\nGenerated tweet:")
        print("-" * 50)
        print(tweet)
        print("-" * 50)
        print(f"Character count: {len(tweet)}")
        
        if len(tweet) > 200:
            print(f"Warning: Tweet is {len(tweet)} characters (over 200 limit)")
        elif len(tweet) < 50:
            print(f"Warning: Tweet is {len(tweet)} characters (under 50 minimum)")
        
        response = input("\nPost this tweet? (yes/no): ")
        
        if response.lower() == 'yes':
            print("\nPosting tweet...")
            result = twitter_client.post_tweet(tweet)
            
            if result:
                print("Tweet posted successfully!")
            else:
                print("Failed to post tweet")
        else:
            print("Cancelled")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        print(f"\nError: {e}")
        print("Check test_debug.log for details")

if __name__ == "__main__":
    test_complete_workflow()
