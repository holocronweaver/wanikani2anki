import re

from kivy.app import App
from kivy.uix.screenmanager import Screen

class APIKeyScreen(Screen):
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


class PickModeScreen(Screen):
    pass
