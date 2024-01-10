from argparse import ArgumentParser
from difflib import SequenceMatcher
import re, m3u8

from pathlib import Path
from os.path import join
import urllib.request
import urllib.error

verbose = False

def debug(message):
    global verbose
    
    if verbose:
        print("[M3U-LOGO-MATCHER:DEBUG] " + message)
        
def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument("-u", "--url", dest="url", help="URL to logos", required=True)
    parser.add_argument("-m", "--m3u", dest="m3u", help="Path to m3u file", required=True, type=Path)
    parser.add_argument("-v", "--verbose", dest="verbose", help="Verbose output", action="store_true")
    
    return parser.parse_args()
    
def fetch_logos(logo_url):
    debug(f"Fetching logos from {logo_url}...")
        
    with urllib.request.urlopen(logo_url) as url:
        data = url.read().decode()
        
        # Get logo names
        for logo in re.findall(r'<a href="(.+\..+)">(.*\..+)</a>', data):
            yield logo
            
def process(arguments):
    debug("Processing...")
    logos = list(fetch_logos(arguments.url))

    if len(logos) == 0:
        print("No logos found! Ensure that the URL is correct and it returns a list of logo resources.")
        return
    
    # Get m3u data
    debug(f"Loading m3u file {arguments.m3u}...")
    playlist = m3u8.load(str(arguments.m3u))
    debug(f"Loaded {len(playlist.segments)} segments")
    
    matched_logos = list(match_similar_logos(logos, get_channels(playlist)))
    debug(f"Matched {len(matched_logos)}/{len(playlist.segments)} logos.")
    debug(f"Missing logos: {len(playlist.segments) - len(matched_logos)}")
    
    # Give result
    result_path = join(arguments.m3u.parent, f"result_{arguments.m3u.name}.txt")
    if Path(result_path).exists():
        response = input(f"Result file {result_path} already exists. Overwrite? [y/N] ")
        if response.lower() == "y":
            print("Overwriting...")
            save_result(result_path, matched_logos)
        else:
            print("Aborting...")
        return
    
    save_result(result_path, matched_logos)
    print(f"Result written to result_{arguments.m3u}.txt")

def save_result(result_path, matched_logos):
    with open(result_path, "w+") as rf:
        debug(f"Writing result to result_{arguments.m3u.name}.txt...")
        for channel, logo in matched_logos:
            parsed_logo_url = f"{arguments.url}/{logo}"
            
            rf.write(f"{channel} -> {parsed_logo_url}\n")
    
    print(f"Result written to {result_path}")
    print("Thank you for using this script!")
            
def match_similar_logos(logos, channels):
    debug("Matching logos...")
    
    for channel in channels:
        debug(f"Matching channel {channel}...")
        
        matched = False
        match_score = 0
        
        for logo in logos:
            if matched:
                break
            
            logo_url, channel_name = logo
            score = get_similarity_ratio(channel, channel_name)
            
            if score > match_score:
                match_score = score
                
            if match_score > 0.5:
                debug(f"Matched {channel} with {logo_url} (ratio: {match_score})")
                matched = True
                yield (channel, logo_url)
            
        if not matched:
            debug(f"No match for {channel}")
            continue
        
def get_channels(playlist):
    for segment in playlist.segments:
        yield segment.title
        
def get_similarity_ratio(a, b):
    return SequenceMatcher(None, a, b).ratio()

if __name__ == "__main__":
    debug("Starting...")
    arguments = parse_arguments()
    verbose = arguments.verbose
    
    debug("Parsed all arguments")
    process(arguments)