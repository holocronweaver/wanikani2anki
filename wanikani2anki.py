# This Source Code Form is subject to the terms of the Mozilla Public
# License, v2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.
from functools import reduce
from datetime import datetime, timedelta

import lib.genanki.genanki as genanki

class WaniKani2Anki:
    """Translate from WaniKani API data to Anki card type data."""

    def __init__(self, wanikani, anki):
        self.wk = wanikani
        self.anki = anki

        self.fields_translators = {
            'radical': self.translate_radical,
            'kanji': self.translate_kanji,
            'vocabulary': self.translate_vocabulary
        }

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
    def check_existence(self, data, key):
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
            'Note': self.check_existence(data, 'meaning_note'),
            'Level': str(data['level']),
        }
        return fields
    def translate_kanji(self, data):
        fields = {
            'Characters': data['character'],
            'Meanings': self.combine_meanings(
                data['meanings'],
                data['meaning_synonyms'] if 'meaning_synonyms' in data else None),
            'Meaning Note': self.check_existence(data, 'meaning_note'),
            'Onyomi': self.get_kanji_readings('Onyomi', data['readings']),
            'Kunyomi': self.get_kanji_readings('Kunyomi', data['readings']),
            'Nanori': self.get_kanji_readings('Nanori', data['readings']),
            'Reading Note': self.check_existence(data, 'reading_note'),
            'Level': str(data['level']),
        }
        return fields
    def translate_vocabulary(self, data):
        fields = {
            'Characters': data['characters'],
            'Meanings': self.combine_meanings(
                data['meanings'],
                data['meaning_synonyms'] if 'meaning_synonyms' in data else None),
            'Meaning Note': self.check_existence(data, 'meaning_note'),
            'Readings': ', '.join(
                [x['reading'] for x in sorted(
                    data['readings'],
                    key=lambda x: x['primary'], reverse=True)]),
            'Reading Note': self.check_existence(data, 'reading_note'),
            'Level': str(data['level']),
        }
        return fields

    def translate_srs(self, data, deck):
        """Translate WaniKani SRS data to Anki SRS data."""
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
            anki_srs['reps_til_grad'] = 3 - wk_srs_stage

            due = datetime.strptime(data['available_at'], wk.timestamp_fmt)
            anki_srs['due'] = due.timestamp()
        elif wk_srs_stage < 9: # review
            anki_srs['stage'] = 2
            anki_srs['interval'] = wk.srs_stage_to_days[wk_srs_stage]
            anki_srs['ease'] = deck.options.starting_ease

            due = datetime.strptime(data['available_at'], wk.timestamp_fmt)
            relative_due = due - deck.creation_time
            anki_srs['due'] = relative_due.days
        else: # burned
            anki_srs['stage'] = 2
            #TODO: Let user customize this, and maybe other stage translations.
            anki_srs['interval'] = 5 * 365
            anki_srs['ease'] = deck.options.starting_ease

            farfuture = datetime.strptime(data['burned_at'], wk.timestamp_fmt)
            farfuture += timedelta(days=5 * 365)
            farfuture -= deck.creation_time
            anki_srs['due'] = farfuture.days
        return anki_srs

    def create_anki_note(self, subject, model, fields_dict, srs):
        """Create Anki note from translated WaniKani data using genanki.
        This translates from internal representation to genanki
        representation so that genanki could be replaced if needed."""
        fields = [fields_dict[field['name']] for field in model.fields]

        note = genanki.Note(model=model, fields=fields)
        note.guid = genanki.guid_for(
            *[fields_dict['Characters'], subject])

        note.stage = srs['stage']
        if note.stage == 0: # new
            pass
        elif note.stage == 1: # learning
            note.due = srs['due']
            note.interval = srs['interval']
            note.reps_til_grad = srs['reps_til_grad']
        elif note.stage == 2: # review
            note.due = srs['due']
            note.interval = srs['interval']
            note.ease = srs['ease']
        else:
            raise ValueError('Illegal SRS level: ' + note.level)

        return note
