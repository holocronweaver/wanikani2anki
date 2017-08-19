# This Source Code Form is subject to the terms of the Mozilla Public
# License, v2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.
from setuptools import setup

setup(name='wanikani2anki',
      version='0.1',
      description='Convert WaniKani data to Anki decks',
      url='http://github.com/holocronweaver/wanikani2anki',
      author='Jesse Johnson',
      # author_email = '',
      license='MPL-2.0',
      packages=['wanikani2anki'],
      zip_safe=False,
      install_requires=[
        'genanki'
      ],
      keywords=[
        'anki',
        'flashcards',
        'memorization',
        'wanikani'
      ])
