# RoastBot dataset scraper, generator, and formatter.
# Created by Sean Gustavson
# Copyright Sean Gustavson 2024, all rights reserved

# Usage: python scrape.py <subreddit> <number of posts> <find_from> <find_from_time <useface> (useface optional, will apend AI aproximation of race/sex/age to row)
#
# Example: python generate.py roastme 100 hot month
# This will scrape 100 hot posts from r/roastme in the last month and save the comments to large, zipper, csv file.
#
# Example 2: python generate.py roastme 100 hot all useface
# This will scrape 100 hot posts from r/roastme from all time and save the comments to a two-column race/age/sex aproximation and roast.

import sys
import os
import zipfile
import praw
from praw.models import MoreComments
from halo import Halo
from tqdm import tqdm
import pandas as pd
import wget

#fetch urls
reddit = praw.Reddit(
    client_id='client id',
    client_secret='client secret',
    user_agent='python:0'
)

if len(sys.argv) < 5:
    print("Usage: python fetch_urls.py <subreddit> <number of posts> <find_from> <find_from_time> <useface> (optional)")
    sys.exit(1)
else:
    subreddit = sys.argv[1]
    if 'r/' in subreddit:
        subreddit = subreddit.replace('r/', '')
    number_of_posts = int(sys.argv[2])
    try:
        number_of_posts = int(sys.argv[2])
    except ValueError:
        print("Usage: python fetch_urls.py <subreddit> <number of posts> <find_from> <find_from_time> <useface> (optional")
        sys.exit(1)
    find_from = sys.argv[3]
    find_from_time = sys.argv[4]
    if (find_from not in ['hot', 'new', 'rising', 'controversial', 'top']) or (find_from_time not in ['hour', 'day', 'week', 'month', 'year', 'all']):
        print("Usage: python fetch_urls.py <subreddit> <number of posts> <find_from> <find_from_time> <useface> (optional")
        print("find_from must be in: ['hot', 'new', 'rising', 'controversial', 'top']")
        print("find_from_time must be in: ['hour', 'day', 'week', 'month', 'year', 'all']")
        sys.exit(1)

useface = False
if len(sys.argv) >= 6:
    if str(sys.argv[5]).capitalize() == "useface".capitalize():
        useface = True
        print("Will use face AI for first row characteristics")
    else:
        useface = False
        print("No AI will be used")

print("Fetching "+str(number_of_posts)+" random "+find_from+" posts from r/"+subreddit+" with time filter "+find_from_time)
#print("Fetching "+str(number_of_posts)+" random "+find_from+" posts from r/"+subreddit+" with time filter "+find_from_time)



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


print(f"Saved {len(post_urls)} post URLs")

#post_urls is the list of urls

#scrape comments from the URLS

def scrape_comments(url,use_csv=False):
    selected_comments = []
    print("Scraping comments from "+str(url.strip()))

    submission = reddit.submission(url=str(url))
    for top_level_comment in submission.comments:
        if isinstance(top_level_comment, MoreComments):
            continue
        #check not gif
        if not '[' in top_level_comment.body:
            #print(top_level_comment.body)
            selected_comments.append(top_level_comment.body)
    #make a csv file with the comments if csv is true
    if use_csv:
        #with open('comments.csv', 'w') as f:
        #    writer = csv.writer(f)
        #    writer.writerow(['comment'])
        #    pbar = tqdm(total=len(selected_comments), desc="Writing comments to CSV")
        #    for item in selected_comments:
        #        writer.writerow([item])
        #        pbar.update(1)
        print('Saving comments to CSV while scraping is not supported')
        sys.exit(1)
    else:
        return selected_comments
