import re

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.behaviors.togglebutton import ToggleButtonBehavior

class SequentialScreen(Screen):
    def next_screen(self):
        pass
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
            self.manager.current = 'pick mode'
        else:
            error_label.error = 'Invalid API key. Please try again.'


class PickDeckTypeScreen(SequentialScreen):
    """Pick the type of Anki deck to create.
    A deck 'type' is a deck options bundle for users who want to skip
    manual configuration."""
    def next_screen(self):
        deck_type = self.get_selected_deck_type()
        if deck_type:
            print('Got it:', deck_type)
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
        #TODO: Save & later restore custom config.
        pass


class DownloadScreen(SequentialScreen):
    """Waiting screen while deck is downloading."""
    def next_screen(self):
        pass

    def prev_screen(self):
        # Cancel download.
        pass

    def update_progress(self):
        self.ids.progress.value = 50


class FinishScreen(SequentialScreen):
    """"""
    def next_screen(self):
        pass

    def prev_screen(self):
        pass
