import glob
import json
import os

class Scraper:
    lastid_before_resume = -1
    ids = []
    data = {}
    cachesize = 500
    counter = 0
    page = 0
    def __init__(self, subject, path, driver, formats):
        self.subject = subject
        self.path = path
        self.driver = driver # webdriver
        self.formats = formats # dict of formats

        self.filename = '{}/{}-scrape.json'.format(self.path, self.subject)
        self.page_filename = self.filename + '_{:04d}'

        if os.path.isfile(self.filename):
            raise Exception(
                'Cache file {} already exists.'.format(self.filename) \
                + ' Aborting to avoid data overwrite.' \
                + ' Please manually detele file if you wish to replace it.'
            )

        self.restore()
    def scrape(self, wk_id, soup):
        self.ids.append(wk_id)
        self._scrape(soup)
        self.counter += 1
        if self.counter == self.cachesize:
            self._serialize_partial()
    def _scrape(self, soup):
        pass
    def add_mnemonic(self, field, soup):
        h2 = soup.find('h2', string=field)
        p = h2.parent.p
        mnemonic = ''
        if len(p.contents):
            mnemonic = ''.join([child.string for child in p.contents])
        else:
            mnemonic = p.string
        self.data[field].append(mnemonic)
    def restore(self):
        # Find last page of partial results.
        filenames = glob.glob(self.filename + '_*')
        if filenames.empty():
            return # No partial results.
        pages = map(lambda x: int(x.split('_')[1]), filenames)
        pages.sort()
        lastpage = pages[-1]
        # Find last completed ID.
        filename = self.page_filename.format(self.page)
        with open(filename, 'r') as f:
            j = json.load(f)
        self.lastid_before_resume = j[-1]['id']
    def _serialize_partial(self):
        partial = self.to_list_of_dicts()
        filename = self.page_filename.format(self.page)
        with open(filename, 'w') as f:
            json.dump(partial, f)

        self.page += 1
        self.counter = 0
        self.ids = []
        self.data = {key:[] for key in data.keys()}
    def serialize(self):
        merged = []
        # Merge partial results with current.
        for filename in glob.glob(self.filename + '_*'):
            with open(filename, 'r') as f:
               merged += json.load(f)
        merged += self.to_list_of_dicts()

        with open(self.filename, 'w') as f:
            json.dump(merged, f)

        # Delete partial results.
        for filename in glob.glob(self.filename + '_*'):
            os.remove(filename)

    def to_list_of_dicts(self):
        l = []
        for i in range(len(self.ids)):
            d = {key: self.data[key][i] for key in self.data.keys()}
            d['id'] = self.ids[i]
            l.append(d)
        return l
class RadicalScraper(Scraper):
    data = { 'Name Mnemonic': [] }
    def _scrape(self, soup):
        self.add_mnemonic('Name Mnemonic', soup)
class KanjiScraper(Scraper):
    data = { 'Meaning Mnemonic': [],
             'Reading Mnemonic': [] }
    def _scrape(self, soup):
        self.add_mnemonic('Meaning Mnemonic', soup)
        self.add_mnemonic('Reading Mnemonic', soup)
class VocabularyScraper(Scraper):
    data = { 'Audio': [],
             'Context Sentences': [],
             'Meaning Explanation': [],
             'Reading Explanation': [] }
    def add_context_sentences(self, soup):
        section = soup.find('section', 'context-sentence')
        sentences = []
        for div in section.find_all('div'):
            ja = div.find('p', attrs={'lang': 'ja'})
            en = div.find('p', attrs={'lang': None})
            sentences.append([ja.string, en.string])
        self.data['Context Sentences'].append(sentences)
    def add_audio(self, soup):
        source = soup.find('source', attrs={'type': self.formats['audio']})
        audiofile = source['src'].split('/')[-1]
        self.data['Audio'].append(audiofile)
        try:
            self.driver.get(source['src'])
        except selenium.common.exceptions.TimeoutException:
            # Navigate to a page which induces a download in Firefox.
            pass
    def _scrape(self, soup):
        self.add_context_sentences(soup)
        self.add_mnemonic('Meaning Explanation', soup)
        self.add_mnemonic('Reading Explanation', soup)
        self.add_audio(soup)


scrapers = {
    'radicals': RadicalScraper,
    'kanji': KanjiScraper,
    'vocabulary': VocabularyScraper
}
