"""Translate from WaniKani API data to Anki card type data.
"""
from functools import reduce
from datetime import datetime, timedelta

def combine_meanings(wk, user):
    """First WaniKani then user meanings in a comma-delim string."""
    wk_sort = sorted(wk, key=lambda x: x['primary'], reverse=True)
    wk_sort = [m['meaning'] for m in wk_sort]
    return ', '.join(wk_sort + user) if user else ', '.join(wk_sort)
def get_reading(kind, wk):
    reading = filter(lambda x: x['type'] == kind, wk)
    reading = sorted(reading, key=lambda x: x['primary'], reverse=True)
    reading = [r['reading'] for r in reading]
    return ', '.join(reading)
def check_existence(data, key):
    if key in data: return data[key] if data[key] else ''
    else: return ''
def get_radical(data):
    return {
        #TODO: Handle radicals without unicode values.
        'Characters': data['character'] if data['character'] else 'FIXME',
        'Meanings': combine_meanings(
            data['meanings'],
            data['meaning_synonyms'] if 'meaning_synonyms' in data else None),
        'Note': check_existence(data, 'meaning_note'),
        'Level': str(data['level']),
    }
def get_kanji(data):
    return {
        'Characters': data['character'],
        'Meanings': combine_meanings(
            data['meanings'],
            data['meaning_synonyms'] if 'meaning_synonyms' in data else None),
        'Meaning Note': check_existence(data, 'meaning_note'),
        'Onyomi': get_reading('Onyomi', data['readings']),
        'Kunyomi': get_reading('Kunyomi', data['readings']),
        'Nanori': get_reading('Nanori', data['readings']),
        'Reading Note': check_existence(data, 'reading_note'),
        'Level': str(data['level']),
    }
def get_vocabulary(data):
    return {
        'Characters': data['characters'],
        'Meanings': combine_meanings(
            data['meanings'],
            data['meaning_synonyms'] if 'meaning_synonyms' in data else None),
        'Meaning Note': check_existence(data, 'meaning_note'),
        'Readings': ', '.join(
            [x['reading'] for x in sorted(
                data['readings'],
                key=lambda x: x['primary'], reverse=True)]),
        'Reading Note': check_existence(data, 'reading_note'),
        'Level': str(data['level']),
    }

translators = {
    'radical': get_radical,
    'kanji': get_kanji,
    'vocabulary': get_vocabulary
}

def srs_translator(data, wanikani):
    """Translate WaniKani SRS data to Anki SRS data."""
    wk_srs_stage = data['srs_stage'] if 'srs_stage' in data else 0
    anki_srs = {}
    if wk_srs_stage == 0: # new
        anki_srs['stage'] = 0
    elif wk_srs_stage < 3: # learning
        #TODO: Probably should set deck learning steps to match WaniKani.
        anki_srs['stage'] = 1
        anki_srs['interval'] = -int(
            60 * 60 * 24 * wanikani.srs_stage_to_days[wk_srs_stage])
        anki_srs['reps_til_grad'] = 3 - wk_srs_stage
        anki_srs['due'] = datetime.strptime(data['available_at'],
                                            wanikani.timestamp_fmt)
    elif wk_srs_stage < 9: # review
        anki_srs['stage'] = 2
        anki_srs['interval'] = wanikani.srs_stage_to_days[wk_srs_stage]
        anki_srs['due'] = datetime.strptime(data['available_at'],
                                            wanikani.timestamp_fmt)
    else: # burned
        anki_srs['stage'] = 2
        #TODO: Let user customize this, and maybe other stage translations.
        anki_srs['interval'] = 5 * 365
        farfuture = datetime.strptime(data['burned_at'],
                                      wanikani.timestamp_fmt)
        farfuture += timedelta(days=5 * 365)
        anki_srs['due'] = farfuture
    return anki_srs
