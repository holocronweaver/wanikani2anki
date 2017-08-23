#! /usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.
"""This script parses the scrape error log and attempts to reparse
any items that failed.

Primarily useful for debugging the scraper by focusing on failed
cases.
"""
from datetime import datetime
import os
import random
import re
import shutil
import time

from bs4 import BeautifulSoup

from webdriver import *
from scrapers import *

from wanikani2anki import WaniKani, WaniKani2Anki

from scrape_options import *

wk = WaniKani()
wk2a = WaniKani2Anki(wk)

user = wk.get_user(username, userpath)

# data = wk.get_data(user, userpath, general_cache_path)

# Scrape!
driver = WebDriver(firefox_profile, audio_path, [formats['audio']])
sleep_offsets = {'radicals': 0, 'kanji': 0, 'vocabulary': -5}

for subject in subjects:
    scraper = scrapers[subject](
        '{}/{}-scrape_cleanup.json'.format(general_cache_path, subject),
        driver, formats)

    get_sleep_time = lambda: 10 + 3 * (random.random() * 2 - 1) + sleep_offsets[subject]

    incompletes = []
    with open('{}/{}-scrape.log'.format(general_cache_path, subject), 'r') as f:
        for line in f.readlines():
            match = re.search(r'item: (.*) id: (.*) url: (.*).$', line)
            incompletes.append({
                'characters': match.group(1),
                'id': int(match.group(2)),
                'url': match.group(3).replace(' ', '-'),
            })

    log = open('{}/{}-scrape_cleanup.log'.format(general_cache_path, subject), 'w')

    for datum in incompletes:
        try:
            html = driver.get_html(datum['url'])

            soup = BeautifulSoup(html, 'lxml')

            datum['id'] = int(datum['id'])
            scraper.scrape(datum['id'], soup)
        except Exception:
            msg = '{}:ERROR: Failed to get item: {} id: {} url: {}.\n'.format(
                datetime.now().isoformat(),
                datum['characters'], datum['id'], datum['url'])
            log.write(msg)
            print(msg)
            raise

        time.sleep(get_sleep_time())
        print('id: {}, data: {}'.format(
            scraper.ids[-1],
            {key: value[-1] for key, value in scraper.data.items()}))

    scraper.serialize()
    log.close()

    # Merge into existing file. Create a backup just in case things go
    # wrong.
    with open(scraper.filename, 'r') as f:
        cleanup = json.load(f)

    filename = '{}/{}-scrape.json'.format(general_cache_path, subject)
    shutil.copy2(filename, filename + '.bk')
    with open(filename, 'r') as f:
        scraped = json.load(f)

    scraped += cleanup
    with open(filename, 'w') as f:
        json.dump(scraped, f)

# For some reason this crashes, but would be nice to close driver.
# driver.quit()
