import praw
from praw.models import MoreComments
import sys
import csv
from halo import Halo
from tqdm import tqdm

reddit = praw.Reddit(
    client_id='client id',
    client_secret='client secret',
    user_agent='python:0'
)

if len(sys.argv) < 5:
    print("Usage: python fetch_urls.py <subreddit> <number of posts> <find_from> <find_from_time>")
    sys.exit(1)
else:
    subreddit = sys.argv[1]
    if 'r/' in subreddit:
        subreddit = subreddit.replace('r/', '')
    number_of_posts = int(sys.argv[2])
    try:
        number_of_posts = int(sys.argv[2])
    except ValueError:
        print("Usage: python fetch_urls.py <subreddit> <number of posts> <find_from> <find_from_time>")
        sys.exit(1)
    find_from = sys.argv[3]
    find_from_time = sys.argv[4]
    if (find_from not in ['hot', 'new', 'rising', 'controversial', 'top']) or (find_from_time not in ['hour', 'day', 'week', 'month', 'year', 'all']):
        print("Usage: python fetch_urls.py <subreddit> <number of posts> <find_from> <find_from_time>")
        sys.exit(1)

#url searching methods
find_from = 'top' # can me 'hot', 'new', 'rising', 'controversial', 'top'
find_from_time = 'year' # can me 'hour', 'day', 'week', 'month', 'year', 'all'

spinner = Halo(text="Fetching "+str(number_of_posts)+" random "+find_from+" posts from r/"+subreddit+" with time filter "+find_from_time, spinner='dots2', text_color='blue', color='blue')
spinner.start()

actual_subreddit = reddit.subreddit(subreddit)
post_urls = []

if find_from == 'hot':
    for submission in actual_subreddit.hot(limit=number_of_posts):
        post_urls.append(submission.permalink)
elif find_from == 'new':
    for submission in actual_subreddit.new(limit=number_of_posts):
        post_urls.append(submission.permalink)
elif find_from == 'rising':
    for submission in actual_subreddit.rising(limit=number_of_posts):
        post_urls.append(submission.permalink)
elif find_from == 'controversial':
    for submission in actual_subreddit.controversial(limit=number_of_posts):
        post_urls.append(submission.permalink)
elif find_from == 'top':
    for submission in actual_subreddit.top(limit=number_of_posts, time_filter=find_from_time):
        post_urls.append(submission.permalink)

spinner.stop()

# Write URLs to file
with open('links.txt', 'w') as f:
    for url in post_urls:
        f.write("https://old.reddit.com" + url + '\n')

print(f"Saved {len(post_urls)} post URLs to links.txt")
