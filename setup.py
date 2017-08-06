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
