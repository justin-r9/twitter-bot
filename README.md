# Twitter Bot with Reddit Content and GLM-4.5-Flash Integration

This is a Twitter automation bot that scrapes content from Reddit, generates mild, insightful comments using GLM-4.5-Flash, and posts them to Twitter. The bot includes a web interface for easy control and monitoring.

## Features

- **Reddit Content Scraping**: Automatically fetches trending posts from specified subreddits
- **AI-Powered Comment Generation**: Uses GLM-4.5-Flash to create mild, insightful comments
- **Twitter Integration**: Posts generated comments to your Twitter account
- **Web Control Panel**: Start/stop the bot and monitor activity through a web interface
- **Rate Limiting**: Respects Twitter's API limits and daily/monthly posting caps
- **Automatic Time Zone Handling**: Uses UTC time for consistent operation
- **Colored Logging**: Easy-to-read logs with color coding and timestamps

## Project Structure

```
twitter-bot/
├── config.py.example         # Configuration template (create config.py from this)
├── twitter_automation.py     # Main bot logic
├── web_interface.py          # Flask web interface
├── requirements.txt         # Python dependencies
├── templates/
│   └── index.html           # HTML template for the web interface
├── .gitignore              # Files to exclude from version control
├── LICENSE                 # MIT License
├── README.md               # This file
└── logs/                   # Log files directory (auto-created, excluded from git)
```

## Prerequisites

- Python 3.10 or higher
- Twitter Developer Account with API access
- Reddit API credentials
- GLM-4.5-Flash API key
- Basic knowledge of Python and command line

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/twitter-bot.git
cd twitter-bot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

Create a `config.py` file based on the template:

```bash
cp config.py.example config.py
```

Then edit `config.py` with your actual API keys:

```python
# Twitter API keys (get these from Twitter Developer portal)
TWITTER_API_KEY = "your_api_key_here"
TWITTER_API_SECRET = "your_api_secret_here"
TWITTER_ACCESS_TOKEN = "your_access_token_here"
TWITTER_ACCESS_TOKEN_SECRET = "your_access_token_secret_here"
TWITTER_BEARER_TOKEN = "your_bearer_token_here"

# GLM-4.5-Flash API key (get this from Zhipu AI)
GLM_API_KEY = "your_glm_api_key_here"
GLM_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

# Reddit API credentials
REDDIT_CLIENT_ID = "your_reddit_client_id"
REDDIT_CLIENT_SECRET = "your_reddit_client_secret"
REDDIT_USER_AGENT = "script:twitter-bot-content-scraper:1.0 (by u/your_reddit_username)"

# Subreddits to scrape content from
SUBREDDITS_TO_SCRAPE = [
    "technology",
    "news",
    "worldnews",
    "politics",
    "science",
    "futurology",
    "todayilearned",
    # Add more subreddits you want to follow
]

# Bot settings
MIN_WAIT_MINUTES = 30   # Minimum minutes between tweets (30 minutes)
MAX_WAIT_MINUTES = 60   # Maximum minutes between tweets (1 hour)
MAX_RUN_HOURS = 9       # Maximum hours the bot will run continuously
MAX_POSTS_PER_DAY = 16  # Maximum posts per day
MAX_POSTS_PER_MONTH = 100  # Maximum posts per month (Twitter's limit)

# Location for trending topics (1 = Worldwide)
TREND_LOCATION_WOEID = 1
```

### 4. Getting API Credentials

#### Twitter API
1. Go to the [Twitter Developer Portal](https://developer.twitter.com/)
2. Create a new project and app
3. Set permissions to "Read and Write"
4. Generate your API keys and tokens
5. Note: Free tier has posting limits. You may need Basic access ($200/month) for full functionality

#### Reddit API
1. Go to [Reddit Preferences](https://www.reddit.com/prefs/apps)
2. Create a new app
3. Select "script" as the app type
4. Use `http://localhost:8080` as the redirect URI
5. Note your client ID and secret

#### GLM-4.5-Flash API
1. Go to the Zhipu AI platform
2. Create an account and generate an API key
3. Use the provided endpoint URL

### 5. Run the Bot

Start the web interface:

```bash
python web_interface.py
```

Open your browser and go to `http://localhost:5000` to access the control panel.

## Usage

### Web Interface

1. **Start/Stop Bot**: Use the buttons to control the bot
2. **View Logs**: Monitor bot activity in real-time
3. **Check Status**: See if the bot is running and how many posts it has made

### Command Line

You can also run the bot directly without the web interface:

```bash
python twitter_automation.py
```

Press Ctrl+C to stop the bot.

## Customization

### Adjusting Posting Frequency

Edit the `MIN_WAIT_MINUTES` and `MAX_WAIT_MINUTES` in `config.py` to change how often the bot posts.

### Adding More Subreddits

Add or remove subreddits in the `SUBREDDITS_TO_SCRAPE` list in `config.py`.

### Changing Tweet Style

Modify the prompt in the `generate_comment_content` method in `twitter_automation.py` to change the tone and style of generated comments.

## Troubleshooting

### Common Issues

1. **Twitter API Error 403**: Your access level doesn't allow posting tweets. You may need to upgrade to Basic access.
2. **Module Not Found**: Make sure all dependencies are installed with `pip install -r requirements.txt`.
3. **Unicode Encoding Error**: The code handles this automatically, but if you see encoding issues, make sure your console supports UTF-8.
4. **Empty Tweet Content**: This can happen if the GLM API returns an empty response. The bot will retry after 5 minutes.

### Logs

Check the `logs/twitter_bot.log` file for detailed information about the bot's operation and any errors.

## Important Notes

- **Twitter API Limits**: The free tier of Twitter's API has significant limitations. You may need to upgrade to Basic access ($200/month) for full functionality.
- **Reddit Rules**: Be careful not to spam subreddits. Follow Reddit's content policy and each subreddit's rules.
- **Bot Disclosure**: Twitter requires disclosure for automated accounts. Consider adding "bot" to your profile or including a disclaimer in your bio.
- **API Costs**: Be aware of any costs associated with the GLM-4.5-Flash API.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This bot is for educational purposes. Use responsibly and in compliance with the terms of service of the platforms it interacts with. The authors are not responsible for any misuse of this software.

## Files You Need to Have

1. **config.py** - Configuration file for API keys and settings (create from config.py.example)
2. **twitter_automation.py** - Main bot logic
3. **web_interface.py** - Flask web interface
4. **requirements.txt** - Python dependencies
5. **templates/index.html** - HTML template for the web interface
6. **.gitignore** - Files to exclude from version control
7. **LICENSE** - MIT License
8. **README.md** - This file
9. **logs/** - Directory for log files (auto-created, excluded from git)
10. **config.py.example** - Configuration template

## Future Enhancements

- Support for additional social media platforms
- Advanced content filtering and moderation
- Analytics dashboard
- Mobile app interface
- Multi-language support
- Integration with more AI models
