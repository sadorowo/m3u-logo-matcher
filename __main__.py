from argparse import ArgumentParser
from difflib import SequenceMatcher
import re

from ipytv import playlist as tv_playlist

from pathlib import Path
import urllib.request
import urllib.error

verbose = False

def debug(message: str):
    global verbose
    
    if verbose:
        print("[M3U-LOGO-MATCHER:DEBUG] " + message)
        
def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument("-u", "--url", dest="url", help="URL to logos", required=True)
    parser.add_argument("-m", "--m3u", dest="m3u", help="Path to m3u file", required=True, type=Path)
    parser.add_argument("-v", "--verbose", dest="verbose", help="Verbose output", action="store_true")
    
    return parser.parse_args()
    
def fetch_logos(base_logo_url: str):
    debug(f"Fetching logos from {base_logo_url}...")
        
    with urllib.request.urlopen(base_logo_url) as url:
        data = url.read().decode()
        
        # Get logo names
        for logo in re.findall(r'<a href="(.+\..+)">(.*\..+)</a>', data):
            logo_url, channel_name = logo
            yield f"{base_logo_url}/{logo_url}", channel_name
            
def process(arguments):
    debug("Processing...")
    logos = list(fetch_logos(arguments.url))

    if len(logos) == 0:
        print("No logos found! Ensure that the URL is correct and it returns a list of logo resources.")
        return
    
    # Get m3u data
    debug(f"Loading m3u file {arguments.m3u}...")
    playlist = tv_playlist.loadf(str(arguments.m3u))
    debug(f"Loaded {playlist.length()} channels")
    
    matched_logos = list(match_similar_logos(logos, get_channels(playlist)))
    debug(f"Matched {len(matched_logos)}/{playlist.length()} logos.")
    debug(f"Missing logos: {playlist.length() - len(matched_logos)}")
    
    replace_logos(playlist, matched_logos)
    debug("Logos replaced.")
    debug("Saving result...")
    
    save_result(arguments.m3u, playlist)

def replace_logos(playlist: tv_playlist.M3UPlaylist, matched_logos: list[tuple[str, str]]):
    debug("Replacing logos...")
    
    for matched_channel, logo in matched_logos:
        debug(f"Replacing logo for {matched_channel}...")
        
        channels = playlist.get_channels()
        channel: tv_playlist.IPTVChannel = None
        channel_index: int = -1
        
        for i, c in enumerate(channels):
            if c.name == matched_channel:
                channel = c
                channel_index = i
                break
            
        if channel is None:
            # Something weird happened.
            print(f"Channel {matched_channel} not found! How did this happen?")
            continue
        
        channel_copy = channel.copy()
        channel_copy.attributes["tvg-logo"] = logo
        playlist.update_channel(channel_index, channel_copy)
    
def save_result(
    input_path: str, 
    playlist: tv_playlist.M3UPlaylist
):
    with open(input_path, "w+") as f:
        f.write(playlist.to_m3u_plus_playlist())
    
    print("File overwritten.")
    print("Thank you for using this script!")
            
def match_similar_logos(logos: list[tuple[str, str]], channels: list[str]):
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
        
def get_channels(playlist: tv_playlist.M3UPlaylist):
    for channel in playlist:
        yield channel.name
        
def get_similarity_ratio(a: str, b: str):
    return SequenceMatcher(None, a, b).ratio()

if __name__ == "__main__":
    debug("Starting...")
    arguments = parse_arguments()
    verbose = arguments.verbose
    
    debug("Parsed all arguments")
    process(arguments)