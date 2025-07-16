#merge a csv file to a big csv file
#usage: python merge.py <file1.csv> <file2.csv> <file3.csv> ...
import os
import sys
import pandas as pd
from halo import Halo

name = input("Enter the name of the big csv file: ")
if '.csv' not in name:
    name += '.csv'
spinner = Halo(text="Merging all csv files into "+name, spinner='dots2', text_color='blue', color='blue')
spinner.start()
# Create empty list to store all dataframes
all_dfs = []

# Read each CSV file and add to list
for file in sys.argv[1:]:
    df = pd.read_csv(file)
    all_dfs.append(df)

# Concatenate all dataframes and write to output file
if all_dfs:
    merged_df = pd.concat(all_dfs, ignore_index=True)
    merged_df.to_csv(name, index=False)
    #print(f"\nSuccessfully merged {len(all_dfs)} files into {name}")
    spinner.succeed()
else:
    print("No input files provided")
    spinner.succeed()