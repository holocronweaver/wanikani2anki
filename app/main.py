from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.widget import Widget


class WaniKani2Anki(Widget):
    def start(self):
        print('Start!')


class WaniKani2AnkiApp(App):
    def build(self):
        self.icon = 'media/images/WaniKaniLogoSite.png'
        return WaniKani2Anki()


if __name__ == '__main__':
    WaniKani2AnkiApp().run()
