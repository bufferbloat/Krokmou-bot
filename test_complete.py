from src.ai_client import AIClient
from src.twitter_client import TwitterClient

def test_complete_workflow():

    ai_client = AIClient()
    twitter_client = TwitterClient()
    
    print("1. Generating tweet...")
    tweet = ai_client.generate_tweet()
    
    if not tweet:
        print("Failed to generate tweet")
        return
    
    print("\nGenerated tweet:")
    print("-" * 50)
    print(tweet)
    print("-" * 50)
    print(f"Character count: {len(tweet)}")
    
    # Ask for confirmation before posting
    response = input("\nWould you like to post this tweet? (yes/no): ")
    
    if response.lower() == 'yes':
        print("\n2. Posting tweet...")
        result = twitter_client.post_tweet(tweet)
        
        if result:
            print("✓ Tweet posted successfully!")
        else:
            print("× Failed to post tweet")
    else:
        print("Tweet posting cancelled")

if __name__ == "__main__":
    test_complete_workflow()