"""
User configurable options for the scraper.
All paths relative to the project root folder.
See scrape_wanikani.py for usage instructions.
"""
import os

general_cache_path = 'cache/general/'

formats = {
    'audio': 'audio/' + 'mpeg', # or 'ogg'
}

audio_path = os.path.abspath(general_cache_path + 'audio/')
if not os.path.isdir(audio_path): os.makedirs(audio_path)

# Absolute path to the Firefox profile folder.
# You should not use your main profile!
# Use a secondary profile and login to WaniKani with it.
firefox_profile = 'YOUR_PATH_HERE'

# WaniKani config.
username = 'YOUR_USERNAME_HERE'
userpath = 'cache/users/{}/'.format(username)
if not os.path.isdir(userpath): os.makedirs(userpath)

# Stick to scraping one subject at a time.
# subjects = ['radicals', 'kanji', 'vocabulary']
subjects = ['radicals']
