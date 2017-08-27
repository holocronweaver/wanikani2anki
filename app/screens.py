import re
import threading
import time

from kivy.app import App
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


class APIKeyScreen(Screen):
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
                print('TODO: Advanced. =)')
                self.manager.current = 'advanced options'
            else:
                self.manager.current = 'download'
        else:
            print('Nah.')

    def get_selected_deck_type(self):
        selection = next(
            (t for t in ToggleButtonBehavior.get_widgets('deck_type')
             if t.state=='down'), None)
        return selection.deck_type if selection else None


class AdvancedDeckOptionsScreen(SequentialScreen):
    """Manually configure deck options."""
    def next_screen(self):
        super().next_screen()
        #TODO: Save & later restore custom config.

        self.manager.current = 'download'


class DownloadScreen(SequentialScreen):
    """Waiting screen while deck is downloading and generating."""
    def next_screen(self):
        super().next_screen()
        self.download_wanikani_data()
        self.manager.current = 'finish'

    def prev_screen(self):
        #TODO: Cancel download.
        super().prev_screen()

    def download_wanikani_data(self):
        #TODO: Figure out nice way to centralize options.
        general_cache = 'cache/general/'
        users_cache = 'cache/users/'

        app = App.get_running_app()
        apikey = app.apikey
        deck_type = app.deck_type
        wk = WaniKani()
        wk2a = WaniKani2Anki(
            wk, mode=deck_type if not 'advanced' in deck_type else 'plus')

        user, userpath = wk.get_user(apikey, users_cache)
        self.update_progress(0.1)

        print('''Fetching information for
        user:  {username}
        level: {level}
        '''.format(**user['wanikani']['data']))

        #TODO: Figure out how to get progress updates.
        data = wk.get_data(user, userpath, general_cache)
        self.update_progress(0.8)

        deck_options = wk2a.create_deck_options(user)
        deck = wk2a.create_deck(user, data, deck_options)

        self.update_progress(1.0)
        time.sleep(1)

    def update_progress(self, value):
        progress = self.ids.progress
        progress.value = int(value * progress.max)


class FinishScreen(SequentialScreen):
    """Farewell screen letting user know what to do next."""
    def next_screen(self):
        pass

    def prev_screen(self):
        pass
