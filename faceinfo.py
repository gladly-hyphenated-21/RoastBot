# aproximates a person in a reddit post's race/age/sex with AI image processing
# Usage: python3 faceinfo.py <url>
# Copyright Sean Gustavson 2025, all rights reserved

import sys
import os
import praw
from halo import Halo
from tqdm import tqdm
import wget

doLocalImage = False

if len(sys.argv) >= 3:
    if "--local" == str(sys.argv[1]):
        doLocalImage = True

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
            return image_url
        except Exception as e:
            print(f"Error downloading regular image: {e}")
            return None

    return None


if not doLocalImage:
    reddit = praw.Reddit(
        client_id='id here',
        client_secret='secret here',
        user_agent='python:0'
    )

    if len(sys.argv) < 2:
        print("Usage: python3 faceinfo.py <url>")
        exit()
    else:
        url = str(sys.argv[1])
        if not 'http' in url:
            print(f"invalid url {url}")
            exit()

    spinner = Halo(text=f"Finding image at url {url}...", spinner='dots2', text_color='blue', color='blue')
    spinner.start()
    submission = reddit.submission(url=url)


    image_url = download_submission_image(submission)
    spinner.stop()


    # download
    spinner = Halo(text=f"Downloading image at url {image_url}...", spinner='dots2', text_color='blue', color='blue')
    spinner.start()
    image_filename = wget.download(image_url)
    print(f"\nDownloaded image to: {image_filename}")
    spinner.stop()
else:
    image_filename = sys.argv[2]
#process
#spinner = Halo(text=f"Analyzing Image...", spinner='dots2', text_color='blue', color='blue')
#spinner.start()

results_total = []
use_fast=True

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

    classifier = pipeline("image-classification", model="rizvandwiki/gender-classification")
    results = classifier(image_filename)
    print("\nAI Classification Results:")
    for result in results:
        results_total.append(result)

    classifier = pipeline("image-classification", model="cledoux42/Ethnicity_Test_v003")
    results = classifier(image_filename)
    print("\nAI Classification Results:")
    for result in results:
        results_total.append(result)

except Exception as e:
    print(f"\nError performing AI classification: {e}")

if not doLocalImage:
    os.remove(image_filename)
    print(f"\nDeleted image file: {image_filename}")


#spinner.stop()
for result in results_total:
    print(f"Label: {result['label']}, Score: {result['score']:.4f}")

print('-------------')
print(results_total[0]['label'])
print(results_total[5]['label'])
print(results_total[6]['label'])
print(results_total[10]['label'])
print(results_total[12]['label'])
