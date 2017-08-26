import re

from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget

class ErrorLabel(Label):
    """Label widget which only shows itself when an error label is set."""
    _error = False

    @property
    def error(self):
        return self._error
    @error.setter
    def error(self, value):
        self._error = value
        if self._error:
            self.text = self._error
            with self.canvas.before:
                # Border.
                Color(rgba=self.border_color)
                Rectangle(pos=self.pos, size=self.size)
                # Background.
                Color(rgba=self.background_color)
                Rectangle(
                    pos=[int(self.pos[i] + self.border_margin)
                         for i in range(2)],
                    size=[self.size[i] - 2 * self.border_margin
                          for i in range(2)])
        else:
            self.text = ''
            self.canvas.before.clear()


class WaniKani2Anki(Widget):
    def process_apikey(self):
        apikey = self.ids.apikey_input.text.strip()
        print('Start with {}!'.format(apikey))
        # Check if it is a valid key.
        regex = '\w{8}-\w{4}-\w{4}-\w{4}-\w{12}$'
        error_label = self.ids.error_label
        if re.match(regex, apikey):
            # error_label.error = 'Match!'
            error_label.error = None
        else:
            error_label.error = 'Invalid API key. Please try again.'


class WaniKani2AnkiApp(App):
    def build(self):
        self.title = 'WaniKani 2 Anki'
        self.icon = 'media/images/WaniKaniLogoSite.png'
        return WaniKani2Anki()


if __name__ == '__main__':
    WaniKani2AnkiApp().run()
