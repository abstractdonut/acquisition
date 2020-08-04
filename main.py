import os
os.environ['KIVY_WINDOW'] = 'sdl2'
os.environ['KIVY_TEXT'] = 'sdl2'
os.environ['KIVY_AUDIO'] = 'sdl2'
os.environ['KIVY_IMAGE'] = 'sdl2'

from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import StringProperty, NumericProperty
from kivy.core.window import Window
from kivy.app import App
from kivy.logger import Logger
from kivy.clock import Clock

from modules.title import TitleScreen
from modules.game import GameScreen
from modules.variants import VariantsScreen
from modules.help import HelpScreen
from modules.settings import SettingsScreen
from modules.about import AboutScreen

from os.path import isfile, join, isdir
from kivy.lang import Builder
from kivy.resources import resource_add_path

import os, sys
sys.path.append(os.getcwd())

kv_path = os.getcwd() + '/layouts/'
kv_load_list = [
    "main.kv",
    "title.kv",
    "game.kv",
    "variants.kv",
    "help.kv",
    "settings.kv",
    "about.kv"
]

resource_add_path(kv_path)

for _file in kv_load_list:
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
        self.help_screen = HelpScreen(name="help")
        self.settings_screen = SettingsScreen(name="settings")
        self.about_screen = AboutScreen(name="about")
        self.add_widget(self.title_screen)
        self.add_widget(self.game_screen)
        self.add_widget(self.variants_screen)
        self.add_widget(self.help_screen)
        self.add_widget(self.settings_screen)
        self.add_widget(self.about_screen)
        self.current = "title"
        self.backscr = "title"
        self.hold = False
#        self.keyboard = Window.request_keyboard(self.keyboard_closed, self)
#        self.keyboard.bind(on_key_down=self.on_key_down)
        Window.bind(on_keyboard=self.on_key)
        self.variants_screen.bind(variant=self.on_variant)
        self.settings_screen.bind(font=self.on_font)
        settings = self.settings_screen.load_settings()
        self.variants_screen.set_variant(settings['variant'])
        self.title_screen.set_variant(settings['variant'])
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
#    def keyboard_closed(self):
#        self.keyboard.unbind(on_key_down=self.on_key_down)
#        self.keyboard = None
    
#    def on_key_down(self, keyboard, keycode, text, modifiers):
#        print("on_key_down received", keycode)
#        if keycode[1] == 'escape':
#            self.escape()
#            return True
#        elif keycode[1] == 't':
#            self.next_theme()
#        elif keycode[1] == 'r':
#            self.last_theme()
    
    # https://stackoverflow.com/questions/51963905/i-want-use-android-default-back-button-in-kivy/51966952
    def on_key(self, window, key, *args):
        if key == 27:  # the esc key
            self.escape()
            return True
    
    def on_stop(self):
        print("AcquisitionSM.on_stop")
        self.game_screen.save_game()
        self.settings_screen.save_settings()
   
    def escape(self):
        # For whatever reason buttons sometimes release twice following a single
        # press. The hold prevents this function from being called twice within
        # some span of time.
        if self.hold:
            return
        self.start_hold()
        print("Caught escape. backscr is", self.backscr)
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
            self.current = self.backscr
        else:
            self.transition.direction = "right"
            self.current = self.backscr
    
    def start_hold(self):
        self.hold = True
        Clock.schedule_once(self.end_hold, 0.1)
    
    def end_hold(self, dt):
        self.hold = False


#try:
#    from jnius import autoclass
#    from android.runnable import run_on_ui_thread

#    android_api_version = autoclass('android.os.Build$VERSION')
#    AndroidView = autoclass('android.view.View')
#    # AndroidPythonActivity = autoclass('org.renpy.android.PythonActivity')
#    AndroidPythonActivity = autoclass('org.kivy.android.PythonActivity')

#    Logger.debug(
#        'Application runs on Android, API level {0}'.format(
#            android_api_version.SDK_INT
#        )
#    )
#except ImportError:
#    def run_on_ui_thread(func):
#        def wrapper(*args):
#            Logger.debug('{0} called on non android platform'.format(
#                func.__name__
#            ))
#        return wrapper

class AcquisitionApp(App):
    def build(self):
        return AcquisitionSM()
    
    def on_stop(self):
        self.root.on_stop()
    
#    @run_on_ui_thread
#    def android_set_hide_menu(self):
#        if android_api_version.SDK_INT >= 19:
#            Logger.debug('API >= 19. Set hide menu')
#            view = AndroidPythonActivity.mActivity.getWindow().getDecorView()
#            view.setSystemUiVisibility(
#                AndroidView.SYSTEM_UI_FLAG_LAYOUT_STABLE |
#                AndroidView.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION |
#                AndroidView.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN |
#                AndroidView.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
#                AndroidView.SYSTEM_UI_FLAG_FULLSCREEN |
#                AndroidView.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
#            )


if __name__=='__main__':
    AcquisitionApp().run()























