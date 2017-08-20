#! /usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.
"""A CLI for converting WaniKani user data to an Anki deck.
TODO: mention in genanki documentation that deck ID is POSIX epoch second timestamp, used for determining relative due dates of cards.
TODO: Match Wanki deck.
TODO: Create web interface and core Python library.
TODO: Double check WaniKani SRS to Anki SRS translation.
TODO: Ensure deck updates properly.
TODO: Consider in long term serializing Anki deck instead of WaniKani JSON.
"""
import os

from wanikani2anki import WaniKani, WaniKani2Anki

wk = WaniKani()
wk2a = WaniKani2Anki(wk)

general_cache_path = 'cache/general/'
if not os.path.isdir(general_cache_path): os.makedirs(general_cache_path)

# username = input('Username: ')
username = 'bbucommander'
userpath = 'cache/users/{}/'.format(username)

user = wk.get_user(username, userpath)

print("""Fetching information for
      user:  {username}
      level: {level}
    """.format(**user['wanikani']['data']))

data = wk.get_data(user, userpath, general_cache_path)

# print(data['vocabulary']['data'][0])
# print(next(x for x in data['radical']['data'] if x['id'] == 8762))

options = wk2a.create_options(user)

deck = wk2a.create_deck(user, data, options)

print('Writing deck...')
#TODO: periodically cleanup old decks
filepath = userpath + 'WaniKani.apkg'
if os.path.isfile(filepath):
    os.remove(filepath)
wk2a.write_deck_to_file(filepath, deck)
print('All done.')
