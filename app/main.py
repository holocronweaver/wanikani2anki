#! /usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.

# Disable mouse multitouch emulation.
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

# from lib.wanikani2anki import WaniKani

from screens import *
from widgets import *


class WaniKani2AnkiApp(App):
    def build(self):
        self.title = 'WaniKani 2 Anki'
        self.icon = 'media/images/WaniKaniLogoSite.png'

        sm = ScreenManager()
        sm.add_widget(APIKeyScreen(name='api key'))
        sm.add_widget(PickModeScreen(name='pick mode'))
        sm.current = 'api key'

        return sm


if __name__ == '__main__':
    WaniKani2AnkiApp().run()
