#! /usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.
"""
TODO: Translate WaniKani SRS to Anki SRS.
TODO: Generate non-user specific note & card IDs. Do not cache.
TODO: Match Wanki deck.
TODO: Create web interface and core Python library.
TODO: Consider in long term serializing Anki deck instead of WaniKani JSON.
"""
import random
import yaml

from translators import *
from wanikani import *

def generate_id():
    """Generate a 32-bit ID useful for Anki."""
    return random.randrange(1 << 30, 1 << 31)

wk = WaniKani()

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
        'deck': generate_id(),
        'options': generate_id(),
    }
    user['ids'].update({subject:generate_id() for subject in wk.subjects})

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

with open('cards.yaml', 'r') as f:
    cards = f.read()
    cards = yaml.load(cards)
with open('wanikani.css','r') as f:
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
deck = genanki.Deck(
    user['ids']['deck'],
    'WaniKani',
    options)
# TODO: adjust genanki deck srs settings.

deck.options = options

filename = userpath + 'WaniKani.apkg'
#TODO: periodically cleanup old decks
if os.path.isfile(filename):
    os.remove(filename)

for subject in wk.subjects:
    data[subject]['data'] = sorted(
        data[subject]['data'], key=lambda x: x['data']['level'])

datum_iter = {subject:iter(data[subject]['data']) for subject in wk.subjects}
datum_dict = {subject:next(datum_iter[subject]) for subject in wk.subjects}
for level in range(1,61):
    for subject in wk.subjects:
    # for subject in ('radical',):
        model = models[subject]
        translator = translators[subject]
        datum = datum_dict[subject]
        while True:
            if datum['data']['level'] != level:
                datum_dict[subject] = datum
                break

            try:
                fields_dict = translator(datum['data'])
                fields = [fields_dict[field['name']] for field in model.fields]

                srs = srs_translator(datum['data'], wk)
            except Exception:
                print(datum['data'])
                print('Failed to translate the above WaniKani data.')
                raise
            # if fields[2] == '':
            #     continue
            #     # print(datum)
            #     # print(fields)
            #     # exit()

            #TODO: Create note ids using subject (i.e. non-user
            # specific) data.

            note = genanki.Note(model=model, fields=fields)
            deck.add_note(note)

            try:
                datum = next(datum_iter[subject])
            except StopIteration:
                # Some levels within 51-60 contain no radicals.
                break


print('Writing deck...')
genanki.Package(deck).write_to_file(filename)
print('All done')
