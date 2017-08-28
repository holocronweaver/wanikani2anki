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
    wk2a_options = None

    wk = WaniKani()
    wk2a = None
    general_cache = 'cache/general/'
    users_cache = 'cache/users/'
    user = None
    userpath = None

    deck_type = ''

    def build(self):
        self.title = 'WaniKani 2 Anki'
        self.icon = 'media/images/WaniKaniLogoSite.png'

        sm = SequentialScreenManager()
        sm.add_widget(APIKeyScreen(name='api key'))
        sm.add_widget(PickDeckTypeScreen(name='pick deck type'))
        sm.add_widget(AdvancedDeckOptionsScreen(name='advanced options'))
        sm.add_widget(DownloadScreen(name='download'))
        sm.add_widget(FinishScreen(name='finish'))
        sm.current = 'api key'

        return sm

    def get_user(self, apikey):
        self.user, self.userpath = self.wk.get_user(apikey, self.users_cache)
        return (self.user, self.userpath)

    def get_data(self):
        deck_type = self.deck_type
        self.wk2a = WaniKani2Anki(
            self.wk,
            mode=deck_type if not 'advanced' in deck_type else 'plus',
            options=self.wk2a_options)
        data = self.wk.get_data(self.user, self.userpath, self.general_cache)
        return data

    def create_deck(self, data):
        deck_options = self.wk2a.create_deck_options(self.user)
        deck = self.wk2a.create_deck(self.user, data, deck_options)
        return deck

    def write_deck_to_file(self, deck):
        deckpath = os.path.join(self.userpath, 'WaniKani.apkg')
        # self.wk2a.write_deck_to_file(deckpath, deck, media, override=True)


if __name__ == '__main__':
    WaniKani2AnkiApp().run()
