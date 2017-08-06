#! /usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.
"""
TODO: User-independent cache.
TODO: Per-user cache.
TODO: One model per subject.
TODO: Consider in long term serializing Anki deck instead of WaniKani JSON.
"""
import yaml

from wanikani import *

wk = WaniKani()

headers = {}
apikey = ''
if os.path.isfile('apikey.txt'):
    with open('apikey.txt', 'r') as f:
        apikey = f.readline().strip()
        headers['Authorization'] = 'Token token=' + apikey
else:
    apikey = input('WaniKani API V2 key (not V1!): ')

try: user = wk.get_from_api('userdata', '/user', headers)
except URLError: print('Invalid API V2 key!'); exit()

path = 'cache/{}/'.format(user['data']['username'])

if not os.path.isfile('apikey.txt'):
    with open('apikey.txt', 'w+') as f:
        f.write(apikey)

print("""Fetching information for
      user:  {username}
      level: {level}
    """.format(**user['data']))

data = {}
for subject in ('radical', 'kanji', 'vocabulary'):
    data[subject] = wk.get(subject, '/subjects?type={}'.format(subject), headers, path)
    data[subject]['data'].sort(key=lambda x: x['id'])

    # Merge subjectable data into subject data to recreate unified
    # object data of WaniKani API V1.
    # for subjectable in ('study_materials', 'review_statistics', 'assignments'):
    for subjectable in ('review_statistics', 'assignments'):
        subdata = wk.get(
            '{}-{}'.format(subject, subjectable),
            '/{}?subject_type={}'.format(subjectable, subject), headers, path)
        subdata['data'].sort(key=lambda x: x['data']['subject_id'])

        datumiter = iter(data[subject]['data'])
        datum = next(datumiter)
        for subdatum in subdata['data']:
            while datum['id'] != subdatum['data']['subject_id']:
                try: datum = next(datumiter)
                except StopIteration: print('Error: Could not find subject id {}. Aborting.'.format(subdatum['data']['subject_id']))
            datum['data'].update(subdatum['data'])

print(data['vocabulary']['data'][0])

with open('cards.yaml', 'r') as f:
    cards = f.read()
    cards = yaml.load(cards)
with open('wanikani.css','r') as f:
    css = f.read()

model = genanki.Model(
    1108933879,
    'WaniKani',
    fields=cards['fields'],
    templates=cards['templates'],
    css=css)

deck = genanki.Deck(
    1970043342,
    'WaniKani')

filename = path + 'WaniKani.apkg'
if os.path.isfile(filename):
    os.remove(filename)

for subject in ('radical', 'kanji', 'vocabulary'):
    characters_key = 'character' if subject != 'vocabulary' else 'characters'
    for datum in data[subject]['data']:
        try:
            characters = datum['data'][characters_key]
            if not characters: characters = 'FIXME'
            meaning = next(m['meaning'] for m in datum['data']['meanings'] if m['primary'])
            if subject != 'radical':
                reading = next(m['reading'] for m in datum['data']['readings'] if m['primary'])
            else:
                reading = 'none'
        except Exception:
            print(datum['data'])
            raise
        fields = [characters, meaning, reading]
        note = genanki.Note(model=model, fields=fields)
        deck.add_note(note)

genanki.Package(deck).write_to_file(filename)
