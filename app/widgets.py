# This Source Code Form is subject to the terms of the Mozilla Public
# License, v2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.
from kivy.base import EventLoop
from kivy.graphics import Color, Rectangle
from kivy.uix.button import Button
from kivy.uix.behaviors.togglebutton import ToggleButtonBehavior
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget

class WKToggleButton(ToggleButton):
    def on_state(self, widget, value):
        """Change solid color based on button state.
        Unfortunately not implemented in default Kivy."""
        if value == 'down':
            self.background_color = self.background_color_down
            self.color = self.color_down
        else:
            self.background_color = self.background_color_normal
            self.color = self.color_normal


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


class TextInputPlus(TextInput):
    """Supports right-click context menus and max characters."""

    use_bubble = True
    max_char = None

    def on_text(self, instance, value):
        if self.max_char and len(value) > self.max_char:
            self.text = value[:self.max_char]

    def on_touch_down(self, touch):
        super().on_touch_down(touch)

        if touch.button == 'right':
            pos = touch.pos
            if self.collide_point(pos[0], pos[1]):
                self._show_cut_copy_paste(
                    pos, EventLoop.window, mode='paste')

    def paste(self):
        super().paste()
        if not self.multiline:
            # Remove extraneous newlines.
            self.text = self.text.rstrip()
