#! /usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.
"""Scrape WaniKani for audio, context sentences, and mnemonics.

This should ONLY be used for aiding private study, such as creating an
offline Anki deck so you can continue studying when Internet access is
unavailable.

All the usual rules of scraping etiquette apply. Run the script during
off hours and no more than once a year to reduce any impact on the WK
servers. Possibly only do one subject a night. The script already
spaces page visits by 5-15 seconds.

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

By default this script saves partial results to disk every 500 items,
saving roughly every 1.3 hours, and will automatically reuse any saved
partial results the next time the script is run.
"""
from datetime import datetime
import os
import random
import time

from bs4 import BeautifulSoup

from webdriver import *
from scrapers import *

from wanikani2anki import WaniKani, WaniKani2Anki

from scrape_options import *

wk = WaniKani()
wk2a = WaniKani2Anki(wk)

user = wk.get_user(username, userpath)

data = wk.get_data(user, userpath, general_cache_path)

# Scrape!
driver = WebDriver(firefox_profile, audio_path, [formats['audio']])
sleep_offsets = {'radicals': 0, 'kanji': 0, 'vocabulary': -5}

for subject in subjects:
    scraper = scrapers[subject](
        '{}/{}-scrape.json'.format(general_cache_path, subject),
        driver, formats)

    get_sleep_time = lambda: 10 + 3 * (random.random() * 2 - 1) + sleep_offsets[subject]

    log = open('{}/{}-scrape.log'.format(general_cache_path, subject), 'a')

    # For restoring, find last index that was serialized.
    resumeindex = -1
    if scraper.lastid_before_resume > -1:
        for i in range(len(data[subject]['data'])):
            wk_datum = data[subject]['data'][i]
            if wk_datum['id'] == scraper.lastid_before_resume:
                resumeindex = i
                break

    for wk_datum in data[subject]['data'][resumeindex + 1:]:
        url = wk_datum['data']['document_url']
        url = url.replace(' ', '-') # Fixes radicals with spaces in URL.

        try:
            html = driver.get_html(url)

            soup = BeautifulSoup(html, 'lxml')

            scraper.scrape(wk_datum['id'], soup)
        except Exception:
            characters = wk_datum['data']['character'] if 'character' in wk_datum['data'] else wk_datum['data']['characters']
            msg = '{}:ERROR: Failed to get item: {} id: {} url: {}.\n'.format(
                datetime.now().isoformat(),
                characters, wk_datum['id'], url)
            log.write(msg)
            print(msg)
            continue

        time.sleep(get_sleep_time())
        print('id: {}, data: {}'.format(
            scraper.ids[-1],
            {key: value[-1] for key, value in scraper.data.items()}))

    scraper.serialize()
    log.close()

# For some reason this crashes, but would be nice to close driver.
# driver.quit()
