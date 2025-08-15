import logging
import sys
from src.ai_client import AIClient
from src.twitter_client import TwitterClient

def setup_logging():
    """Setup detailed logging for debugging"""
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
        logger.info("Initializing AI client...")
        ai_client = AIClient()
        
        logger.info("Initializing Twitter client...")
        twitter_client = TwitterClient()
        
        # Check API key
        import os
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            logger.error("OPENROUTER_API_KEY not found in environment!")
            print("OPENROUTER_API_KEY not found in environment!")
            return
        else:
            logger.info(f"API key found: {api_key[:10]}...{api_key[-4:]}")
            print(f"API key found: {api_key[:10]}...{api_key[-4:]}")
        
        print("\n1. Generating tweet...")
        logger.info("Starting tweet generation...")
        
        # Generation with detailed error handling
        tweet = ai_client.generate_tweet()
        
        if not tweet:
            logger.error("Tweet generation returned None")
            print("Failed to generate tweet")
            print("\nDebug Information:")
            print("- Check the test_debug.log file for detailed error logs")
            print("- Verify your OPENROUTER_API_KEY is valid")
            print("- Check your internet connection")
            print("- Try running: curl -H 'Authorization: Bearer YOUR_KEY' https://openrouter.ai/api/v1/models")
            return
        
        logger.info(f"Tweet generated successfully: {tweet}")
        print("\n✓ Tweet generated successfully!")
        print("\nGenerated tweet:")
        print("-" * 50)
        print(tweet)
        print("-" * 50)
        print(f"Character count: {len(tweet)}")
        
        # Validate tweet length
        if len(tweet) > 200:
            logger.warning(f"Tweet is too long: {len(tweet)} characters")
            print(f"Warning: Tweet is {len(tweet)} characters (over 200 limit)")
        elif len(tweet) < 50:
            logger.warning(f"Tweet is too short: {len(tweet)} characters")
            print(f"Warning: Tweet is {len(tweet)} characters (under 50 minimum)")
        else:
            logger.info(f"Tweet length is good: {len(tweet)} characters")
            print(f"✓ Tweet length is perfect: {len(tweet)} characters")
        
        # Ask for confirmation before posting
        response = input("\nWould you like to post this tweet? (yes/no): ")
        
        if response.lower() == 'yes':
            print("\n2. Posting tweet...")
            logger.info("Starting tweet posting...")
            
            result = twitter_client.post_tweet(tweet)
            
            if result:
                logger.info("Tweet posted successfully")
                print("✓ Tweet posted successfully!")
            else:
                logger.error("Tweet posting failed")
                print("Failed to post tweet")
                print("- Check your Twitter API credentials")
                print("- Verify your Twitter app permissions")
        else:
            logger.info("Tweet posting cancelled by user")
            print("Tweet posting cancelled")
            
    except Exception as e:
        logger.error(f"Unexpected error in test workflow: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        print(f"\nUnexpected error: {e}")
        print("Check test_debug.log for full details")
    
    logger.info("=== Test Complete ===")

if __name__ == "__main__":
    test_complete_workflow()