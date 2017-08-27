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


if __name__ == '__main__':
    WaniKani2AnkiApp().run()
