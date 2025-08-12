from src.ai_client import AIClient

def test_tweet_generation():
    ai_client = AIClient()
    tweet = ai_client.generate_tweet()
    
    if tweet:
        print("\nGenerated tweet:")
        print("-" * 50)
        print(tweet)
        print("-" * 50)
        print(f"Character count: {len(tweet)}")
    else:
        print("Failed to generate tweet")

if __name__ == "__main__":
    test_tweet_generation()