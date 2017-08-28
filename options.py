"""
User configurable options.
All relative paths are relative to the project root folder.
"""
import os

options = {
    'general_cache': 'cache/general/',
    'users_cache': 'cache/users/',
    'deck_path': 'WaniKani.apkg',
    'media_dir': os.path.abspath('media/'),
    'media_formats': {
        'audio': {
            'subdir': 'audio',
            'ext': 'mp3', # or 'ogg'
        },
        'font': {
            'subdir': '',
            'ext': 'ttf', # can't change this, sorry!
        },
    },
    # Absolute path to the Firefox profile folder.
    # You should not use your main profile!
    # Use a secondary profile and login to WaniKani with it.
    'firefox_profile': '',
    # WaniKani config.
    'apikey': '',
}

# Choose which subjects to process when deck building or website
# scraping.
# When scraping, stick to one subject at a time.
subjects = ['radicals', 'kanji', 'vocabulary']
# subjects = ['radicals']
