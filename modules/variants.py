from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty

class VariantsScreen(Screen):
    variant = StringProperty("standard")
    
    def on_parent(self, instance, parent):
        self.screenmanager = parent
    
    def escape(self):
        self.screenmanager.transition.direction = "right"
        self.screenmanager.current = "title"
    
    def set_variant(self, variant):
        self.variant = variant
    
    def set_font(self, font):
        self.ids.title.font_name = font
        self.ids.standard.font_name = font
        self.ids.standard_desc.font_name = font
        self.ids.golf.font_name = font
        self.ids.golf_desc.font_name = font
        self.ids.diagonals.font_name = font
        self.ids.diagonals_desc.font_name = font
#        self.ids.checkers.font_name = font
#        self.ids.checkers_desc.font_name = font
    
    def standard(self):
        self.variant = "standard"
        self.escape()
    
    # Named so because 'continue' is already a keyword in python.
    def golf(self):
        self.variant = "golf"
        self.escape()
    
    def diagonals(self):
        self.variant = "diagonal"
        self.escape()
    
    def checkers(self):
        self.variant = "checkers"
        self.escape()
