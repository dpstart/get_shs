import pandas as pd

import os
import re
import argparse
import numpy as np
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

    #File with ['id' , 'ver_id'] in each row
    ids  = pd.read_csv(fn,  sep='\t', header=None).values #[0]
    
    print(f"The number of songs in {fn} is: ", len(ids))

    df = pd.read_csv("./list",  sep='\t', header=None)
    df.columns = ["id", "ver_id", "title", "performer", "url", "status"]

    print("The number of songs in TRAIN + TEST + VALID IS: ", len(df))

    #Get all the idx, ver_id from the list of all data
    list_indexes = df[['id', 'ver_id']].values

    #Sort the ['id'] in ids (test file is not ordered by the 'id' like the others)
    idx = np.argsort(ids[:, 0], kind = 'stable')
    ids = ids[idx]

    keep_idx = [] #Indexes to keep after in the df
    idx_file = 0
    #We want to intersect the id and ver_id of the list file with 
    #all the songs and the id and ver_id of the train, for example
    for list_idx in range(list_indexes.shape[0]):
        
        if(list_indexes[list_idx, 0] == ids[idx_file, 0] and list_indexes[list_idx, 1] == ids[idx_file, 1]):
            keep_idx.append(list_idx)
            idx_file += 1

            if(idx_file == ids.shape[0]): #If we arrive at the end of the train/val/test file
                break
    
    #Filter with the indexes to keep
    df = df.loc[keep_idx]
    
    #df = df[df['id'].isin(ids)]
    
    print(f"The {fn} size is: ", len(df))
    print(f"The {fn} unique number is: ", np.unique(df['id']).shape[0] )
    
    #Make sure that the sizes are matching
    assert len(df) == ids.shape[0]

    return 0
    for url, id in zip(df.url, df.id):

        if not os.path.isdir(f"./{id}"):
            os.makedirs(f"./{id}")
        scrape_it(url, path=f"./{id}", quiet=False, overwrite=False)
    
    return 0

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
    