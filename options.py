"""
User configurable options.
All relative paths are relative to the project root folder.
"""
import os

general_cache = 'cache/general/'
if not os.path.isdir(general_cache): os.makedirs(general_cache)
users_cache = 'cache/users/'
if not os.path.isdir(users_cache): os.makedirs(users_cache)

media_dir = os.path.abspath('wanikani/')
if not os.path.isdir(media_dir): os.makedirs(media_dir)
media_formats = {
    'audio': {
        'subdir': 'audio',
        'ext': 'mp3', # or 'ogg'
    }
}

# Absolute path to the Firefox profile folder.
# You should not use your main profile!
# Use a secondary profile and login to WaniKani with it.
firefox_profile = ''

# WaniKani config.
apikey = ''

# Choose which subjects to process when deck building or website
# scraping.
# When scraping, stick to one subject at a time.
subjects = ['radicals', 'kanji', 'vocabulary']
# subjects = ['radicals']
