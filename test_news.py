"""
Test script for Krokmou Bot - News Awareness Feature
Tests the NewsClient functionality.
"""

from src.news_client import NewsClient
import json


def test_news_fetch():
    """Test fetching and filtering news headlines"""
    print("\n" + "="*60)
    print("TESTING NEWS FETCH")
    print("="*60)
    
    news = NewsClient()
    
    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
    news_config = config.get("news_awareness", {})
    
    print(f"\nConfig: {json.dumps(news_config, indent=2)}")
    
    # Fetch headlines
    print("\nFetching headlines...")
    articles = news._fetch(news_config)
    
    print(f"\nFetched {len(articles)} articles")
    
    if articles:
        print("\nTop 5 headlines:")
        for i, article in enumerate(articles[:5]):
            title = article.get('title', 'No title')[:80]
            category = article.get('_category', 'unknown')
            print(f"  {i+1}. [{category}] {title}")
    
    return articles


def test_headline_selection():
    """Test selecting the best newsworthy headline"""
    print("\n" + "="*60)
    print("TESTING HEADLINE SELECTION")
    print("="*60)
    
    news = NewsClient()
    
    with open('config.json', 'r') as f:
        config = json.load(f)
    news_config = config.get("news_awareness", {})
    
    result = news.get_headline(news_config)
    
    if result:
        headline, description, keywords = result
        print(f"\nSelected headline: {headline}")
        print(f"Description: {description[:150]}..." if description else "No description")
        print(f"Keywords: {keywords}")
    else:
        print("\nNo suitable headline found")
    
    return result


def test_news_tweet_generation():
    """Test generating a cat-perspective news tweet"""
    print("\n" + "="*60)
    print("TESTING NEWS TWEET GENERATION")
    print("="*60)
    
    news = NewsClient()
    
    with open('config.json', 'r') as f:
        config = json.load(f)
    news_config = config.get("news_awareness", {})
    
    # Get a headline
    result = news.get_headline(news_config)
    
    if not result:
        print("\nNo headline found, using test headline")
        headline = "SpaceX launches largest rocket ever built into orbit"
        description = "Elon Musk's SpaceX successfully launched its Starship rocket, the most powerful ever built."
    else:
        headline, description, keywords = result
        print(f"\nUsing real headline: {headline}")
    
    # Generate tweet
    print("\nGenerating news tweet...")
    tweet = news.generate_news_tweet(headline, description)
    
    if tweet:
        print("\n" + "-"*50)
        print(tweet)
        print("-"*50)
        print(f"Character count: {len(tweet)}")
    else:
        print("Failed to generate news tweet")
    
    return tweet


def test_news_history():
    """Test news history tracking"""
    print("\n" + "="*60)
    print("TESTING NEWS HISTORY")
    print("="*60)
    
    news = NewsClient()
    
    # Load current history
    history = news._load_history()
    print(f"\nCurrent history: {json.dumps(history, indent=2)}")
    
    # Test keyword extraction
    test_headline = "Trump announces new tariffs on technology imports from China"
    keywords = news._extract(test_headline)
    print(f"\nExtracted keywords from: '{test_headline}'")
    print(f"Keywords: {keywords}")
    
    # Check if covered
    is_covered = news.is_covered(test_headline, keywords)
    print(f"Is topic covered: {is_covered}")
    
    # Test last tweet time and weekly count
    last_time = news.get_last_time()
    tweets_this_week = news.get_weekly_count()
    print(f"\nLast news tweet: {last_time}")
    print(f"News tweets this week: {tweets_this_week}")


def test_regular_tweet():
    """Test that regular tweet generation still works"""
    print("\n" + "="*60)
    print("TESTING REGULAR TWEET GENERATION")
    print("="*60)
    
    from src.ai_client import AIClient
    ai = AIClient()
    
    print("\nGenerating regular tweet...")
    tweet = ai.generate_tweet()
    
    if tweet:
        print("\n" + "-"*50)
        print(tweet)
        print("-"*50)
        print(f"Character count: {len(tweet)}")
    else:
        print("Failed to generate regular tweet")
    
    return tweet


if __name__ == "__main__":
    print("\n" + "#"*60)
    print("# KROKMOU BOT - NEWS AWARENESS TEST")
    print("#"*60)
    
    # Run tests
    test_news_fetch()
    test_headline_selection()
    test_news_tweet_generation()
    test_news_history()
    test_regular_tweet()
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60 + "\n")
