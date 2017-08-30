# This Source Code Form is subject to the terms of the Mozilla Public
# License, v2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.
import os
import re
import threading
import time
from urllib.error import *
import yaml

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import NumericProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.behaviors.togglebutton import ToggleButtonBehavior

from lib.wanikani2anki import WaniKani, WaniKani2Anki
# from options import *

import utility

class SequentialScreen(Screen):
    def on_enter(self):
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def next_screen(self):
        self.manager.transition.direction = 'left'
    def prev_screen(self):
        self.manager.transition.direction = 'right'
        self.manager.current = self.manager.previous()

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'enter':
            self.next_screen()
        return True

class SequentialScreenManager(ScreenManager):
    """A screen manager that calls."""
    def next_screen(self):
        self.current_screen.next_screen()
    def prev_screen(self):
        self.current_screen.prev_screen()


class APIKeyScreen(SequentialScreen):
    """Get user's WaniKani API V2 key."""
    def next_screen(self):
        super().next_screen()
        self.process_apikey()

    def process_apikey(self):
        apikey = self.ids.apikey_input.text.strip()

        # Check if it is a valid key.
        regex = '\w{8}-\w{4}-\w{4}-\w{4}-\w{12}$'
        error_label = self.ids.error_label
        if not re.match(regex, apikey):
            error_label.error = 'Invalid API key. Please try again.'
            return

        app = App.get_running_app()
        try:
            user = app.get_user(apikey)
        except URLError as e:
            if hasattr(e, 'message'):
                error_label.error = e.message
            else:
                error_label.error = 'Unknown error. Please check key and internet connection, then try again.'
            return

        error_label.error = None
        self.manager.transition.direction = 'left'
        self.manager.current = 'pick deck type'


class PickDeckTypeScreen(SequentialScreen):
    """Pick the type of Anki deck to create.
    A deck 'type' is a deck options bundle for users who want to skip
    manual configuration."""
    def next_screen(self):
        super().next_screen()

        app = App.get_running_app()

        app.deck_type = self.get_selected_deck_type()
        if app.deck_type:
            if 'custom' in app.deck_type:
                self.manager.current = 'custom options'
            else:
                self.manager.current = 'download'
            self.ids.error_label.error = ''
        else:
            self.ids.error_label.error = 'Please make a selection. (*^.^*)'

    def get_selected_deck_type(self):
        selection = next(
            (t for t in ToggleButtonBehavior.get_widgets('deck_type')
             if t.state=='down'), None)
        return selection.deck_type if selection else None


class CustomDeckOptionsScreen(SequentialScreen):
    """Manually configure deck options."""

    def on_enter(self):
        super().on_enter()
        self.app_options = App.get_running_app().app_options
        self.restore_options()

    def next_screen(self):
        super().next_screen()

        # Validate options.
        try:
            burn_years = int(self.ids.burn_years.text)
            if not 0 <= burn_years <= 100: raise Exception()
        except:
            self.ids.error_label.error = 'Burn years must be an integer between 0 and 100.'
            return

        # Save options.
        self.app_options.update({
            'burn years': burn_years,
            'enable audio': self.ids.enable_audio.state == 'down',
            'separate meaning and reading': self.ids.separate_meaning_and_reading.state == 'down',
        })

        with open(App.get_running_app().app_options_path, 'w') as f:
            yaml.dump(self.app_options, f)

        self.manager.current = 'download'

    def restore_options(self):
        self.ids.burn_years.text = str(self.app_options['burn years'])
        self.ids.enable_audio.state = 'down' if self.app_options['enable audio'] else 'normal'
        self.ids.separate_meaning_and_reading.state = 'down' if self.app_options['separate meaning and reading'] else 'normal'


class DownloadScreen(SequentialScreen):
    """Waiting screen while deck is downloading and generating."""

    progress = NumericProperty(0)
    download_thread = None
    create_deck_button = None
    status = None

    status_text = {
        None: "Select 'Create Deck' to\nbegin download from WaniKani.",
        'downloading': 'Downloading from WaniKani',
        'building': 'Building Anki Deck',
        'canceled': 'Cancelling',
        'complete': 'Deck complete!'
    }

    def next_screen(self):
        super().next_screen()

        self.create_deck_button = self.ids.create_deck.__self__
        self.ids.create_deck_container.remove_widget(self.ids.create_deck)
        self.download_thread = threading.Thread(
            target=self.download_wanikani_data)

        self.status = 'downloading'
        self.download_thread.start()
        Clock.schedule_interval(self.update_download_progress, 0.5)

    def prev_screen(self):
        app = App.get_running_app()
        self.status = 'canceled'
        if self.download_thread:
            app.cancel_download()
            self.download_thread.join()

        self.reset()

        self.manager.transition.direction = 'right'
        self.manager.current = 'pick deck type'

    def reset(self):
        if self.create_deck_button:
            self.ids.create_deck_container.add_widget(self.create_deck_button)
            self.create_deck_button = None
        self.progress = 0
        self.download_thread = None
        self.status = None
        self.create_deck_button = None

    def download_wanikani_data(self):
        app = App.get_running_app()

        self.progress = 10
        time.sleep(1)

        if 'canceled' == self.status:
            return

        data = app.get_data(app.user)

        if 'canceled' == self.status:
            return

        self.progress = 90
        time.sleep(1)

        self.status = 'building'
        deck = app.create_deck(app.user, data)

        if deck:
            self.status = 'complete'
            app.write_deck_to_file(deck)
            self.progress = 100
            time.sleep(2)
            self.manager.current = 'finish'

    def update_download_progress(self, time_delta):
        downloading = 'downloading' == self.status
        if downloading:
            self.progress = 10 + App.get_running_app().download_progress * 80
        return downloading

    @property
    def status(self):
        return self._status
    @status.setter
    def status(self, value):
        if value in self.status_text:
            self.ids.status.text = self.status_text[value]
        self._status = value


class FinishScreen(SequentialScreen):
    """Farewell screen letting user know what to do next."""
    # def on_enter(self):
    #     super().on_enter()
    #     deck_path = App.get_running_app().deck_path
    #     self.ids.deck_path.text = os.path.join('{wanikani2anki folder}', deck_path)

    def next_screen(self):
        utility.open_file_in_default_app(App.get_running_app().deck_path)

    def prev_screen(self):
        directory = os.path.dirname(App.get_running_app().deck_path)
        utility.open_file_in_default_app(directory)
