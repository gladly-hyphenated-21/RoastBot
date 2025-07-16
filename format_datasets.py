import os
import zipfile
import sys
import random

if len(sys.argv) < 2:
    print("Usage: python format_datasets.py <subreddit>")
    sys.exit(1)

subreddit = sys.argv[1]

#zip all the csv files in the datasets directory
with zipfile.ZipFile(f'datasets_{subreddit}.zip', 'w') as zipf:
    for file in os.listdir('datasets'):
        zipf.write(os.path.join('datasets', file), file)
#delete the datasets in the datasets directory
for file in os.listdir('datasets'):
    os.remove(os.path.join('datasets', file))

print("Datasets saved to datasets.zip")