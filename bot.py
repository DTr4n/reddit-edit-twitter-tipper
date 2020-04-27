from dotenv import find_dotenv, load_dotenv
from os import getenv
import praw
import tweepy


load_dotenv(find_dotenv())

# Twitter security codes
CONSUMER_KEY = getenv('TWITTER_CONSUMER_KEY')
CONSUMER_SECRET = getenv('TWITTER_CONSUMER_SECRET')
ACCESS_TOKEN = getenv('TWITTER_ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = getenv('TWITTER_ACCESS_TOKEN_SECRET')

# Reddit security codes
CLIENT_ID = getenv('REDDIT_CLIENT_ID')
CLIENT_SECRET = getenv('REDDIT_CLIENT_SECRET')
PASSWORD = getenv('REDDIT_PASSWORD')
USERNAME = getenv('REDDIT_USERNAME')
USER_AGENT = getenv('REDDIT_USER_AGENT')

# The Reddit user the bot is overseeing
TARGET_REDDIT_USER = getenv('TARGET_REDDIT_USER')


def duplicate_post(id):
	"""
	Check if the post has already been come across by comparing the post id with the one stored
	"""
	try:
		with open('submission_history.txt', 'r') as f:
			return id == f.readline().strip()
	except FileNotFoundError:
		return False


def identify_update_within_post(submission) -> str:
	"""
	Identify if the current post's has been edited with an addition of text by reverse searching
	where the section of text saved in the history file is located. If it's at the end, the post
	hasn't been updated, therefore return None. Else, return the new text following where the
	previous section of text ended at.

	In the case where the section of text saved isn't found in current post, return a string 
	"Unidentify edit made to post" to be tweeted
	"""

	with open('submission_history.txt', 'r') as f:
		f.readline()  # Ignore first line, which is the post id
		previous_text = f.read().strip()

	last_index = submission.selftext.rfind(previous_text)

	if last_index == -1:
		update_history_file(submission)
		return "Unidentify edit made to post: submission.title"  + '\nhttps://www.reddit.com' \
				+ submission.permalink + '?sort=new'
	elif (last_index + len(previous_text) == len(submission.selftext)):
		return None
	else:
		update_history_file(submission)
		return submission.selftext[last_index + len(previous_text):]


def update_history_file(submission):
	"""
	Overwrite a text file with information about the last post submission the bot came across
	First line is the submission id
	The rest of the text file contains the last 200 characters of the submission text.
	"""
	with open('submission_history.txt', 'w') as f:
		f.write(submission.id +'\n')
		f.write(submission.selftext[-200:])


def get_update_from_reddit_user() -> str:
	"""
	If targeted Reddit user made a new post, return the link to the post.
	If a previous post is edited with a clearly added section of text, return the updated text.
	If a previous post is edited, but an update isn't clear (e.g. spelling fix), then return
		"Unidentify edit made to post"
	If no change is detected, return None.
	"""

	# Create a Reddit instance with values saved in praw.ini file
	reddit = praw.Reddit(client_id=CLIENT_ID,
                         client_secret=CLIENT_ID,
                         password=PASSWORD,
                         username=USERNAME,
                         user_agent = USER_AGENT)

	# Retrieve latest submission
	try: 
		submission = next(iter(reddit.redditor(TARGET_REDDIT_USER).submissions.new(limit=1)))
	except StopIteration:
		print('No submissions found or invalid Reddit username')
		return None

	print(submission.title)

	if duplicate_post(submission.id):
		return identify_update_within_post(submission)
	else:
		update_history_file(submission)
		return 'New Post: ' + submission.title + '\nhttps://www.reddit.com' + submission.permalink \
				+ '?sort=new'


def create_twitter_api():
	# Authenticate to Twitter
	auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
	auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

	return tweepy.API(auth)


def tweet_in_chunks(api, tweet_text):
	"""
	Tweets are limited to 240 characters, therefore bot must break down the text into chunks of 240
	characters or less. Tweeting the chunkcs in reverse so that it reads top down in Twitter.
	"""

	# TODO: Parse out links in the tweet_text. If a link is seperated into different chunks, it won't
	#       be useful. Note to self: Twitter shortens a link to 23 characters
	# TODO: For image links, download images and tweet the downloaded image instead of a url link

	chunk_end_index = len(tweet_text)
	while chunk_end_index >= 0:
		chunck_start_index = chunk_end_index - 240 if chunk_end_index - 240 > 0 else 0
		api.update_status(tweet_text[chunck_start_index : chunk_end_index])
		chunk_end_index -= 240


def tweeter(tweet_text):
	api = create_twitter_api()
	tweet_in_chunks(api, tweet_text)


def main():
	update_text = get_update_from_reddit_user()

	# if (update_text):
	# 	tweeter(update_text.strip())


if __name__ == "__main__":
	main()