def download_submission_image(submission, filename_prefix=''):
    """
    Download the image from a submission, handling both regular posts and galleries.

    Args:
        submission: A praw.models.Submission object
        filename_prefix: Prefix for the saved filename

    Returns:
        str: Path to downloaded file, or None if no image was found/downloaded
    """
    # Check if submission is a gallery
    if hasattr(submission, 'gallery_data'):
        # Handle gallery post - get first image
        if submission.gallery_data['items']:
            media_id = submission.gallery_data['items'][0]['media_id']
            image_url = f"https://i.redd.it/{media_id}.jpg"
            try:
                return image_url
            except Exception as e:
                print(f"Error downloading gallery image: {e}")
                return None

    # Handle regular image post
    elif submission.url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
        try:
            return submission.url
        except Exception as e:
            print(f"Error downloading regular image: {e}")
            return None

    return None
dataset = []
urls = post_urls

#main loop
pbar = tqdm(total=len(urls))
for i, url in enumerate(urls):

    #print(f"working on {i+1} of {len(urls)}...")
    pbar.update()
    url = 'https://old.reddit.com' + url

    #ai stuff
    if useface:
        print("Finding image at url {url}...")

    submission = reddit.submission(url=url)

    image_url = download_submission_image(submission)


    skip_ai = False
    # download
    if useface:
        try:
            print(f"Downloading image at url {image_url}...")

            image_filename = wget.download(image_url)
            print(f"\nDownloaded image to: {image_filename}")
        except:
            print("something went wrong downloading an image...")
            skip_ai = True
            continue
    else:
        skip_ai = True

    results_total = []
    use_fast=True

    if not skip_ai:
        try:
            from transformers import pipeline
            classifier = pipeline("image-classification", model="nateraw/vit-age-classifier")
            results = classifier(image_filename)
            print("\nAI Classification Results:")
            for result in results:
                results_total.append(result)

            #second model
            classifier = pipeline("image-classification", model="WinKawaks/vit-tiny-patch16-224")
            results = classifier(image_filename)
            print("\nAI Classification Results:")
            for result in results:
                results_total.append(result)

            #third model
            classifier = pipeline("image-classification", model="rizvandwiki/gender-classification")
            results = classifier(image_filename)
            print("\nAI Classification Results:")
            for result in results:
                results_total.append(result)

            #fourth model
            classifier = pipeline("image-classification", model="cledoux42/Ethnicity_Test_v003")
            results = classifier(image_filename)
            print("\nAI Classification Results:")
            for result in results:
                results_total.append(result)

        except Exception as e:
            print(f"\nError performing AI classification: {e}")

        os.remove(image_filename)

        for result in results_total:
            print(f"Label: {result['label']}, Score: {result['score']:.4f}")

        print('-------------')
        print(results_total[0]['label'])
        print(results_total[5]['label'])
        print(results_total[6]['label'])
        print(results_total[10]['label'])
        print(results_total[12]['label'])
        #end ai stuff

        totalresults = str(results_total[0]['label'] + ", " + results_total[5]['label'] + ", " + results_total[6]['label'] + ", " + results_total[10]['label'] + ", " + results_total[12]['label'])
        ai_info = totalresults
    else:
        ai_info = "roast:"
    try:
        comments = scrape_comments(url, use_csv=False)
        if comments:  # Only add if we got comments
            # Create a list of dictionaries for the DataFrame
            data = [{'input': ai_info, 'output': comment} for comment in comments]
            df = pd.DataFrame(data)
            df.to_csv(f'datasets/dataset{i+1}.csv', index=False, encoding='utf-8')
    except Exception as e:
        print(f"Error processing URL {url}: {str(e)}")
pbar.close()

print("Datasets saved to datasets directory")

#zip all the csv files in the datasets directory
#with zipfile.ZipFile(f'datasets_{actual_subreddit}.zip', 'w') as zipf:
#    for file in os.listdir('datasets'):
#        zipf.write(os.path.join('datasets', file), file)

#make one big csv file
with open(f'dataset_{actual_subreddit}_{find_from}_{len(urls)}.csv', 'w') as f:
    for file in os.listdir('datasets'):
        with open(os.path.join('datasets', file), 'r') as infile:
            f.write(infile.read())


#delete the datasets in the datasets directory
for file in os.listdir('datasets'):
    os.remove(os.path.join('datasets', file))

print(f"Datasets saved to dataset_{actual_subreddit}_{find_from}_{len(urls)}.csv")
