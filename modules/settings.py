from kivy.uix.screenmanager import Screen
from kivy.properties import (
BoundedNumericProperty, OptionProperty, StringProperty
)
from kivy.clock import Clock

import os
import pickle
from pprint import pprint

class SettingsScreen(Screen):
    size_x = BoundedNumericProperty(7, min=3, max=42)
    size_y = BoundedNumericProperty(7, min=3, max=42)
    mode = OptionProperty("drag", options=["drag", "click"])
    player1 = OptionProperty("human", options=["human", "computer"])
    player2 = OptionProperty("computer", options=["human", "computer"])
    difficulty = OptionProperty("challenging", options=["easy", "challenging", "formidable"])
    sound = OptionProperty("enabled", options=["enabled", "disabled"])
    speed = OptionProperty("fast", options=["immediate", "fast", "slow"])
    grid = OptionProperty("enabled", options=["enabled", "disabled"])
    allowed = OptionProperty("enabled", options=["enabled", "disabled"])
    font = StringProperty("fonts/CaviarDreams.ttf")
    hold = False
    
    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)
        self.variant = "standard"
        self.gold = "d4af37"
        self.silver = "b0c4de"
        self.rust = "b7410e"
        self.update_text()
    
    def start_hold(self):
        self.hold = True
        Clock.schedule_once(self.end_hold, 0.1)
    
    def end_hold(self, dt):
        self.hold = False
    
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
#        self.ids.font.font_name = font
    
    def set_variant(self, variant):
        self.variant = variant
        self.save_settings()
    
#    def alter_board_size(self):
#        sx_prop = self.property('size_x')
#        sy_prop = self.property('size_y')
#        if self.size_x == sx_prop.get_min(self) or self.size_y == sy_prop.get_min(self):
#            self.size_x = self.property('size_x').get_max(self)
#            self.size_y = self.property('size_y').get_max(self)
#        else:
#            self.size_x -= 1
#            self.size_y -= 1
#        self.ids.board_size.text = "board size is %d, %d" % (self.size_x, self.size_y)

    def alter_board_size(self):
        # For whatever reason buttons sometimes release twice following a single
        # press. The hold prevents this function and others in this module from
        # being called twice within some span of time.
        if self.hold:
            return
        self.start_hold()
        if self.size_x == 5:
            self.size_x = 7
            self.size_y = 7
        elif self.size_x == 7:
            self.size_x = 9
            self.size_y = 9
        elif self.size_x == 9:
            self.size_x = 11
            self.size_y = 11
        else:
            self.size_x = 5
            self.size_y = 5
        #self.ids.board_size.text = "board size is %d, %d" % (self.size_x, self.size_y)
        self.update_text()
        self.save_settings()
    
    def alter_mode(self):
        if self.hold:
            return
        self.start_hold()
        if self.mode == "drag":
            self.mode = "click"
        else:
            self.mode = "drag"
#        self.ids.mode.text = "mode set to " + self.mode
        self.update_text()
        self.save_settings()
    
    def alter_player1(self):
        if self.hold:
            return
        self.start_hold()
        if self.player1 == "human":
            self.player1 = "computer"
            #self.ids.player1.text = "player 1 is a [color=%s]computer[/color]" % (self.rust)
        else:
            self.player1 = "human"
            #self.ids.player1.text = "player 1 is [color=%s]human[/color]" % (self.gold)
        self.update_text()
        self.save_settings()
    
    def alter_player2(self):
        if self.hold:
            return
        self.start_hold()
        if self.player2 == "human":
            self.player2 = "computer"
#            self.ids.player2.text = "player 2 is a [color=%s]computer[/color]" % (self.rust)
        else:
            self.player2 = "human"
#            self.ids.player2.text = "player 2 is [color=%s]human[/color]" % (self.gold)
        self.update_text()
        self.save_settings()
    
    def alter_difficulty(self):
        if self.hold:
            return
        self.start_hold()
        if self.difficulty == "easy":
            self.difficulty = "challenging"
        elif self.difficulty == "challenging":
            self.difficulty = "formidable"
        else:
            self.difficulty = "easy"
