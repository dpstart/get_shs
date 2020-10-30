import pandas as pd

import os
import re
import argparse

import pafy

try:
    from urllib.parse import urlencode
    from urllib.request import urlopen
except ImportError:
    from urllib import urlencode, urlopen

YOUTUBE_API_KEY = "AIzaSyDc3qwXIs-vVo9LF3fsAmEcDw98Y-UU-X8" 
pafy.set_api_key(YOUTUBE_API_KEY) 


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--train", action='store_true')
    parser.add_argument("--val", action='store_true')
    parser.add_argument("--test", action='store_true')

    args = parser.parse_args()


    if args.train:
        fn = "SHS100K-TRAIN"
    elif args.val:
        fn = "SHS100K-VAL"
    elif args.test:
        fn = "SHS100K-TEST"


    ids  = pd.read_csv(fn,  sep='\t', header=None)[1]


    df = pd.read_csv("./list",  sep='\t', header=None)
    df.columns = ["id", "ver_id", "title", "performer", "url", "status"]


    df = df[df['id'].isin(ids)]

    for url, id in zip(df.url, df.id):
        if not os.path.isdir(f"./{id}"):
            os.makedirs(f"./{id}")
        scrape_it(url, path=f"./{id}", quiet=False, overwrite=False)

def scrape_it(url, path, quiet, overwrite):

    try:
        video = pafy.new(url)
    except Exception as e: 
        print(str(e) + "\n")
        return

    # Collect video metadata.
    metadata = video.keywords + [
        video.title, video.author, video.description, video.category
    ]
    haystack = ' '.join(metadata).lower()

   
    # Always prefer highest quality audio.
    audio = video.getbestaudio()

    # Skip existing files.
    if os.path.isfile(audio.filename) and not overwrite:
        return
    
    # Download audio to working directory.
    audio.download(filepath=path, quiet=quiet)

if __name__ == "__main__":
    main()
    