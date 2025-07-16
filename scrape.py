import praw
from praw.models import MoreComments
import sys
from halo import Halo
from tqdm import tqdm
import pandas as pd



reddit = praw.Reddit(
    client_id='client id',
    client_secret='client secret',
    user_agent='python:0'
)

def pass_urls_from_file(file_path):
    with open(file_path, 'r') as file:
        # Strip whitespace and empty lines
        urls = [url.strip() for url in file.readlines() if url.strip()]
    return urls

def scrape_comments(url,use_csv=False):
    selected_comments = []
    spinner = Halo(text="Scraping comments from "+url.strip(), spinner='dots', text_color='blue',color='blue')
    spinner.start()
    submission = reddit.submission(url=str(url))
    for top_level_comment in submission.comments:
        if isinstance(top_level_comment, MoreComments):
            continue
        #check not gif
        if not '[' in top_level_comment.body:
            #print(top_level_comment.body)
            selected_comments.append(top_level_comment.body)
    spinner.stop()
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

dataset = []
urls = pass_urls_from_file(sys.argv[1])

for i, url in enumerate(urls):
    try:
        comments = scrape_comments(url, use_csv=False)
        if comments:  # Only add if we got comments
            dataset.append(comments)
            # Convert comments to pandas DataFrame and save as CSV
            df = pd.DataFrame(comments, columns=['comment'])
            df.to_csv(f'datasets/dataset{i+1}.csv', index=False, encoding='utf-8')
    except Exception as e:
        print(f"Error processing URL {url}: {str(e)}")

print("Datasets saved to datasets directory")
