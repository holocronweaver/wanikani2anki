# This Source Code Form is subject to the terms of the Mozilla Public
# License, v2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.
import copy
from datetime import datetime, timedelta
from functools import reduce
import glob
import os
import yaml

import genanki

from .anki import Anki
from .wanikani import WaniKani

class WaniKani2Anki:
    """Create an Anki deck from WaniKani data."""

    def __init__(self):
        self.wk = WaniKani()
        self.anki = Anki()

        self.options = self.load_options()

        self.media = self.get_media(self.options['media formats'],
                                    self.options['media dir'])

        self.fields_translators = {
            'radicals': self.translate_radical,
            'kanji': self.translate_kanji,
            'vocabulary': self.translate_vocabulary
        }

    def get_user(self, apikey=None):
        if not apikey:
            apikey = self.options['api key']
        return self.wk.get_user(apikey, self.options['users cache'])

    def get_data(self, user):
        return self.wk.get_data(user, self.options['general cache'])

    def write_deck_to_file(self, deck, filepath, override=False):
        if override and os.path.isfile(filepath):
            os.remove(filepath)
        genanki.Package(deck, self.media).write_to_file(filepath)

    def cancel_download(self):
        self.wk.cancel_download()


    def combine_meanings(self, wk, user):
        """First WaniKani then user meanings in a comma-delim string."""
        wk_sort = sorted(wk, key=lambda x: x['primary'], reverse=True)
        wk_sort = [m['meaning'] for m in wk_sort]
        return ', '.join(wk_sort + user) if user else ', '.join(wk_sort)
    def get_kanji_readings(self, kind, readings):
        """Get list of readings of particular kind (onyomi, kunyomi, nanori)
        from WaniKani kanji readings, ordering primary reading first."""
        reading = filter(lambda x: x['type'] == kind, readings)
        reading = sorted(reading, key=lambda x: x['primary'], reverse=True)
        reading = [r['reading'] for r in reading]
        return ', '.join(reading)
    def get_mnemonic(self, field, data):
        """Join mnemonic and its hint using '::hint::', which can be further
        parsed and formatted in-card using JavaScript."""
        if not self.check_existence(field, data):
            return ''
        else:
            if type(data[field]) is list:
                return '::hint::'.join(data[field])
            else: #TODO: Check no longer needed once scraping redone.
                return data[field]
    def check_existence(self, key, data):
        """Return empty string unless key exists in map and its value is not
        None."""
        if key in data: return data[key] if data[key] else ''
        else: return ''

    def translate_radical(self, data):
        fields = {
            #TODO: Handle radicals without unicode values.
            'Characters': data['character'] if data['character'] else 'FIXME',
            'Meanings': self.combine_meanings(
                data['meanings'],
                data['meaning_synonyms'] if 'meaning_synonyms' in data else None),
            'Note': self.check_existence('meaning_note', data),
            'Meaning Mnemonic': self.get_mnemonic('Meaning Mnemonic', data),
            'Level': str(data['level']),
        }
        return fields
    def translate_kanji(self, data):
        fields = {
            'Characters': data['character'],
            'Meanings': self.combine_meanings(
                data['meanings'],
                data['meaning_synonyms'] if 'meaning_synonyms' in data else None),
            'Meaning Note': self.check_existence('meaning_note', data),
            'Onyomi': self.get_kanji_readings('Onyomi', data['readings']),
            'Kunyomi': self.get_kanji_readings('Kunyomi', data['readings']),
            'Nanori': self.get_kanji_readings('Nanori', data['readings']),
            'Reading Note': self.check_existence('reading_note', data),
            'Meaning Mnemonic': self.get_mnemonic('Meaning Mnemonic', data),
            'Reading Mnemonic': self.get_mnemonic('Reading Mnemonic', data),
            'Level': str(data['level']),
        }
        return fields
    def translate_vocabulary(self, data):
        context_sentences = ''
        if 'Context Sentences' in data:
            context_sentences = '::context::'.join(
                ['::translation::'.join(pair) for pair in data['Context Sentences']])

        audio = ''
        if self.options['enable audio'] and 'Audio' in data:
            audio = '[sound:{}]'.format(data['Audio'])

        fields = {
            'Characters': data['characters'],
            'Meanings': self.combine_meanings(
                data['meanings'],
                data['meaning_synonyms'] if 'meaning_synonyms' in data else None),
            'Meaning Note': self.check_existence('meaning_note', data),
            'Readings': ', '.join(
                [x['reading'] for x in sorted(
                    data['readings'],
                    key=lambda x: x['primary'], reverse=True)]),
            'Reading Note': self.check_existence('reading_note', data),
            'Audio': audio,
            'Context Sentences': context_sentences,
            'Meaning Explanation': self.get_mnemonic('Meaning Explanation', data),
            'Reading Explanation': self.get_mnemonic('Reading Explanation', data),
            'Level': str(data['level']),
        }
        return fields

    def translate_srs(self, data, deck):
        """Translate WaniKani SRS data to Anki SRS data."""
        #TODO: Let user further customize stage translations?
        wk = self.wk
        wk_srs_stage = data['srs_stage'] if 'srs_stage' in data else 0
        anki_srs = {}
        if wk_srs_stage == 0: # new
            anki_srs['stage'] = 0
        elif wk_srs_stage < 3: # learning
            #TODO: Probably should set deck learning steps to match WaniKani.
            anki_srs['stage'] = 1
            anki_srs['interval'] = -int(
                60 * 60 * 24 * wk.srs_stage_to_days[wk_srs_stage])
            anki_srs['reps_left_til_grad'] = 3 - wk_srs_stage

            due = datetime.strptime(data['available_at'], wk.timestamp_fmt)
            anki_srs['due'] = due.timestamp()
        elif wk_srs_stage < 9: # review
            anki_srs['stage'] = 2
            anki_srs['interval'] = wk.srs_stage_to_days[wk_srs_stage]
            anki_srs['ease_factor'] = deck.options.starting_ease

            due = datetime.strptime(data['available_at'], wk.timestamp_fmt)
            relative_due = due - deck.creation_time
            anki_srs['due'] = relative_due.days
            anki_srs['status'] = 0
        else: # burned
            anki_srs['stage'] = 2
            if self.options['burn years']:
                anki_srs['interval'] = int(self.options['burn years'] * 365)

                farfuture = datetime.strptime(data['burned_at'], wk.timestamp_fmt)
                farfuture += timedelta(days=anki_srs['interval'])
                farfuture -= deck.creation_time
                anki_srs['due'] = farfuture.days
                anki_srs['status'] = 0
            else:
                anki_srs['interval'] = 0
                anki_srs['due'] = 0
                # Suspended, requires manual unsuspension.
                anki_srs['status'] = 1

            anki_srs['ease_factor'] = deck.options.starting_ease
        return anki_srs

    def create_anki_note(self, datum, deck, model, subject):
        """Create Anki note from translated WaniKani data using genanki.
        This translates from internal representation to genanki
        representation so that genanki could be replaced if needed."""
        fields_dict = self.fields_translators[subject](datum)
        srs = self.translate_srs(datum, deck)

        fields = [fields_dict[field['name']] for field in model.fields]

        note = genanki.Note(model=model, fields=fields)
        note.guid = genanki.guid_for(
            *[fields_dict['Characters'], subject])
        note.tags = ['WKLevel_' + fields_dict['Level']]
        note.set_card_options(srs)

        return note

    def create_deck_options(self, user):
        """Create an Anki options group that mimics the WaniKani SRS
        algorithm."""
        options = genanki.OptionsGroup(
            user['ids']['options'], 'WaniKani',
            new_steps = [1, 10, 4 * 60, 8 * 60],
            new_cards_per_day = 20,
            max_reviews_per_day = 200,
            starting_ease = 2250,
            bury_related_new_cards = False,
            bury_related_review_cards = False,
        )

        return options

    def create_models(self, user):
        """Create WaniKani card models for an Anki deck."""
        cards = self.anki.import_card_definitions('cards/cards.yaml')
        with open('cards/wanikani.css', 'r') as f:
            css = f.read()

        models = {}
        if self.options['separate meaning and reading']:
            f = lambda x: not 'and' in x['name']
        else:
            f = lambda x: 'and' in x['name']
        for subject, model in cards.items():
            templates = copy.deepcopy(model['templates'])
            if not 'radical' in subject:
                templates = list(filter(f, templates))

            models[subject] = genanki.Model(
                user['ids'][subject],
                'WaniKani ' + subject.title(),
                fields=model['fields'],
                templates=templates,
                css=css)
        return models

    def create_deck(self, user, data, deck_options=None):
        """Create Anki deck from WaniKani data."""
        if not deck_options:
            deck_options = self.create_deck_options(user)

        deck = genanki.Deck(
            user['ids']['deck'],
            'WaniKani',
            deck_options)
        deck.description = r'Your personalized WaniKani Anki deck. \nGenerated on {}.'.format(deck.creation_time.date().isoformat())

        models = self.create_models(user)

        # Sort subject data by level to make building deck in level-order easier.
        for subject in self.wk.subjects:
            data[subject]['data'] = sorted(
                data[subject]['data'], key=lambda x: x['data']['level'])

        datum_iter = {subject:iter(data[subject]['data'])
                      for subject in self.wk.subjects}
        datum_dict = {subject:next(datum_iter[subject])
                      for subject in self.wk.subjects}
        for level in range(1,61):
            for subject in self.wk.subjects:
                model = models[subject]
                fields_translator = self.fields_translators[subject]
                datum = datum_dict[subject]
                while True:
                    if datum['data']['level'] != level:
                        # Note: Some levels 51-60 contain no radicals.
                        datum_dict[subject] = datum
                        break

                    try:
                        note = self.create_anki_note(
                            datum['data'], deck, model, subject)
                        deck.add_note(note)
                    except Exception:
                        print(datum['data'])
                        print('Failed to translate the above WaniKani data to Anki. Aborting.')
                        raise

                    try:
                        datum = next(datum_iter[subject])
                    except StopIteration:
                        break

        return deck

    def get_media(self, media_formats, media_dir):
        """Get list of media files from the formats dict and media path."""
        if not os.path.isdir(media_dir):
            if os.path.isfile(media_dir):
                raise ValueError('Media path is a file, not a directory: ' + media_dir)
            else:
                raise ValueError('Media path does not exist: ' + media_dir)

        media = []
        for medium, options in media_formats.items():
            format_path = os.path.join(media_dir, options['subdir'])
            format_regex = os.path.join(
                format_path, '*.' + options['ext'])
            media += glob.glob(format_regex)

        return media

    def load_options(self):
        with open('options.yaml', 'r') as f:
            options = yaml.load(f)
        deck_type = options['deck type']
        options.update(options['deck types'][deck_type])
        return options

    @property
    def download_progress(self):
        return self.wk.download_progress
