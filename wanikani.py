# This Source Code Form is subject to the terms of the Mozilla Public
# License, v2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.
import json
import os
from urllib.error import *
from urllib.request import *

import genanki

class WaniKani:
    rooturl = 'https://www.wanikani.com/api/v2'

    srs_stage_to_days = [0, 4/24, 8/24, 1, 3, 7, 14, 28, 56]

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
