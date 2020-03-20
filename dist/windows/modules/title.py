from kivy.uix.screenmanager import Screen

class TitleScreen(Screen):
    def on_parent(self, instance, parent):
        self.screenmanager = parent
    
    def play(self):
        self.screenmanager.transition.direction = "left"
        self.screenmanager.current = "game"
    
    # Named so because 'continue' is already a keyword in python.
    def continue_game(self):
        self.screenmanager.transition.direction = "left"
        self.screenmanager.current = "game"
    
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
