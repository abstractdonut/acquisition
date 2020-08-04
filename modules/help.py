from kivy.uix.screenmanager import Screen


class HelpScreen(Screen):
    def set_font(self, font):
        pass
    
    def on_pre_enter(self):
        self.ids.scroll.scroll_y = 1
