"""
News Client for Krokmou Bot
"""

import os
import re
import json
import requests
import logging
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from dotenv import load_dotenv

load_dotenv()

NEWS_HISTORY_FILE = 'news_history.json'

STOPWORDS = {
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare',
    'ought', 'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by',
    'from', 'as', 'into', 'through', 'during', 'before', 'after', 'above',
    'below', 'between', 'under', 'again', 'further', 'then', 'once',
    'here', 'there', 'when', 'where', 'why', 'how', 'all', 'each', 'few',
    'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
    'own', 'same', 'so', 'than', 'too', 'very', 'just', 'and', 'but',
    'if', 'or', 'because', 'until', 'while', 'about', 'against', 'this',
    'that', 'these', 'those', 'what', 'which', 'who', 'whom', 'its', 'it',
    'he', 'she', 'they', 'his', 'her', 'their', 'says', 'said', 'new',
    'first', 'last', 'long', 'great', 'little', 'over', 'after', 'back',
    'also', 'made', 'make'
}


class NewsClient:
    def __init__(self):
        self.news_api_key = os.getenv('NEWSAPI_KEY')
        self.news_api_url = "https://newsapi.org/v2/top-headlines"
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        self.openrouter_api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.logger = logging.getLogger(__name__)
    
    def _load_history(self):
        try:
            with open(NEWS_HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"covered_topics": [], "last_news_tweet": None}
    
    def _save_history(self, history):
        with open(NEWS_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    
    def is_covered(self, headline, keywords):
        """Check if topic was covered in last 72h (keyword overlap or similarity)"""
        history = self._load_history()
        cutoff = datetime.now() - timedelta(hours=72)
        
        for topic in history.get("covered_topics", []):
            topic_time = datetime.fromisoformat(topic["timestamp"])
            if topic_time < cutoff:
                continue
            
            topic_keywords = set(k.lower() for k in topic.get("keywords", []))
            new_keywords = set(k.lower() for k in keywords)
            if len(topic_keywords & new_keywords) >= 2:
                return True
            
            similarity = SequenceMatcher(None, headline.lower(), topic.get("headline", "").lower()).ratio()
            if similarity > 0.6:
                return True
        
        return False
    
    def mark_covered(self, headline, keywords):
        history = self._load_history()
        
        history["covered_topics"].append({
            "headline": headline,
            "keywords": keywords,
            "timestamp": datetime.now().isoformat()
        })
        history["last_news_tweet"] = datetime.now().isoformat()
        
        cutoff = datetime.now() - timedelta(days=7)
        history["covered_topics"] = [
            t for t in history["covered_topics"]
            if datetime.fromisoformat(t["timestamp"]) > cutoff
        ]
        
        self._save_history(history)
        self.logger.info(f"Marked covered: {headline[:50]}...")
    
    def get_last_time(self):
        history = self._load_history()
        last_news = history.get("last_news_tweet")
        return datetime.fromisoformat(last_news) if last_news else None
    
    def get_weekly_count(self):
        history = self._load_history()
        cutoff = datetime.now() - timedelta(days=7)
        
        count = 0
        for topic in history.get("covered_topics", []):
            try:
                if datetime.fromisoformat(topic["timestamp"]) > cutoff:
                    count += 1
            except (KeyError, ValueError):
                continue
        return count
    
    def _extract(self, headline, description=""):
        text = f"{headline} {description}".lower()
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
        keywords = [w for w in words if w.lower() not in STOPWORDS]
        
        seen = set()
        unique = []
        for k in keywords:
            if k.lower() not in seen:
                seen.add(k.lower())
                unique.append(k)
        return unique[:10]
    
    def _fetch(self, config):
        if not self.news_api_key:
            self.logger.warning("NewsAPI key not configured")
            return []
        
        categories = config.get("categories", ["general"])
        countries = config.get("countries", ["us", "fr"])
        all_articles = []
        seen_titles = set()
        
        for country in countries:
            for category in categories:
                try:
                    params = {
                        "apiKey": self.news_api_key,
                        "country": country,
                        "category": category,
                        "pageSize": 10
                    }
                    
                    response = requests.get(self.news_api_url, params=params, timeout=10)
                    response.raise_for_status()
                    
                    for article in response.json().get("articles", []):
                        title = article.get("title", "")
                        if title not in seen_titles:
                            seen_titles.add(title)
                            article["_category"] = category
                            article["_country"] = country
                            all_articles.append(article)
                    
                except requests.exceptions.RequestException as e:
                    self.logger.error(f"Fetch error {country}/{category}: {e}")
                except Exception as e:
                    self.logger.error(f"Unexpected fetch error: {e}")
        
        self.logger.debug(f"Fetched {len(all_articles)} articles")
        return all_articles
    
    def _has_keyword(self, article, keywords_config):
        if not keywords_config:
            return True
        
        headline = article.get("title", "").lower()
        description = (article.get("description") or "").lower()
        text = f"{headline} {description}"
        
        for keyword in keywords_config.keys():
            if self._matches(keyword, text, keywords_config):
                return True
        return False
    
    def _matches(self, keyword, text, keywords_config):
        keyword_lower = keyword.lower()
        
        if keyword_lower in keywords_config:
            for alias in keywords_config[keyword_lower].get("aliases", []):
                if alias.lower() in text:
                    return True
            return False
        return keyword_lower in text
    
    def _score(self, article, keywords_config):
        score = 0
        headline = article.get("title", "").lower()
        description = (article.get("description") or "").lower()
        text = f"{headline} {description}"
        
        for keyword, data in keywords_config.items():
            if self._matches(keyword, text, keywords_config):
                score += data.get("points", 0)
        return score
    
    def get_headline(self, config):
        articles = self._fetch(config)
        if not articles:
            return None
        
        keywords_config = config.get("keywords", {})
        scored = []
        
        for article in articles:
            headline = article.get("title", "")
            description = article.get("description") or ""
            
            if not headline or "[Removed]" in headline or "[Removed]" in description:
                continue
            
            if not self._has_keyword(article, keywords_config):
                continue
            
            keywords = self._extract(headline, description)
            if self.is_covered(headline, keywords):
                continue
            
            score = self._score(article, keywords_config)
            scored.append((score, headline, description, keywords))
        
        if not scored:
            self.logger.debug("No suitable headlines found")
            return None
        
        scored.sort(key=lambda x: x[0], reverse=True)
        
        min_score = config.get("min_score", 10)
        top_score = scored[0][0]
        
        if top_score < min_score:
            self.logger.debug(f"Top score {top_score} below threshold {min_score}")
            return None
        
        _, headline, description, keywords = scored[0]
        self.logger.info(f"Selected (score {top_score}): {headline[:60]}...")
        return (headline, description, keywords)
    
    def _load_tweets(self):
        try:
            with open('tweet_history.txt', 'r', encoding='utf-8') as f:
                return [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            return []
    
    def _is_similar(self, new_tweet, threshold=0.6):
        for old_tweet in self._load_tweets():
            if SequenceMatcher(None, new_tweet.lower(), old_tweet.lower()).ratio() > threshold:
                return True
        return False
    
    def generate_news_tweet(self, headline, description, max_attempts=5):
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json"
        }
        
        history_context = "\n".join(self._load_tweets()[-5:])
        system_prompt = self._build_prompt(headline, description, history_context)
        
        data = {
            "model": "meta-llama/llama-3.3-70b-instruct:free",
            "temperature": 0.8,
            "top_p": 0.9,
            "frequency_penalty": 0.7,
            "presence_penalty": 0.7,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Write a funny tweet about this news. Be SPECIFIC - mention the subject by name. React as Krokmou the cat."}
            ]
        }
        
        for attempt in range(max_attempts):
            try:
                response = requests.post(self.openrouter_api_url, headers=headers, json=data, timeout=30)
                response.raise_for_status()
                
                tweet = response.json()['choices'][0]['message']['content'].strip()
                tweet = self._clean_tweet(tweet)
                
                if len(tweet) > 200 or len(tweet) < 30:
                    self.logger.debug(f"Invalid length ({len(tweet)}), retry {attempt + 1}")
                    continue
                
                if self._is_similar(tweet):
                    self.logger.debug(f"Too similar, retry {attempt + 1}")
                    continue
                
                self.logger.info(f"Generated: {tweet}")
                return tweet
                
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Network error: {e}")
            except (KeyError, Exception) as e:
                self.logger.error(f"Generation error: {e}")
        
        self.logger.error("Failed to generate news tweet")
        return None
    
    def _build_prompt(self, headline, description, history_context):
        return f"""You are Krokmou, a mischievous black cat tweeting about real-world news.

NEWS TO REACT TO:
Headline: "{headline}"
Details: {description}

IMPORTANT - BE DIRECT AND SPECIFIC:
- Mention the actual subject by name (Trump, Macron, Nvidia, SpaceX, etc.)
- Make it clear what the news is about
- React from a cat's perspective but be specific about the topic
- Your owner is a tech enthusiast, so tech/GPU news affects them directly

REACTION STYLE:
- You are Krokmou, a cat who sees human news through cat logic
- Be playful, witty, and sometimes sarcastic
- Connect the news to cat life or your owner's life when relevant
- Keep it funny and lighthearted, avoid being preachy

GOOD EXAMPLES:
- "Trump did WHAT now? Humans and their territory disputes. At least when I fight for the sunny spot, nobody writes articles about it."
- "Nvidia prices going up again. Great, my owner will be crying into my fur instead of buying me treats."
- "Macron said something and now everyone is yelling. I said meow once and got the same reaction. Politics is just loud meowing."
- "SpaceX launched another rocket. Very loud. Very rude. Some of us are trying to nap."
- "Another war update. Humans really need to learn from cats... we just hiss and move on."

BAD EXAMPLES (too vague):
- "Humans are being weird again" (doesn't mention the subject)
- "Something happened in the world" (too generic)
- "The news is confusing" (doesn't react to the actual topic)

WRITING RULES:
- Write ONE tweet, 50-200 characters
- No emojis or hashtags
- First person as Krokmou
- BE SPECIFIC about the news topic
- Output only the tweet text

Recent tweets to avoid repetition:
{history_context}"""
    
    def _clean_tweet(self, tweet):
        tweet = tweet.strip('"\'')
        tweet = re.sub(r'"?\s*\(\d+\s+characters?\)"?$', '', tweet).strip()
        tweet = tweet.strip('"\'')
        tweet = re.sub(r'[—]', '... ', tweet)
        return tweet.strip('"\'')
