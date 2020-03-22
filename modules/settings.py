from kivy.uix.screenmanager import Screen
from kivy.properties import (
BoundedNumericProperty, OptionProperty, StringProperty
)

import os
import pickle

class SettingsScreen(Screen):
    size_x = BoundedNumericProperty(7, min=3, max=7)
    size_y = BoundedNumericProperty(7, min=3, max=7)
    mode = OptionProperty("drag", options=["drag", "click"])
    player1 = OptionProperty("human", options=["human", "computer"])
    player2 = OptionProperty("human", options=["human", "computer"])
    difficulty = OptionProperty("challenging", options=["easy", "challenging", "infuriating"])
    sound = OptionProperty("enabled", options=["enabled", "disabled"])
    speed = OptionProperty("fast", options=["immediate", "fast", "slow"])
    grid = OptionProperty("enabled", options=["enabled", "disabled"])
    font = StringProperty("")
    
    def retrieve_fonts(self):
        filenames = os.listdir('fonts/')
        fontpaths = ['fonts/' + filename for filename in filenames]
        return fontpaths
    
    def set_font(self, font):
        self.ids.title.font_name = font
        self.ids.board_size.font_name = font
        self.ids.mode.font_name = font
        self.ids.player1.font_name = font
        self.ids.player2.font_name = font
        self.ids.difficulty.font_name = font
        self.ids.sound.font_name = font
        self.ids.speed.font_name = font
        self.ids.grid.font_name = font
        self.ids.font.font_name = font
    
    def alter_board_size(self):
        sx_prop = self.property('size_x')
        sy_prop = self.property('size_y')
        if self.size_x == sx_prop.get_min(self) or self.size_y == sy_prop.get_min(self):
            self.size_x = self.property('size_x').get_max(self)
            self.size_y = self.property('size_y').get_max(self)
        else:
            self.size_x -= 1
            self.size_y -= 1
        self.ids.board_size.text = "board size is %d, %d" % (self.size_x, self.size_y)
    
    def alter_mode(self):
        if self.mode == "drag":
            self.mode = "click"
        else:
            self.mode = "drag"
        self.ids.mode.text = "mode set to " + self.mode
    
    def alter_player1(self):
        if self.player1 == "human":
            self.player1 = "computer"
            self.ids.player1.text = "player 1 is a computer"
        else:
            self.player1 = "human"
            self.ids.player1.text = "player 1 is human"
    
    def alter_player2(self):
        if self.player2 == "human":
            self.player2 = "computer"
            self.ids.player2.text = "player 2 is a computer"
        else:
            self.player2 = "human"
            self.ids.player2.text = "player 2 is human"
    
    def alter_difficulty(self):
        if self.difficulty == "easy":
            self.difficulty = "challenging"
        elif self.difficulty == "challenging":
            self.difficulty = "infuriating"
        else:
            self.difficulty = "easy"
        self.ids.difficulty.text = "computer difficulty is " + self.difficulty
    
    def alter_sound(self):
        if self.sound == "enabled":
            self.sound = "disabled"
        else:
            self.sound = "enabled"
        self.ids.sound.text = "sound is " + self.sound
    
    def alter_speed(self):
        if self.speed == "fast":
            self.speed = "slow"
        elif self.speed == "slow":
            self.speed = "immediate"
        else:
            self.speed = "fast"
        self.ids.speed.text = "move animation speed is " + self.speed
    
    def alter_grid(self):
        if self.grid == "enabled":
            self.grid = "disabled"
        else:
            self.grid = "enabled"
        self.ids.grid.text = "grid is " + self.grid
    
    def alter_font(self):
        fonts = self.retrieve_fonts()
        print("\nretreived the following fonts", fonts)
        print("\ncurrent font is", self.font)
        try:
            idx = fonts.index(self.font)
            idx = (idx + 1) % len(fonts)
            self.font = fonts[idx]
            print("selected %s from fonts" % self.font)
        except ValueError:
            print("alter_font received ValueError")
            self.font = "fonts/Brendohand.otf"
        self.ids.font.text = "using %s font" % self.font.split('/')[1].split('.')[0]
    
    # TODO this has not been modified to include recent settings additions
    def update_text(self):
        self.ids.board_size.text = "board size is %d, %d" % (self.size_x, self.size_y)
        self.ids.mode.text = "mode set to " + self.mode
        if self.player1 == "human":
            self.ids.player1.text = "player 1 is human"
        else:
            self.ids.player1.text = "player 1 is a computer"
        if self.player2 == "human":
            self.ids.player2.text = "player 2 is human"
        else:
            self.ids.player2.text = "player 2 is a computer"
        self.ids.difficulty.text = "computer difficulty is " + self.difficulty
        self.ids.sound.text = "sound is " + self.sound
        self.ids.speed.text = "move animation speed is " + self.speed
        self.ids.grid.text = "grid is " + self.grid
        self.ids.font.text = "using %s font" % self.font.split('/')[1].split('.')[0]
    
    def export_settings(self):
        return {
            "size_x":       self.size_x,
            "size_y":       self.size_y,
            "mode":         self.mode,
            "player1":      self.player1,
            "player2":      self.player2,
            "difficulty":   self.difficulty,
            "sound":        self.sound,
            "speed":        self.speed,
            "grid":         self.grid,
            "font":         self.font
        }
    
    def import_settings(self, settings):
        print(settings)
        self.size_x     = settings['size_x']
        self.size_y     = settings['size_y']
        self.mode       = settings['mode']
        self.player1    = settings['player1']
        self.player2    = settings['player2']
        self.difficulty = settings['difficulty']
        self.sound      = settings['sound']
        self.speed      = settings['speed']
        self.grid       = settings['grid']
        self.font       = settings['font']
        self.update_text()
    
    def save_settings(self):
        path = "data/settings.p"
        data = self.export_settings()
        with open(path, 'wb') as pfile:
            pickle.dump(data, pfile)
    
    def load_settings(self):
        path = "data/settings.p"
        try:
            with open(path, 'rb') as pfile:
                data = pickle.load(pfile)
            self.import_settings(data)
        except FileNotFoundError:
            pass
        return self.export_settings()



















    
