# This Source Code Form is subject to the terms of the Mozilla Public
# License, v2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.
import copy
import json
import os
from urllib.error import *
from urllib.request import *

import time

class WaniKani:
    rooturl = 'https://www.wanikani.com/api/v2'
    subjects = ('radicals', 'kanji', 'vocabulary')
    srs_stage_to_days = [0, 4/24, 8/24, 1, 3, 7, 14, 28, 56]
    timestamp_fmt = '%Y-%m-%dT%H:%M:%SZ'

    _download_canceled = False
    _download_progress = 0

    def get_json(self, request, description):
        """Make a GET request and return resulting JSON."""
        try: response = urlopen(request)
        except URLError as error:
            print('Error while fetching {}!'.format(description))
            raise error
        # print(response.getcode())
        # print(response.info())
        return json.loads(response.read().decode())

    def get_from_api(self, resource, url_ext, headers):
        """Make a WaniKani API request and return the result.

        Make as many GET requests as needed to obtain all the data for
        a particular WaniKani API request, then merge results.
        """
        data = None
        pages = []
        next_url = self.rooturl + url_ext
        while next_url and next_url != 'null':
            request = Request(next_url, headers=headers)
            pages.append(self.get_json(request, resource))
            if 'pages' in pages[-1]:
                next_url = pages[-1]['pages']['next_url']
            else:
                next_url = None
        data = pages[0]
        for page in pages[1:]:
            data['data'] += page['data']
        return data

    def get(self, resource, url_ext, headers, path, do_update=False):
        """Retrieve cached WaniKani data or, if none, retrieve it via WaniKani API.
        """
        filename = os.path.join(path, resource + '.json')
        if os.path.isfile(filename):
            print(resource + ' has existing JSON cache.')
            with open(filename, 'r') as f:
                 data = json.load(f)

            # Check for updates and update as needed.
            if do_update:
                url_ext_addendum = '&updated_after={}'.format(data['data_updated_at'])
                if '?' not in url_ext: url_ext_addendum[0] = '?'
                url_ext += url_ext_addendum
                update = self.get_from_api(resource, url_ext, headers)
                if int(update['total_count']) > 0:
                    data['data'].update(update['data'])
                    with open(filename, 'w') as f:
                        json.dump(data, f)

            data['from_cache'] = True
        else:
            if not os.path.isdir(path):
                os.makedirs(path)
            data = self.get_from_api(resource, url_ext, headers)
            with open(filename, 'x') as f:
                json.dump(data, f)
            data['from_cache'] = False
        return data

    def get_data(self, user, userpath, general_cache):
        """Gather all WaniKani data for user.
        Data is downloaded/updated as necessary from the web and
        cached for future use.

        Data is a dict of subjects with the following format.

        data = {
          subject: { // radicals, kanji, or vocabular
            somerequest: info,
            morerequest: info,
            ...
            andso: on,
            data: [item1,
                   item2,
                   ...
                   lastitem]
          }
        }
        Each item has all the data for a single radical, kanji, or
        vocab. Items have a structure similar to subject.

        item = {
          somerequest: info,
          morerequest: info,
          ...
          andso: on,
          data: {
            wanikani_data: value,
            more_wanikani_data: value,
            ...
            and_even_more_wanikani_data: value
          }
        }

        The item['data'] field contains all the WaniKani data for
        that item available from the WK API.

        The available fields in item['data'] depend on the subject and
        whether the user has reviewed the item at least once. See the
        WaniKani V2 API for what to expect. Currently all data that
        can be pulled is pulled, so if you can't find what you want
        then most likely the WaniKani API doesn't provide it yet or
        you haven't reviewed the item on WaniKani at least once.
        """
        headers = self.create_headers(user)
        data = {}
        subjectables = (
            'study_materials',
            'review_statistics',
            'assignments',
        )
        items_downloaded = 0
        num_download_items = len(self.subjects)
        num_download_items += len(self.subjects) * len(subjectables)
        pause_secs = 0.25
        for subject in self.subjects:
            if self._download_canceled:
                return None

            data[subject] = self.get(
                subject + '-subjects',
                '/subjects?type={}'.format(subject),
                headers, general_cache)
            data[subject]['data'].sort(key=lambda x: x['id'])

            items_downloaded += 1
            self._download_progress = items_downloaded / num_download_items
            time.sleep(pause_secs)

            errmsg ='Error: Could not find subject id {}. Aborting.'

            # Merge in scrape data for each item, if available.
            scrape_filename = os.path.join(
                general_cache, '{}-scrape.json'.format(subject))
            if os.path.isfile(scrape_filename):
                with open(scrape_filename, 'r') as f:
                    scraped = json.load(f)
                scraped.sort(key=lambda x: x['id'])

                datumiter = iter(data[subject]['data'])
                datum = next(datumiter)
                for subdatum in scraped:
                    while datum['id'] != subdatum['id']:
                        try: datum = next(datumiter)
                        except StopIteration: print(errmsg.format(
                                subdatum['id']))
                    datum['data'].update(subdatum['data'])

            # Merge subjectable data into subject data to recreate unified
            # object data of WaniKani API V1.
            for subjectable in subjectables:
                if self._download_canceled:
                    return None

                subdata = self.get(
                    '{}-{}'.format(subject, subjectable),
                    '/{}?subject_type={}'.format(subjectable, subject),
                    headers, userpath)
                subdata['data'].sort(key=lambda x: x['data']['subject_id'])

                items_downloaded += 1
                self._download_progress = items_downloaded / num_download_items
                time.sleep(pause_secs)

                datumiter = iter(data[subject]['data'])
                datum = next(datumiter)
                for subdatum in subdata['data']:
                    while datum['id'] != subdatum['data']['subject_id']:
                        try: datum = next(datumiter)
                        except StopIteration: print(errmsg.format(
                                subdatum['data']['subject_id']))
                    datum['data'].update(subdatum['data'])
        return data

    def create_headers(self, user):
        headers = {}
        headers['Authorization'] = 'Token token=' + user['apikey']
        return headers

    def get_user(self, apikey, users_cache):
        user = {'apikey': apikey}

        headers = self.create_headers(user)
        try:
            user['wanikani'] = self.get_from_api('userdata', '/user', headers)
        except URLError as e:
            msg = '\nIs your API V2 key correct? {}\n'.format(user['apikey'])
            if e.hasattr(message): e.message += msg
            else: e.message = msg
            raise e

        username = user['wanikani']['data']['username']

        userpath = os.path.join(users_cache, username)
        userfile = os.path.join(userpath, 'user.json')
        if os.path.isfile(userfile):
            with open(userfile, 'r') as f:
                user.update(json.load(f))
        else:
            if not os.path.isdir(userpath): os.makedirs(userpath)

            user['ids'] = {
                'deck': self.anki.generate_id(),
                'options': self.anki.generate_id(),
            }
            user['ids'].update(
                {subject:self.anki.generate_id()
                 for subject in self.wk.subjects})

            with open(userfile, 'w') as f:
                clean_user = copy.deepcopy(user)
                del clean_user['apikey']
                json.dump(clean_user, f)

        return [user, userpath]

    def cancel_download(self):
        self._download_canceled = True

    @property
    def download_progress(self):
        return self._download_progress
