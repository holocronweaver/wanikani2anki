from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.widget import Widget


class WaniKani2Anki(Widget):
    pass


class WaniKani2AnkiApp(App):
    def build(self):
        return WaniKani2Anki()


if __name__ == '__main__':
    WaniKani2AnkiApp().run()
