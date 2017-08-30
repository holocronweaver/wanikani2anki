#! /usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.

# Disable mouse multitouch emulation.
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from kivy.app import App

from screens import *
from widgets import *

class WaniKani2AnkiApp(App):
    user = None
    deck_path = ''
    user_path = None

    app_options = {}
    app_options_path = 'app_options.yaml'

    def build(self):
        self.title = 'WaniKani 2 Anki'
        self.icon = 'media/images/WaniKaniLogoSite.png'

        self.wk2a = WaniKani2Anki()

        if os.path.isfile(self.app_options_path):
            with open(self.app_options_path, 'r') as f:
                self.app_options = yaml.load(f)
                self.wk2a.options['deck types']['user'] = self.app_options
                self.wk2a.options.update(
                    self.wk2a.options['deck types']['user'])

        sm = SequentialScreenManager()
        sm.add_widget(APIKeyScreen(name='api key'))
        sm.add_widget(PickDeckTypeScreen(name='pick deck type'))
        sm.add_widget(AdvancedDeckOptionsScreen(name='advanced options'))
        sm.add_widget(DownloadScreen(name='download'))
        sm.add_widget(FinishScreen(name='finish'))
        sm.current = 'api key'

        return sm

    def get_user(self, apikey):
        self.user = self.wk2a.get_user(apikey)
        return self.user

    def get_data(self, user):
        data = self.wk2a.get_data(user)
        return data

    def create_deck(self, user, data):
        deck_options = self.wk2a.create_deck_options(user)
        deck = self.wk2a.create_deck(user, data, deck_options)
        return deck

    def write_deck_to_file(self, deck):
        self.deck_path = os.path.join(self.user['path'],
                                      self.wk2a.options['deck path'])
        self.wk2a.write_deck_to_file(deck, self.deck_path, override=True)

    def cancel_download(self):
        self.wk2a.cancel_download()

    @property
    def download_progress(self):
        return self.wk2a.download_progress

if __name__ == '__main__':
    WaniKani2AnkiApp().run()
