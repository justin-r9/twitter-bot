import tweepy
import requests
import time
import random
import logging
import os
import sys
from datetime import datetime, timedelta, date
from calendar import monthrange
from config import *
import pytz  # For timezone handling
import praw  # For Reddit API
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Create a custom formatter that ensures newlines
class NewlineFormatter(logging.Formatter):
    def format(self, record):
        # Add a newline at the end of each log message
        message = super().format(record)
        return message + "\n"

# Set up formatters
console_formatter = NewlineFormatter('%(asctime)s.%(msecs)03d - %(levelname)s - [%(threadName)s] - %(message)s')
file_formatter = NewlineFormatter('%(asctime)s.%(msecs)03d - %(levelname)s - [%(threadName)s] - %(message)s')

# Set up console handler with UTF-8 encoding
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(console_formatter)

# Force UTF-8 encoding for the console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        # If reconfigure fails, we'll handle it in the error logging
        pass

# Set up file handler with rotation (10MB per file, keep 5 backups)
file_handler = RotatingFileHandler(
    "logs/twitter_bot.log",
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(file_formatter)

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(console_handler)
root_logger.addHandler(file_handler)

# Prevent duplicate logs
root_logger.propagate = False

class TwitterAutomation:
    def __init__(self):
        # This sets up our connection to Twitter
        logging.info("Setting up Twitter API connection...")

        # For posting tweets - using OAuth 1.0a
        self.auth = tweepy.OAuth1UserHandler(
            TWITTER_API_KEY, TWITTER_API_SECRET,
            TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET
        )
        self.api = tweepy.API(self.auth, wait_on_rate_limit=True)

        # For reading tweets (home timeline) - we are not using this anymore for scraping
        self.client = tweepy.Client(
            TWITTER_BEARER_TOKEN,
            TWITTER_API_KEY, TWITTER_API_SECRET,
            TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET,
            wait_on_rate_limit=True
        )

        # Set up Reddit API connection
        logging.info("Setting up Reddit API connection...")
        self.reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )

        # This will help us avoid processing the same post multiple times
        self.last_processed_ids = set()

        # Track when the bot started
        self.start_time = datetime.now()

        # Set maximum run time (9 hours)
        self.max_run_time = timedelta(hours=MAX_RUN_HOURS)

        # Flag to control bot execution
        self.running = True

        # Track posts per day and month
        self.posts_today = 0
        self.posts_this_month = 0

        # Get current UTC date and month
        utc_now = datetime.now(pytz.UTC)
        self.current_day = utc_now.date()
        self.current_month = utc_now.month
        self.current_year = utc_now.year

        logging.info(f"Bot initialized. Current UTC date: {self.current_day}, Current month: {self.current_month}/{self.current_year}")
        logging.info("Twitter and Reddit API connections established")

    def stop(self):
        """Set the running flag to False to stop the bot"""
        self.running = False
        logging.info("Stop signal received")

    def check_run_time(self):
        """Check if the bot has been running for more than the maximum allowed time"""
        current_time = datetime.now()
        elapsed_time = current_time - self.start_time

        if elapsed_time >= self.max_run_time:
            error_msg = f"Bot has been running for {elapsed_time} which exceeds the maximum allowed time of {self.max_run_time}"
            logging.error(error_msg)
            logging.error("Stopping bot due to maximum run time exceeded")
            return False
        return True

    def check_limits(self):
        """Check if we've reached daily or monthly limits"""
        # Get current UTC time
        utc_now = datetime.now(pytz.UTC)
        current_date = utc_now.date()
        current_month = utc_now.month
        current_year = utc_now.year

        # Reset counters if day has changed
        if current_date != self.current_day:
            logging.info(f"Day changed from {self.current_day} to {current_date}. Resetting daily post counter.")
            self.posts_today = 0
            self.current_day = current_date

        # Reset counters if month has changed
        if current_month != self.current_month or current_year != self.current_year:
            logging.info(f"Month changed from {self.current_month}/{self.current_year} to {current_month}/{self.current_year}. Resetting monthly post counter.")
            self.posts_this_month = 0
            self.current_month = current_month
            self.current_year = current_year

        # Check daily limit
        if self.posts_today >= MAX_POSTS_PER_DAY:
            logging.info(f"Daily post limit reached ({self.posts_today}/{MAX_POSTS_PER_DAY})")
            return "daily"

        # Check monthly limit
        if self.posts_this_month >= MAX_POSTS_PER_MONTH:
            logging.info(f"Monthly post limit reached ({self.posts_this_month}/{MAX_POSTS_PER_MONTH})")
            return "monthly"

        return None

    def calculate_wait_until_next_period(self, limit_type):
        """Calculate how long to wait until the next day or month"""
        utc_now = datetime.now(pytz.UTC)

        if limit_type == "daily":
            # Calculate time until midnight UTC
            tomorrow = utc_now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            wait_seconds = (tomorrow - utc_now).total_seconds()
            logging.info(f"Waiting until next day (UTC). {wait_seconds/3600:.1f} hours remaining.")
            return wait_seconds

        elif limit_type == "monthly":
            # Calculate time until next month
            current_day = utc_now.day
            current_month = utc_now.month
            current_year = utc_now.year

            # Get the number of days in the current month
            days_in_month = monthrange(current_year, current_month)[1]

            # Calculate the first day of next month
            if current_month == 12:
                next_month = 1
                next_year = current_year + 1
            else:
                next_month = current_month + 1
                next_year = current_year

            next_month_date = datetime(next_year, next_month, 1, tzinfo=pytz.UTC)
            wait_seconds = (next_month_date - utc_now).total_seconds()
            logging.info(f"Waiting until next month (UTC). {wait_seconds/86400:.1f} days remaining.")
            return wait_seconds

        return 0

    def get_reddit_posts(self, subreddit_name, limit=10, time_filter='day'):
        """Get posts from a specific subreddit"""
        try:
            logging.info(f"Fetching posts from r/{subreddit_name}...")
            subreddit = self.reddit.subreddit(subreddit_name)

            # Get top posts from the specified time filter
            posts = []
            for post in subreddit.top(time_filter=time_filter, limit=limit):
                posts.append({
                    'id': post.id,
                    'title': post.title,
                    'selftext': post.selftext,
                    'url': post.url,
                    'score': post.score,
                    'num_comments': post.num_comments,
                    'created_utc': post.created_utc
                })

            logging.info(f"Retrieved {len(posts)} posts from r/{subreddit_name}")
            return posts
        except Exception as e:
            logging.error(f"Error fetching posts from r/{subreddit_name}: {e}")
            return []

    def get_trending_reddit_posts(self, limit=20):
        """Get trending posts from r/all and r/popular"""
        try:
            logging.info("Fetching trending Reddit posts...")
            trending_posts = []

            # Get top posts from r/all
            all_posts = self.get_reddit_posts('all', limit=limit//2, time_filter='day')
            trending_posts.extend(all_posts)

            # Get top posts from r/popular
            popular_posts = self.get_reddit_posts('popular', limit=limit//2, time_filter='day')
            trending_posts.extend(popular_posts)

            # Sort by score (descending) to get the most popular
            trending_posts.sort(key=lambda x: x['score'], reverse=True)

            logging.info(f"Retrieved {len(trending_posts)} trending Reddit posts")
            return trending_posts
        except Exception as e:
            logging.error(f"Error fetching trending Reddit posts: {e}")
            return []

    def scrape_content(self):
        """Collect content from Reddit subreddits and trending posts"""
        all_posts = []

        # Get posts from specified subreddits
        for subreddit_name in SUBREDDITS_TO_SCRAPE:
            subreddit_posts = self.get_reddit_posts(subreddit_name, limit=5, time_filter='day')
            all_posts.extend(subreddit_posts)

        # Get trending posts
        trending_posts = self.get_trending_reddit_posts(limit=10)
        all_posts.extend(trending_posts)

        # Filter out posts we've already processed
        new_posts = [post for post in all_posts if post['id'] not in self.last_processed_ids]

        # Remember these posts so we don't process them again
        for post in new_posts:
            self.last_processed_ids.add(post['id'])

        # Keep only the last 1000 IDs to prevent memory issues
        if len(self.last_processed_ids) > 1000:
            self.last_processed_ids = set(list(self.last_processed_ids)[-1000:])

        logging.info(f"Scraped {len(new_posts)} new Reddit posts")
        return new_posts

    def generate_comment_content(self, posts):
        """Use GLM-4.5-Flash to create a mild, insightful comment"""
        if not posts:
            return None

        context = "\n".join([f"Title: {post['title']}\nContent: {post['selftext'][:200]}..." if post['selftext'] else f"Title: {post['title']}" for post in posts[:10]])

        headers = {
            "Authorization": f"Bearer {GLM_API_KEY}",
            "Content-Type": "application/json"
        }

        prompt = f"""Based on the following Reddit posts, please generate a mild and insightful comment that encourages thoughtful discussion.

Reddit posts:
{context}

Requirements:
- Write from the perspective of a curious and open-minded individual.
- Offer a balanced viewpoint or ask a genuine question to learn more.
- Use respectful and inclusive language.
- Avoid making absolute statements or generalizations.
- Aim for a friendly and approachable tone.
- Keep the comment between 150-200 characters.

Comment:"""

        data = {
            "model": "GLM-4.5-Flash",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an AI assistant that specializes in creating thoughtful and respectful online comments. Your goal is to foster positive and constructive conversations."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 256,
            "temperature": 0.7
        }

        try:
            logging.info("Generating comment content with GLM-4.5-Flash...")
            response = requests.post(GLM_API_URL, headers=headers, json=data)
            response.raise_for_status()

            response_data = response.json()

            if "choices" not in response_data or not response_data["choices"]:
                logging.error("No choices in GLM API response: %s", response_data)
                return None

            generated_content = response_data["choices"][0]["message"].get("content", "").strip()

            if not generated_content:
                logging.error("Empty content received from GLM API.")
                return None

            logging.info(f"Generated comment: {generated_content}")
            return generated_content
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err} - {http_err.response.text}")
            return None
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            return None

    def post_tweet(self, content):
        """Post the generated tweet to Twitter"""
        try:
            logging.info("Posting tweet to Twitter...")
            # Use OAuth 1.0a API for posting
            response = self.api.update_status(content)
            self.posts_today += 1
            self.posts_this_month += 1
            logging.info(f"Tweet posted successfully! Tweet ID: {response.id}")
            logging.info(f"Posts today: {self.posts_today}/{MAX_POSTS_PER_DAY}, Posts this month: {self.posts_this_month}/{MAX_POSTS_PER_MONTH}")
            return True
        except Exception as e:
            logging.error(f"Error posting tweet: {e}")
            return False

    def run(self):
        """Main function that runs the automation loop"""
        logging.info("Starting Twitter automation bot")
        self.running = True

        while self.running:
            try:
                # Check if we've exceeded the maximum run time
                if not self.check_run_time():
                    break

                # Check if we've reached daily or monthly limits
                limit_reached = self.check_limits()
                if limit_reached:
                    # Calculate how long to wait until the next period
                    wait_seconds = self.calculate_wait_until_next_period(limit_reached)

                    # Wait until the next period, checking the running flag periodically
                    end_time = time.time() + wait_seconds
                    while time.time() < end_time and self.running:
                        time.sleep(60)  # Check every minute
                    continue

                # Step 1: Scrape content from Reddit
                posts = self.scrape_content()

                if posts:
                    # Step 2: Generate new provocative tweet content using GLM-4.5-Flash
                    comment_content = self.generate_comment_content(posts)

                    if comment_content:
                        # Step 3: Post the tweet
                        self.post_tweet(comment_content)

                        # Wait for a random time between posts
                        wait_minutes = random.randint(MIN_WAIT_MINUTES, MAX_WAIT_MINUTES)
                        wait_seconds = wait_minutes * 60

                        logging.info(f"Waiting for {wait_minutes} minutes before next tweet...")

                        # Check the running flag periodically during the wait
                        end_time = time.time() + wait_seconds
                        while time.time() < end_time and self.running:
                            time.sleep(10)  # Check every 10 seconds
                    else:
                        logging.warning("Failed to generate comment content")
                        # Wait a shorter time before retrying (5 minutes instead of the full interval)
                        wait_minutes = 5
                        wait_seconds = wait_minutes * 60
                        logging.info(f"Waiting for {wait_minutes} minutes before retrying...")

                        # Check the running flag periodically during the wait
                        end_time = time.time() + wait_seconds
                        while time.time() < end_time and self.running:
                            time.sleep(10)  # Check every 10 seconds
                else:
                    logging.info("No new Reddit posts to process")

                    # Wait a shorter time before retrying (5 minutes)
                    wait_minutes = 5
                    wait_seconds = wait_minutes * 60
                    logging.info(f"Waiting for {wait_minutes} minutes before retrying...")

                    # Check the running flag periodically during the wait
                    end_time = time.time() + wait_seconds
                    while time.time() < end_time and self.running:
                        time.sleep(10)  # Check every 10 seconds

            except KeyboardInterrupt:
                logging.info("Bot stopped by user")
                break
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
                # Wait a minute before trying again
                logging.info("Waiting 60 seconds before retrying...")
                for _ in range(60):
                    if not self.running:
                        break
                    time.sleep(1)

        logging.info("Bot stopped")

if __name__ == "__main__":
    bot = TwitterAutomation()
    bot.run()
