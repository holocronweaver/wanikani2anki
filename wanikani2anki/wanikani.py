# This Source Code Form is subject to the terms of the Mozilla Public
# License, v2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.
import json
import os
from urllib.error import *
from urllib.request import *

class WaniKani:
    rooturl = 'https://www.wanikani.com/api/v2'
    subjects = ('radical', 'kanji', 'vocabulary')
    srs_stage_to_days = [0, 4/24, 8/24, 1, 3, 7, 14, 28, 56]
    timestamp_fmt = '%Y-%m-%dT%H:%M:%SZ'

    def get_json(self, request, description):
        """Make a GET request and return resulting JSON."""
        try: response = urlopen(request)
        except URLError as error:
            print('Error while fetching {}: {}'.format(description, error.reason))
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
            pages.append(self.get_json(request, type))
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
        filename = path + resource + '.json'
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

    def get_data(self, user, userpath, general_cache_path):
        """Gather all WaniKani data for user.
        Data is downloaded/updated as necessary from the web and
        cached for future use."""
        headers = self.create_headers(user)
        data = {}
        for subject in self.subjects:
            data[subject] = self.get(
                subject + '-subjects',
                '/subjects?type={}'.format(subject),
                headers, general_cache_path)
            data[subject]['data'].sort(key=lambda x: x['id'])

            # Merge subjectable data into subject data to recreate unified
            # object data of WaniKani API V1.
            for subjectable in ('study_materials', 'review_statistics', 'assignments'):
                subdata = self.get(
                    '{}-{}'.format(subject, subjectable),
                    '/{}?subject_type={}'.format(subjectable, subject),
                    headers, userpath)
                subdata['data'].sort(key=lambda x: x['data']['subject_id'])

                datumiter = iter(data[subject]['data'])
                datum = next(datumiter)
                for subdatum in subdata['data']:
                    while datum['id'] != subdatum['data']['subject_id']:
                        try: datum = next(datumiter)
                        except StopIteration: print('Error: Could not find subject id {}. Aborting.'.format(subdatum['data']['subject_id']))
                    datum['data'].update(subdatum['data'])
        return data

    def create_headers(self, user):
        headers = {}
        headers['Authorization'] = 'Token token=' + user['apikey']
        return headers

    def get_user(self, username, userpath):
        user = {}
        userfile = userpath + '/user.json'
        if os.path.isfile(userfile):
            with open(userfile, 'r') as f:
                user = json.load(f)
        else:
            user['apikey'] = input('WaniKani API V2 key (not V1!): ')
            user['ids'] = {
                'deck': self.anki.generate_id(),
                'options': self.anki.generate_id(),
            }
            user['ids'].update(
                {subject:self.anki.generate_id()
                 for subject in self.wk.subjects})

        headers = self.create_headers(user)

        try: user['wanikani'] = self.get_from_api('userdata', '/user', headers)
        except URLError:
            #TODO: Check URL error to determine exact cause, i.e. net down, etc.
            #TODO: Pass error to user.
            print('Invalid API V2 key: ' + user['apikey'])
            print('Please double check the key. It is stored in: ' + user['apikey'])
            exit()

        if username != user['wanikani']['data']['username']:
            print('Warning: username mismatch!')
            print("Locally cached username: '{}'".format(username))
            print("Username reported by WaniKani: '{}'.".format(user['wanikani']['data']['username']))
            #TODO: Pass error to user.
            response = ''
            while (response != 'y' and response != 'n'):
                response = input('Do you wish to continue? [Y/N] ')
                response = response.lower()
            if response == 'n': exit()

        if not os.path.isfile(userfile):
            if not os.path.isdir(userpath):
                #TODO: Let user handle this?
                os.makedirs(userpath)
            with open(userfile, 'w+') as f:
                json.dump(user, f)

        return user
