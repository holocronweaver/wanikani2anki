import os
import re
import threading
import time
import yaml

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.behaviors.togglebutton import ToggleButtonBehavior

from lib.wanikani2anki import WaniKani, WaniKani2Anki
# from options import *


class SequentialScreen(Screen):
    def next_screen(self):
        self.manager.transition.direction = 'left'
    def prev_screen(self):
        self.manager.transition.direction = 'right'
        self.manager.current = self.manager.previous()

class SequentialScreenManager(ScreenManager):
    """A screen manager that calls."""
    def next_screen(self):
        self.current_screen.next_screen()
    def prev_screen(self):
        self.current_screen.prev_screen()


class APIKeyScreen(SequentialScreen):
    """Get user's WaniKani API V2 key."""
    def process_apikey(self):
        apikey = self.ids.apikey_input.text.strip()

        # Check if it is a valid key.
        regex = '\w{8}-\w{4}-\w{4}-\w{4}-\w{12}$'
        error_label = self.ids.error_label
        if re.match(regex, apikey):
            error_label.error = None
            App.get_running_app().apikey = apikey
            self.manager.transition.direction = 'left'
            self.manager.current = 'pick deck type'
        else:
            error_label.error = 'Invalid API key. Please try again.'


class PickDeckTypeScreen(SequentialScreen):
    """Pick the type of Anki deck to create.
    A deck 'type' is a deck options bundle for users who want to skip
    manual configuration."""
    def next_screen(self):
        super().next_screen()

        app = App.get_running_app()

        app.deck_type = self.get_selected_deck_type()
        if app.deck_type:
            if 'advanced' in app.deck_type:
                self.manager.current = 'advanced options'
            else:
                self.manager.current = 'download'
        else:
            self.ids.error_label.error = 'Please make a selection.'

    def get_selected_deck_type(self):
        selection = next(
            (t for t in ToggleButtonBehavior.get_widgets('deck_type')
             if t.state=='down'), None)
        return selection.deck_type if selection else None


class AdvancedDeckOptionsScreen(SequentialScreen):
    """Manually configure deck options."""

    filename = 'user_options.yaml'

    def on_enter(self):
        if os.path.isfile(self.filename):
            with open(self.filename, 'r') as f:
                self.wk2a_options = yaml.load(f)
            self.restore_options()

    def next_screen(self):
        super().next_screen()

        #TODO: Save & later restore custom config.

        # Validate options.
        try:
            burn_years = int(self.ids.burn_years.text)
            if not 1 <= burn_years <= 100: raise Exception()
        except:
            self.ids.error_label.error = 'Burn years must be an integer between 1 and 100.'
            return

        # Save options.
        app = App.get_running_app()

        app.wk2a_options = {
            'burn years': burn_years,
            'enable audio': self.ids.enable_audio.state == 'down',
            'separate meaning and reading': self.ids.separate_meaning_and_reading.state == 'down',
        }

        with open(self.filename, 'w') as f:
            yaml.dump(app.wk2a_options, f)

        self.manager.current = 'download'

    def restore_options(self):
        self.ids.burn_years.text = str(self.wk2a_options['burn years'])
        self.ids.enable_audio.state = 'down' if self.wk2a_options['enable audio'] else 'normal'
        self.ids.separate_meaning_and_reading.state = 'down' if self.wk2a_options['separate meaning and reading'] else 'normal'


class DownloadScreen(SequentialScreen):
    """Waiting screen while deck is downloading and generating."""

    progress = NumericProperty(0)
    download_thread = None
    download_status = None # 'downloading', 'canceled', 'complete'
    create_deck_button = None

    def next_screen(self):
        super().next_screen()
        self.create_deck_button = self.ids.create_deck
        self.ids.create_deck_container.remove_widget(self.ids.create_deck)
        self.download_thread = threading.Thread(
            target=self.download_wanikani_data)

        self.download_status = 'downloading'
        self.download_thread.start()
        Clock.schedule_interval(self.update_download_progress, 0.5)

    def prev_screen(self):
        self.download_status = 'canceled'
        if self.download_thread:
            self.wk.cancel_download()
            self.download_thread.join()
        if self.create_deck_button:
            self.ids.create_deck_container.add_widget(self.create_deck_button)

        # Reset state. TODO: Convert to function.
        self.progress = 0
        self.download_thread = None
        self.download_status = None
        self.create_deck_button = None

        self.manager.transition.direction = 'right'
        self.manager.current = 'pick deck type'

    def download_wanikani_data(self):
        #TODO: Figure out nice way to centralize options.
        general_cache = 'cache/general/'
        users_cache = 'cache/users/'

        app = App.get_running_app()
        apikey = app.apikey
        deck_type = app.deck_type
        self.wk = WaniKani()
        wk2a = WaniKani2Anki(
            self.wk,
            mode=deck_type if not 'advanced' in deck_type else 'plus',
            options=app.wk2a_options)

        user, userpath = self.wk.get_user(apikey, users_cache)
        self.progress = 10
        time.sleep(1)

        print('''Fetching information for
        user:  {username}
        level: {level}
        '''.format(**user['wanikani']['data']))

        if 'canceled' == self.download_status:
            return

        data = self.wk.get_data(user, userpath, general_cache)

        if 'canceled' == self.download_status:
            return

        self.progress = 90
        time.sleep(1)

        deck_options = wk2a.create_deck_options(user)
        deck = wk2a.create_deck(user, data, deck_options)

        if deck:
            self.download_status = 'complete'
            deckpath = os.path.join(userpath, 'WaniKani.apkg')
            # wk2a.write_deck_to_file(deckpath, deck, media, override=True)
            self.progress = 100
            time.sleep(2)
            self.manager.current = 'finish'

    def update_download_progress(self, time_delta):
        downloading = 'downloading' == self.download_status
        if downloading:
            self.progress = 10 + self.wk.download_progress * 80
        return downloading


class FinishScreen(SequentialScreen):
    """Farewell screen letting user know what to do next."""
    def next_screen(self):
        pass

    def prev_screen(self):
        pass