#        self.ids.difficulty.text = "computer difficulty is " + self.difficulty
        self.update_text()
        self.save_settings()
    
    def alter_sound(self):
        if self.hold:
            return
        self.start_hold()
        if self.sound == "enabled":
            self.sound = "disabled"
        else:
            self.sound = "enabled"
#        self.ids.sound.text = "sound is " + self.sound
        self.update_text()
        self.save_settings()
    
    def alter_speed(self):
        if self.hold:
            return
        self.start_hold()
        if self.speed == "fast":
            self.speed = "slow"
        elif self.speed == "slow":
            self.speed = "immediate"
        else:
            self.speed = "fast"
#        self.ids.speed.text = "move animation speed is " + self.speed
        self.update_text()
        self.save_settings()
    
    def alter_grid(self):
        if self.hold:
            return
        self.start_hold()
        if self.grid == "enabled":
            self.grid = "disabled"
        else:
            self.grid = "enabled"
#        self.ids.grid.text = "grid is " + self.grid
        self.update_text()
        self.save_settings()
    
    def alter_allowed(self):
        if self.hold:
            return
        self.start_hold()
        if self.allowed == "enabled":
            self.allowed = "disabled"
        else:
            self.allowed = "enabled"
        self.update_text()
        self.save_settings()
    
    def alter_font(self):
        if self.hold:
            return
        self.start_hold()
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
        #self.ids.font.text = "using %s font" % self.font.split('/')[1].split('.')[0]
        self.update_text()
        self.save_settings()
    
    # TODO this has not been modified to include recent settings additions
    def update_text(self):
        self.ids.board_size.text = "board size is [color=%s]%d, %d[/color]" % \
                                   (self.gold, self.size_x, self.size_y)
        self.ids.mode.text = "move pieces via [color=%s]%s[/color]" % \
                             (self._color(self.mode), self.mode)
        if self.player1 == "human":
            self.ids.player1.text = "player 1 is [color=%s]human[/color]" % self.gold
        else:
            self.ids.player1.text = "player 1 is a [color=%s]computer[/color]" % self.rust
        if self.player2 == "human":
            self.ids.player2.text = "player 2 is [color=%s]human[/color]" % self.gold
        else:
            self.ids.player2.text = "player 2 is a [color=%s]computer[/color]" % self.rust
        self.ids.difficulty.text = "computer difficulty is [color=%s]%s[/color]" % \
                                   (self._color(self.difficulty), self.difficulty)
        self.ids.sound.text = "sound is [color=%s]%s[/color]" % \
                              (self._color(self.sound), self.sound)
        self.ids.speed.text = "move animation speed is [color=%s]%s[/color]" % \
                              (self._color(self.speed), self.speed)
        self.ids.grid.text = "grid is [color=%s]%s[/color]" % \
                             (self._color(self.grid), self.grid)
        self.ids.allowed.text = "move highlighting is [color=%s]%s[/color]" % \
                                (self._color(self.allowed), self.allowed)
#        self.ids.font.text = "using [color=%s]%s[/color] font" % \
#                             (self.gold, self.font.split('/')[1].split('.')[0])
    
    def _color(self, string):
        colordict = {
            "easy": self.silver,
            "challenging": self.gold,
            "formidable": self.rust,
            "human": self.gold,
            "computer": self.rust,
            "enabled": self.gold,
            "disabled": self.rust,
            "drag": self.gold,
            "click": self.rust,
            "fast": self.gold,
            "slow": self.rust,
            "immediate": self.silver
        }
        return colordict[string]
    
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
            "allowed":      self.allowed,
            "font":         self.font,
            "variant":      self.variant
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
        self.allowed    = settings['allowed']
        self.font       = settings['font']
        self.variant    = settings['variant']
        self.update_text()
    
    def save_settings(self):
        path = "data/settings.p"
        data = self.export_settings()
        print("saving the following settings")
        pprint(data)
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



















    
