#! /usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.
"""
TODO: Translate WaniKani SRS to Anki SRS.
TODO: User-independent cache.
TODO: Per-user cache.
TODO: Consider in long term serializing Anki deck instead of WaniKani JSON.
TODO: On first run generate deck, note and card IDs. Cache for use on subsequent runs.
"""
import yaml

from translators import *
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
    for subjectable in ('study_materials', 'review_statistics', 'assignments'):
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
# print(next(x for x in data['radical']['data'] if x['id'] == 8762))

with open('cards.yaml', 'r') as f:
    cards = f.read()
    cards = yaml.load(cards)
with open('wanikani.css','r') as f:
    css = f.read()

models = {}
for subject, model in cards.items():
    models[subject] = genanki.Model(
        model['id'],
        'WaniKani ' + subject.title(),
        fields=model['fields'],
        templates=model['templates'],
        css=css)

deck = genanki.Deck(
    1970043342, # random.randrange(1 << 30, 1 << 31)
    'WaniKani')
# TODO: adjust genanki deck srs settings.

filename = path + 'WaniKani.apkg'
if os.path.isfile(filename):
    os.remove(filename)

for subject in ('radical', 'kanji', 'vocabulary'):
    data[subject]['data'] = sorted(
        data[subject]['data'], key=lambda x: x['data']['level'])

datum_iter = {
    'radical': iter(data['radical']['data']),
    'kanji': iter(data['kanji']['data']),
    'vocabulary': iter(data['vocabulary']['data']),
}
datum_dict = {
    'radical': next(datum_iter['radical']),
    'kanji': next(datum_iter['kanji']),
    'vocabulary': next(datum_iter['vocabulary']),
}
for level in range(1,61):
    for subject in ('radical', 'kanji', 'vocabulary'):
    # for subject in ('radical',):
        model = models[subject]
        translator = translators[subject]
        datum = datum_dict[subject]
        while True:
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

            note = genanki.Note(model=model, fields=fields)
            deck.add_note(note)

            try:
                datum = next(datum_iter[subject])
                if datum['data']['level'] != level:
                    datum_dict[subject] = datum
                    break
            except StopIteration:
                print('Done with {}.'.format(subject))
                break


genanki.Package(deck).write_to_file(filename)
