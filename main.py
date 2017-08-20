#! /usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.
"""
TODO: mention in genanki documentation that deck ID is POSIX epoch second timestamp, used for determining relative due dates of cards.
TODO: Match Wanki deck.
TODO: Create web interface and core Python library.
TODO: Double check WaniKani SRS to Anki SRS translation.
TODO: Ensure deck updates properly.
TODO: Consider in long term serializing Anki deck instead of WaniKani JSON.
"""
from datetime import datetime
import json
import os
import random

import lib.genanki.genanki as genanki

from anki import Anki
from wanikani import WaniKani
from wanikani2anki import WaniKani2Anki

anki = Anki()
wk = WaniKani()
wk2a = WaniKani2Anki(wk, anki)

general_cache_path = 'cache/general/'
if not os.path.isdir(general_cache_path): os.makedirs(general_cache_path)

# username = input('Username: ')
username = 'bbucommander'
userpath = 'cache/users/{}/'.format(username)

user = {}
userfile = userpath + '/user.json'
if os.path.isfile(userfile):
    with open(userfile, 'r') as f:
        user = json.load(f)
else:
    user['apikey'] = input('WaniKani API V2 key (not V1!): ')
    user['ids'] = {
        'deck': anki.generate_id(),
        'options': anki.generate_id(),
    }
    user['ids'].update(
        {subject:anki.generate_id() for subject in wk2a.wk.subjects})

headers = {}
headers['Authorization'] = 'Token token=' + user['apikey']

try: user['wanikani'] = wk.get_from_api('userdata', '/user', headers)
except URLError:
    #TODO: Check URL error to determine exact cause, i.e. net down, etc.
    print('Invalid API V2 key: ' + user['apikey'])
    print('Please double check the key. It is stored in: ' + user['apikey'])
    exit()

if username != user['wanikani']['data']['username']:
    print('Warning: username mismatch!')
    print("Locally cached username: '{}'".format(username))
    print("Username reported by WaniKani: '{}'.".format(user['wanikani']['data']['username']))
    response = ''
    while (response != 'y' and response != 'n'):
        response = input('Do you wish to continue? [Y/N] ')
        response = response.lower()
    if response == 'n': exit()

if not os.path.isfile(userfile):
    if not os.path.isdir(userpath):
        os.makedirs(userpath)
    with open(userfile, 'w+') as f:
        json.dump(user, f)

print("""Fetching information for
      user:  {username}
      level: {level}
    """.format(**user['wanikani']['data']))

data = {}
for subject in wk.subjects:
    data[subject] = wk.get(subject + '-subjects', '/subjects?type={}'.format(subject), headers, general_cache_path)
    data[subject]['data'].sort(key=lambda x: x['id'])

    # Merge subjectable data into subject data to recreate unified
    # object data of WaniKani API V1.
    for subjectable in ('study_materials', 'review_statistics', 'assignments'):
        subdata = wk.get(
            '{}-{}'.format(subject, subjectable),
            '/{}?subject_type={}'.format(subjectable, subject), headers, userpath)
        subdata['data'].sort(key=lambda x: x['data']['subject_id'])

        datumiter = iter(data[subject]['data'])
        datum = next(datumiter)
        for subdatum in subdata['data']:
            while datum['id'] != subdatum['data']['subject_id']:
                try: datum = next(datumiter)
                except StopIteration: print('Error: Could not find subject id {}. Aborting.'.format(subdatum['data']['subject_id']))
            datum['data'].update(subdatum['data'])

# print(data['vocabulary']['data'][0])
# print(next(x for x in data['radical']['data'] if x['id'] == 8762))

cards = anki.import_card_definitions('cards/cards.yaml')
with open('cards/wanikani.css', 'r') as f:
    css = f.read()

models = {}
for subject, model in cards.items():
    models[subject] = genanki.Model(
        user['ids'][subject],
        'WaniKani ' + subject.title(),
        fields=model['fields'],
        templates=model['templates'],
        css=css)

options = genanki.OptionsGroup(user['ids']['options'], 'WaniKani')
options.new_steps = [1, 10, 4 * 60, 8 * 60]
options.new_cards_per_day = 20
options.max_reviews_per_day = 200
options.starting_ease = 2250
options.new_bury_related_cards = False
options.review_bury_related_cards = False

deck = genanki.Deck(
    user['ids']['deck'],
    'WaniKani',
    options)
deck.description = r'Your personalized WaniKani Anki deck. \nGenerated on {}.'.format(deck.creation_time.date().isoformat())

# Sort subject data by level to make building deck in level-order easier.
for subject in wk.subjects:
    data[subject]['data'] = sorted(
        data[subject]['data'], key=lambda x: x['data']['level'])

datum_iter = {subject:iter(data[subject]['data']) for subject in wk.subjects}
datum_dict = {subject:next(datum_iter[subject]) for subject in wk.subjects}
for level in range(1,61):
    for subject in wk.subjects:
        model = models[subject]
        fields_translator = wk2a.fields_translators[subject]
        datum = datum_dict[subject]
        while True:
            if datum['data']['level'] != level:
                # Note: Some levels 51-60 contain no radicals.
                datum_dict[subject] = datum
                break

            try:
                note = wk2a.create_anki_note(datum['data'], model, subject)
                deck.add_note(note)
            except Exception:
                print(datum['data'])
                print('Failed to translate the above WaniKani data to Anki.'
                      ' Aborting.')
                raise

            try:
                datum = next(datum_iter[subject])
            except StopIteration:
                break


print('Writing deck...')
filename = userpath + 'WaniKani.apkg'
#TODO: periodically cleanup old decks
if os.path.isfile(filename):
    os.remove(filename)
genanki.Package(deck).write_to_file(filename)
print('All done.')
