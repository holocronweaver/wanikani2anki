#! /usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.
"""Scrape WaniKani for audio, context sentences, and mnemonics.

This should ONLY be used for aiding private study, such as creating an
offline Anki deck so you can continue studying when Internet access is
unavailable.

Also, do not run this script more than once and preferably run it
during off hours to reduce any impact on the WK servers. Possibly only
do one subject a night. The script already spaces page visits by 5-15
seconds.

A complete download takes about 23 hours:
radicals: 1.3 hours
kanji: 5.3 hours
vocabulary: 16.7 hours

Requires a dummy Firefox profile which has logged into the WaniKani
website, as well as the geckodriver executable to be in PATH.

geckodriver can be obtained from:
https://github.com/mozilla/geckodriver/releases

Note that selenium opens a browser window and 'drives' it
programatically. I know of no convenient cross-platform method of
hiding the browser window.
"""
from datetime import datetime
import json
import os
import random
import time

from bs4 import BeautifulSoup

from webdriver import *

from wanikani2anki import WaniKani, WaniKani2Anki

#BEGIN USER CONFIGURABLE OPTIONS
subjects = ['radicals', 'kanji', 'vocabulary']
# subjects = ['kanji']

general_cache_path = 'cache/general/'

audio_path = os.path.abspath(general_cache_path + 'audio/')
if not os.path.isdir(audio_path): os.makedirs(audio_path)
audio_format = 'audio/' + 'mpeg' # or 'ogg'

firefox_profile = '/home/jesse/.mozilla/firefox/1crm9gtr.crawl/'

# WaniKani config.
username = 'bbucommander'
userpath = 'cache/users/{}/'.format(username)
#END USER CONFIGURABLE OPTIONS

wk = WaniKani()
wk2a = WaniKani2Anki(wk)

user = wk.get_user(username, userpath)

data = wk.get_data(user, userpath, general_cache_path)

# Scrape!
driver = WebDriver(firefox_profile, audio_path, [audio_format])
scraped_data = {}
sleep_offsets = {'radicals': 0, 'kanji': 0, 'vocabulary': -5}

def get_mnemonic(field, soup, scrape_dict):
    h2 = soup.find('h2', string=field)
    p = h2.parent.p
    if len(p.contents):
        scrape_dict[field] = ''.join([child.string for child in p.contents])
    else:
        scrape_dict[field] = p.string
def scrape_radical(soup):
    scraped = {}
    get_mnemonic('Name Mnemonic', soup, scraped)
    return scraped
def scrape_kanji(soup):
    scraped = {}
    get_mnemonic('Meaning Mnemonic', soup, scraped)
    get_mnemonic('Reading Mnemonic', soup, scraped)
    return scraped
def scrape_vocabulary(soup):
    scraped = {}
    # Context sentences.
    section = soup.find('section', 'context-sentence')
    sentences = []
    for div in section.find_all('div'):
        ja = div.find('p', attrs={'lang': 'ja'})
        en = div.find('p', attrs={'lang': None})
        sentences.append([ja.string, en.string])
    scraped['Context Sentences'] = sentences
    # Mnemonincs.
    get_mnemonic('Meaning Explanation', soup, scraped)
    get_mnemonic('Reading Explanation', soup, scraped)
    # Audio.
    source = soup.find('source', attrs={'type': audio_format})
    audiofile = source['src'].split('/')[-1]
    scraped['Audio'] = audiofile
    try:
        driver.get(source['src'])
    except selenium.common.exceptions.TimeoutException:
        # Navigatig to a page which induces a download in Firefox
        pass

    return scraped

scrapers = {
    'radicals': scrape_radical,
    'kanji': scrape_kanji,
    'vocabulary': scrape_vocabulary
}

for subject in subjects:
    scraped_data[subject] = []
    scraper = scrapers[subject]

    fields_translator = wk2a.fields_translators[subject]

    get_sleep_time = lambda: 10 + 3 * (random.random() * 2 - 1) + sleep_offsets[subject]

    log = open('{}/{}-scrape.log'.format(general_cache_path, subject), 'a')

    for wk_datum in data[subject]['data']:
        datum = fields_translator(wk_datum['data'])

        url = wk_datum['data']['document_url']

        try:
            html = driver.get_html(url)

            soup = BeautifulSoup(html, 'lxml')

            scraped = scraper(soup)
            scraped['id'] = wk_datum['id']
        except Exception:
            msg = '{}:ERROR: Failed to get item: {} id: {} url: {}.\n'.format(
                datetime.now().isoformat(),
                datum['Characters'], wk_datum['id'], url)
            log.write(msg)
            print(msg)
            continue

        scraped_data[subject].append(scraped)
        time.sleep(get_sleep_time())
        print(scraped)

    log.close()


for subject, scraped in scraped_data.items():
    filename = '{}/{}-scrape.json'.format(general_cache_path, subject)
    with open(filename, 'w') as f:
        json.dump(scraped, f)

# For some reason this crashes, but would be nice to close driver.
# driver.quit()
