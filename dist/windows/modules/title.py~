from kivy.uix.screenmanager import Screen
from kivy.clock import Clock

class TitleScreen(Screen):
    def __init__(self, **kwargs):
        super(TitleScreen, self).__init__(**kwargs)
        self.gold = "d4af37"
    
    def on_parent(self, instance, parent):
        self.screenmanager = parent
    
    def set_variant(self, variant):
        if variant == "standard":
            self.ids.title.text = "ACQUISITION"
        elif variant == "golf":
            self.ids.title.text = "ACQUISITION ~ [color=%s]GOLF[/color]" % self.gold
        elif variant == "diagonal":
            self.ids.title.text = "ACQUISITION ~ [color=%s]ODD DIAGONALS[/color]" % self.gold
        elif variant == "checkers":
            self.ids.title.text = "ACQUISITION ~ [color=%s]CHECKERS[/color]" % self.gold
        else:
            raise ValueError
    
    def set_font(self, font):
        print("setting font for title")
        self.ids.title.font_name = font
        self.ids.play.font_name = font
        self.ids.continue_game.font_name = font
        self.ids.variants.font_name = font
        self.ids.help.font_name = font
        self.ids.settings.font_name = font
        self.ids.about.font_name = font
    
    def play(self, dt=0):
        self.screenmanager.transition.direction = "left"
        self.screenmanager.current = "game"
    
    # Named so because 'continue' is already a keyword in python.
    def continue_game(self):
        self.screenmanager.game_screen.load_game()
        Clock.schedule_once(self.play, 0.1)
    
    def variants(self):
        self.screenmanager.transition.direction = "left"
        self.screenmanager.current = "variants"
    
    def help(self):
#        self.screenmanager.transition.direction = "left"
#        self.screenmanager.current = "help"
        pass
        
    def settings(self):
        self.screenmanager.transition.direction = "left"
        self.screenmanager.current = "settings"
    
    def about(self):
#        self.screenmanager.transition.direction = "left"
#        self.screenmanager.current = "about"
        pass
