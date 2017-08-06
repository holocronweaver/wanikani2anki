"""Translate from WaniKani API data to Anki card type data.
"""
from functools import reduce

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
