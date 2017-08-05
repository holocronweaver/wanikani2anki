#! /usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.
import json
from urllib.request import *

headers = {}
with open('apikey.txt', 'r') as f:
    apikey = f.readline().strip()
    headers['Authorization'] = 'Token token=' + apikey

rooturl = 'https://www.wanikani.com/api/v2'

request = Request(rooturl + '/user', headers=headers)
response = urlopen(request)
print(response.getcode())
print(response.info())
user = json.loads(response.read().decode())
print(user)
