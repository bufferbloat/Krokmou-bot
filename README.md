<div align="center">
<img src="https://2264.pw/src/media/krokmouautist.png" align="center" width="20%" >
<h1>Krokmou Bot</h1>

<div align="left" style="position: relative;">
<p align="left">
	A simple Twitter bot that keeps the memory of my beloved cat alive through daily generated tweets.
</p>
<p align="left">
	<img src="https://img.shields.io/github/last-commit/bufferbloat/Krokmou-bot?style=flat-square&color=0080ff" alt="last-commit">
	<img src="https://img.shields.io/github/commit-activity/t/bufferbloat/Krokmou-bot?style=flat-square&color=0080ff" alt="commit-activity">
	<img src="https://img.shields.io/github/languages/top/bufferbloat/Krokmou-bot?style=flat-square&color=0080ff" alt="top-language">
	<a href="https://x.com/KrokmouVoid" target="_blank">
		<img src="https://img.shields.io/badge/follow-@KrokmouVoid-1DA1F2?style=flat-square&logo=x&logoColor=white" alt="twitter">
	</a>

</p>

## Overview

[Krokmou Bot](https://x.com/KrokmouVoid) is a simple Twitter bot made to preserve and share the memory of my recently deceased cat named Krokmou. 
It generates tweets that capture Krokmou's unique personality, sharing imagined daily adventures, thoughts about cuddles, and playful moments with leaves and treats, keeping his spirit alive in the digital world.
<br/>
<br/>
I started this project earlier this year as a fun experiment and never really finished it, the project has taken on deeper meaning and purpose following Krokmou's passing, serving as both a memorial and a way to process grief

## Features

- **Smart Tweet Generation**: Uses [OpenRouter API](https://openrouter.ai/docs/quickstart) to create personality-consistent tweets
- **Time-Aware Content**: Generates contextual tweets based on time of day and seasons
- **Scheduled Posting**: Tweets three times per day using [Tweepy](https://github.com/tweepy/tweepy/) library
- **Content Diversity**: Implements smart similarity checking to prevent repetitive tweets
- **Tweet History**: Maintains a local history to ensure unique and varied content
- **Docker Support**: Easy deployment and management through containerization

## Project Structure

```sh
└── Krokmou-bot/
    ├── Dockerfile
    ├── docker-compose.yml
    ├── requirements.txt
    ├── src/
    │   ├── __init__.py
    │   ├── ai_client.py
    │   ├── main.py
    │   └── twitter_client.py
    ├── test_ai.py
    └── test_complete.py
```

## Getting Started

### Prerequisites

- Python 3.8+
- Docker / Docker Compose
- Twitter Bot API credentials
- OpenRouter API key

### Installation

1. Clone the repository:
```sh
git clone https://github.com/bufferbloat/Krokmou-bot
cd Krokmou-bot
```

2. Create a `.env` file with your credentials:
```sh
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
OPENROUTER_API_KEY=your_openrouter_api_key
```

3. Build and run with Docker:
```sh
docker-compose up -d --build
```

### Testing

Test the bot's functionality:

```sh
# Test tweet generation
py test_ai.py

# Test complete functionality
py test_complete.py
```

Check the bot logs to verify it’s running correctly:
```sh
cat krokmou_bot.log
```
Or follow the logs in real-time:
```sh
tail -f krokmou_bot.log
```

## Project Roadmap

- [X] Basic tweet generation and posting
- [X] Time-aware tweet generation
- [X] Tweet similarity prevention
- [X] Seasonal event awareness
- [X] Improve prompt generation [¹](https://github.com/bufferbloat/Krokmou-bot/commit/b2bd5d03a38852cc7dfea763c7c2c5bf5b8edf41) [²](https://github.com/bufferbloat/Krokmou-bot/commit/551b9984786d457ff2fe970931404b7c5774f623#diff-802a5f77f165df16a184bcb5aed013e7f9d4a586f72c1b8e54815e960ea1f15e)
- [ ] Weather-aware tweet generation
- [ ] Real-world events awareness
- [ ] Images support
- [ ] Discord integration bridge
- [ ] Interactive reply system
- [ ] Codebase cleanup (lol)



## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Created in memory of Krokmou, a beloved cat whose spirit lives on through this project
- Thanks to [Tweepy](https://www.tweepy.org/) for making Twitter API integration seamless and reliable
- Special thanks to [OpenRouter](https://openrouter.ai/docs/quickstart) for providing free API access

##
<div align="center">
Made with ❤️ for Krokmou
