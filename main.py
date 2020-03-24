from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.app import App

from modules.title import TitleScreen
from modules.game import GameScreen
from modules.variants import VariantsScreen
from modules.settings import SettingsScreen

from os.path import isfile, join, isdir
from kivy.lang import Builder
from kivy.resources import resource_add_path

import os, sys
sys.path.append(os.getcwd())

### Copypasted from chess/main.py, will need to be adapted later on.
kv_path = os.getcwd() + '/layouts/'
kv_load_list = [
    "title.kv",
    "game.kv",
    "variants.kv",
    "settings.kv"
]

resource_add_path(kv_path)

for _file in kv_load_list:
    if _file.endswith('.kv'):
        print("Attempting to load following path:")
        print(kv_path + _file, "\n")
        Builder.load_file(_file)
###


class AcquisitionSM(ScreenManager):
    def __init__(self, **kwargs):
        super(AcquisitionSM, self).__init__(**kwargs)
        self.title_screen = TitleScreen(name="title")
        self.game_screen = GameScreen(name="game")
        self.variants_screen = VariantsScreen(name="variants")
        #self.help_screen = RulesScreen(name="rules")
        self.settings_screen = SettingsScreen(name="settings")
        #self.about_screen = AboutScreen(name="about")
        self.add_widget(self.title_screen)
        self.add_widget(self.game_screen)
        self.add_widget(self.variants_screen)
        self.add_widget(self.settings_screen)
        self.current = "title"
        self.keyboard = Window.request_keyboard(self.keyboard_closed, self)
        self.keyboard.bind(on_key_down=self.on_key_down)
        self.variants_screen.bind(variant=self.on_variant)
        self.settings_screen.bind(font=self.on_font)
        settings = self.settings_screen.load_settings()
        self.variants_screen.set_variant(settings['variant'])
        #self.title_screen.set_variant(settings['variant'])
        self.game_screen.import_settings(settings)
        self.on_font(self.settings_screen, self.settings_screen.font)
    
    def on_variant(self, instance, variant):
        self.game_screen.set_game_variant(variant)
        self.title_screen.set_variant(variant)
        self.settings_screen.set_variant(variant)
    
    def on_font(self, instance, font):
        print("on_font reached")
        for screen in self.screens:
            screen.set_font(font)
    
    # https://stackoverflow.com/questions/17280341/how-do-you-check-for-keyboard-events-with-kivy
    def keyboard_closed(self):
        self.keyboard.unbind(on_key_down=self.on_key_down)
        self.keyboard = None
    
    def on_key_down(self, keyboard, keycode, text, modifiers):
        print("on_key_down received", keycode)
        if keycode[1] == 'escape':
            self.escape()
            return True
    
    def on_stop(self):
        print("AcquisitionSM.on_stop")
        self.game_screen.save_game()
        self.settings_screen.save_settings()
    
    def escape(self):
        if self.current == "title":
            App.get_running_app().stop()
        elif self.current == "game":
            settings = self.game_screen.export_settings()
            self.settings_screen.import_settings(settings)
            self.transition.direction = "right"
            self.current = "title"
        elif self.current == "settings":
            settings = self.settings_screen.export_settings()
            self.game_screen.import_settings(settings)
            self.transition.direction = "right"
            self.current = "title"
        else:
            self.transition.direction = "right"
            self.current = "title"


class AcquisitionApp(App):
    def build(self):
        return AcquisitionSM()
    
    def on_stop(self):
        self.root.on_stop()


if __name__=='__main__':
    AcquisitionApp().run()























