from kivy.uix.screenmanager import Screen
from kivy.clock import Clock

class TitleScreen(Screen):
    def __init__(self, **kwargs):
        self.gold = "d4af37"
        super(TitleScreen, self).__init__(**kwargs)
    
    def on_enter(self):
        self.screenmanager.backscr = "title"
    
    def on_parent(self, instance, parent):
        self.screenmanager = parent
    
    def set_variant(self, variant):
        if variant == "standard":
            self.ids.title.source = "images/logo/title/Acquisition-logo-4.png"
        elif variant == "golf":
            self.ids.title.source = "images/logo/title/Acquisition-logo-4-golf.png"
        elif variant == "diagonal":
            self.ids.title.source = "images/logo/title/Acquisition-logo-4-odd-diagonals.png"
        elif variant == "checkers":
            self.ids.title.source = "images/logo/title/Acquisition-logo-4-checkers.png"
        else:
            raise ValueError
    
    def set_font(self, font):
        print("setting font for title")
#        self.ids.title.font_name = font
        self.ids.play.font_name = font
        self.ids.continue_game.font_name = font
        self.ids.variants.font_name = font
        self.ids.help.font_name = font
        self.ids.settings.font_name = font
        self.ids.about.font_name = font
        
    def play(self, dt=0):
        self.screenmanager.game_screen.reset()
        self.screenmanager.transition.direction = "left"
        self.screenmanager.current = "game"
    
    # Named so because 'continue' is already a keyword in python.
    def continue_game(self):
        self.screenmanager.game_screen.load_game()
        self.screenmanager.transition.direction = "left"
        self.screenmanager.current = "game"
    
    def variants(self):
        self.screenmanager.transition.direction = "left"
        self.screenmanager.current = "variants"
    
    def help(self):
        self.screenmanager.transition.direction = "left"
        self.screenmanager.current = "help"
        
    def settings(self):
        self.screenmanager.transition.direction = "left"
        self.screenmanager.current = "settings"
    
    def about(self):
        self.screenmanager.transition.direction = "left"
        self.screenmanager.current = "about"









