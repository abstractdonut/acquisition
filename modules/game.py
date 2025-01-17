import kivy
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.properties import (
    ListProperty, OptionProperty, BooleanProperty, NumericProperty
)
from kivy.animation import Animation, AnimationTransition
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.cache import Cache

# ANDROID VERSION
from kivy.core.audio import SoundLoader
# WINDOWS VERSION
#import pygame
import pickle
import pprint
import sys

from modules.board import (
    Board, GolfVariant, CheckersVariant, CheckersVariant2, DiagonalVariant
)

import threading
from functools import partial

from math import floor
from pprint import pprint

class Game():
    variants = {
        "standard": Board,
        "golf":     GolfVariant,
        "checkers": CheckersVariant2,
        "diagonal": DiagonalVariant
    }
    def __init__(self, size=(7, 7), variant="standard"):
        self.variant = variant
        self.board = Game.variants[variant](size)
        self.line = []
        self.indx = -1      # no moves yet
    
    def get_state(self):
        return self.board.state()
    
    def make_move(self, frompos, topos):
        if self.indx + 1 < len(self.line):
            c1 = self.line[self.indx+1]['from pos'] == frompos
            c2 = self.line[self.indx+1]['to pos'] == topos
            if c1 and c2:
                if not self.redo():
                    raise RuntimeError
                self.save_game()
                return True
        try:
            self.board.push({'from pos': frompos, 'to pos': topos})
        except ValueError:
            return False
        self.indx = len(self.board.moves) - 1
        self.line = [move for move in self.board.moves]
        self.save_game()
        return True
    
    def choose_move(self, callback, difficulty):
        print("choosing move for computer")
        print("note, current board size is %d, %d" % self.board.size)
        breadth = self.choose_breadth(difficulty)
        handicap = self.choose_handicap(difficulty)
        args = (callback, 1, breadth, handicap)
        target = self.board.best_move
        minimax_thread = threading.Thread(target=target, args=args, daemon=True)
        minimax_thread.start()
        return minimax_thread
    
    def choose_breadth(self, difficulty):
        print("current difficulty is", difficulty)
        if difficulty == "easy":
            return 13
        elif difficulty == "challenging":
            return 16
        elif difficulty == "formidable":
            return 21
        else:
            raise ValueError
    
    def choose_handicap(self, difficulty):
        if difficulty == "easy":
            return 3
        elif difficulty == "challenging":
            return 1
        else:
            return 0
    
    def next_move(self):
        if self.indx + 1 < len(self.line):
            return self.line[self.indx + 1]
    
    def undo(self):
        if self.indx >= 1:
            self.board.pop()
            self.board.pop()
            self.indx -= 2
            return True
        elif self.indx >= 0:
            self.board.pop()
            self.indx -= 1
        else:
            return False
    
    def redo(self):
        if self.indx + 1 < len(self.line):
            self.indx += 1
            print("preparing to push move.")
            self.board.push(self.line[self.indx])
            return True
        else:
            print("redo failed.")
            return False
    
    def reset(self):
        if self.line:
            self.board = self.board.__class__(self.board.size)
            self.line = []
            self.indx = -1
            return True
        else:
            return False
    
    def save_game(self):
        print("preparing to save game")
        if len(self.line) > 0:
            path = "data/game-%s.p" % self.variant
            data = (self.line, self.board.size)
            with open(path, 'wb') as pfile:
                pickle.dump(data, pfile)
    
    def load_game(self):
        print("loading game with variant %s" % self.variant)
        path = "data/game-%s.p" % self.variant
        try:
            with open(path, 'rb') as pfile:
                self.line, size = pickle.load(pfile)
                self.board = self.board.__class__(size)
                for move in self.line:
                    self.board.push(move)
                self.indx = len(self.line) - 1
            return True
        except FileNotFoundError:
            pass


class GameScreen(Screen):
    status_verbose = {
        'init':         "New Game: Player 1's turn",
        'player1':      "Player 1's turn",
        'player2':      "Player 2's turn",
        'player1 win':  "Game Over: Player 1 wins!",
        'player2 win':  "Game Over: Player 2 wins!",
        'stalemate':    "Game Over: Stalemate."
    }
    player1 = OptionProperty("human", options=["human", "computer"])
    player2 = OptionProperty("computer", options=["human", "computer"])
    paused = BooleanProperty(False)
    turns = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        Window.bind(size=self.on_window_size)
        self.variant = "standard"
        self.game = Game()
        self.mode = "drag"
        self.turns = 0
        self.searching = False
        self.difficulty = "challening"
        self.font = "fonts/CaviarDreams.ttf"
        self.grid = "enabled"
        self.sound = "enabled"
        self.speed = "fast"
        # ANDROID VERSION
        self.move_sound1 = SoundLoader.load('audio/move.wav')
        self.move_sound2 = SoundLoader.load('audio/move.wav')
        self.capture_sound = SoundLoader.load('audio/capture.wav')
        # WINDOWS VERSION
#        pygame.mixer.pre_init(22050, -16, 2, 2048) 
#        pygame.mixer.init()
#        self.move_sound1 = pygame.mixer.Sound("audio/move.wav")
#        self.move_sound2 = pygame.mixer.Sound("audio/move.wav")
#        self.capture_sound = pygame.mixer.Sound("audio/capture.wav")
        self.active = False
        self.pending = None
        self.redo_flag = False
        self.animations_complete = 0    # for debugging
        self.minimaxes_complete = 0     # also for debugging
        self.ids.piece_layout.populate(self.game.board)
        self.ids.piece_layout.bind(move_indicator=self.on_move_indicator)
        self.ids.piece_layout.bind(size=self.on_piece_layout_size)
        self.ids.status.text = GameScreen.status_verbose['init']
        self.hold = False
    
    def on_touch_up(self, touch):
#        if self.hold:
#            return True
#        self.start_hold()
        collide = self.ids.piece_layout.collide_point(*touch.pos)
        if collide:
            status = self.game.board.get_state()
            self.ids.status.text = GameScreen.status_verbose[status]
            if self.paused:
                self.paused = False
                self.start_turn(0)
                print("game screen on_touch_up digested.")
                return True
        super(GameScreen, self).on_touch_up(touch)
        return False
    
    def on_pre_enter(self):
        self.active = True
        print("received on_pre_enter")
        Window.size = (Window.size[0] - 1, Window.size[1])
        #Window.size = (Window.size[0] + 1, Window.size[1])
        if self.sound == "enabled":
            self.ids.toggle_sound.source = "images/icons/volume_black.png"
        else:
            self.ids.toggle_sound.source = "images/icons/volume_gray.png"
        if self.grid == "enabled":
            self.ids.toggle_grid.source = "images/icons/grid_black.png"
        else:
            self.ids.toggle_grid.source = "images/icons/grid_gray.png"
    
    def on_enter(self):
        print("received on_enter")
        print("game screen, self.parent is", self.parent)
        self.parent.backscr = "game"
        self.ids.piece_layout.update_dimensions()
        self.reload()
        if self.human_turn():
            self.start_turn(0)
        else:
            self.paused = True
    
    def on_leave(self):
        self.active = False
    
    def on_paused(self, instance, paused):
        print("on_paused received value %r" % paused)
        if paused:
            self.ids.status.text = "Game Paused"
            self.ids.piece_layout.disable()
#        else:
            if not self.human_turn():
                self.redo()
                self.redo_flag = False
            self.start_turn(0)
    
    def start_turn(self, dt):
        if self.game.board.game_over():
            print("caught gameover from start_turn")
        else:
            self.turns += 1
            print("")
            if self.human_turn():
                print("New turn for human player.")
                self.paused = False
                self.ids.piece_layout.enable()
            else:
                print("New turn for computer player.")
                self.ids.piece_layout.disable()
                self.choose_move(0)
    
    def on_turns(self, instance, turns):
        if turns % 15 == 0:
            self.reload()
    
    def human_turn(self):
        h1 = self.player1 == "human" and len(self.game.board.moves) % 2 == 0
        h2 = self.player2 == "human" and len(self.game.board.moves) % 2 == 1
        return h1 or h2
    
    def choose_move(self, dt):
        if not self.paused and not self.game.board.game_over():
            print("choosing new move for the computer")
            self.searching = True
            self.game.choose_move(self.minimax_callback, self.difficulty)
    
    def minimax_callback(self, move):
        if self.searching:
            self.minimaxes_complete += 1
            print("minimax callback reached %d times." % self.minimaxes_complete)
            self.searching = False
            self.animate_move(move)
        else:
            print("minimax callback ignored.")
    
    def animate_move(self, move):
        self.pending = move
        assert(not move is None)
        self.ids.piece_layout.animate_move(move, self.on_anim_complete)
    
    def on_anim_complete(self, animation, widget):
        if self.active:
            self.animations_complete += 1
            print("on_anim_complete reached %d times." % self.animations_complete)
            self.game.make_move(self.pending['from pos'], self.pending['to pos'])
            self.pending = None
            if self.redo_flag:
                print("on_anim_complete detected redo.")
                self.update(True, False)
                self.redo_flag = False
            else:
                print("on_anim_complete did not detect redo.")
                self.update()
    
    def on_move_indicator(self, instance, value):
        if len(value) == 4 and not self.game.board.game_over():
            print("received", value, "from move indicator")
            frompos = tuple(value[:2])
            topos   = tuple(value[2:])
            if self.mode == "drag":
                if self.game.make_move(frompos, topos):
                    self.update()
            elif self.mode == "click":
                move = {'from pos': frompos, 'to pos': topos}
                if self.game.board.is_legal(move):
                    self.animate_move(move)
            else:
                raise ValueError
    
    def on_window_size(self, window, size):
        self.update_padding()
        self.update_controls()
    
    def on_piece_layout_size(self, instance, size):
        self.update_controls()
    
    def update_controls(self):
        width = self.ids.piece_layout.width
        self.ids.controls.width = min(width * 4 / 3, Window.size[0])
        self.ids.controls.x = (Window.size[0] - self.ids.controls.width) / 2
    
    def update_padding(self):
        k = 2/3         # width coefficient
        if Window.size[0] <= k * Window.size[1]:
            self.ids.container.padding = [0, 0, 0, 0]
        else:
            gwidth = k * Window.size[1]
            pwidth = (Window.size[0] - gwidth) / 2
            self.ids.container.padding = [pwidth, 0, pwidth, 0]
#        k = 1/2         # width coefficient
#        if True: # Window.size[0] <= k * Window.size[1]:
#            self.ids.lpad.width = 0
#            self.ids.rpad.width = 0
#        else:
#            gwidth = k * Window.size[1]
#            pwidth = (Window.size[0] - gwidth) / 2
#            self.ids.lpad.width = pwidth
#            self.ids.rpad.width = pwidth
        
    
    def undo(self, dt=0):
        if self.hold:
            print("Caught duplicate undo")
            return True
        self.start_hold()
        if self.ids.piece_layout.animating:
            # TODO Alter this to abort the animation and expedite the undo.
            print("rescheduling undo")
            self.ids.piece_layout.abort_animation()
            Clock.schedule_once(self.undo, 0.05)
            return
        print("committing to undo")
        self.searching = False
        self.game.undo()
        if not self.human_turn():
            self.paused = True
        else:
            self.paused = False
        self.update(False, False)
    
    def redo(self, dt=0):
        if self.hold:
            print("Caught duplicate redo")
            return True
        self.start_hold()
        if self.ids.piece_layout.animating:
            print("rescheduling redo")              # is this necessary now that the same
            self.ids.piece_layout.abort_animation() # sort of check has been implemented within
            Clock.schedule_once(self.redo, 0.05)    # piece_layout?
            return
        print("committing to redo")
        self.searching = False
#        res = self.game.redo()
        move = self.game.next_move()
        if not move is None:
            self.paused = True
            self.animate_move(move)
            self.redo_flag = True
            self.paused = True
    
    def reset(self, dt=0):
        if self.hold:
            print("Caught duplicate reset")
            return True
        self.start_hold()
        print("sys.version is", sys.version)
        print("kivy.__version__ is %s" % kivy.__version__)
        if self.ids.piece_layout.animating:
            print("rescheduling reset")
            self.ids.piece_layout.abort_animation()
            Clock.schedule_once(self.reset, 0.5)
            return
        print("committing to reset")
        self.searching = False
        self.game.reset()
        if not self.human_turn():
            self.paused = True
        else:
            self.paused = False
        self.ids.piece_layout.board = self.game.board
        self.update(False)
    
    def toggle_sound(self):
        if self.hold:
            return
        self.start_hold()
        if self.sound == "enabled":
            self.sound = "disabled"
            self.ids.toggle_sound.source = "images/icons/volume_gray.png"
        else:
            self.sound = "enabled"
            self.ids.toggle_sound.source = "images/icons/volume_black.png"
    
    def toggle_grid(self):
        if self.hold:
            return
        self.start_hold()
        if self.grid == "enabled":
            self.grid = "disabled"
            self.ids.toggle_grid.source = "images/icons/grid_gray.png"
        else:
            self.grid = "enabled"
            self.ids.toggle_grid.source = "images/icons/grid_black.png"
        self.ids.piece_layout.set_grid(self.grid)
    
    def start_hold(self):
        self.hold = True
        Clock.schedule_once(self.end_hold, 0.1)
    
    def end_hold(self, dt):
        self.hold = False 
    
    def goto_settings(self):
        self.parent.transition.direction = "left"
        self.parent.current = "settings"
    
    def goto_help(self):
        self.parent.transition.direction = "left"
        self.parent.current = "help"
    
    def reload(self):
        self.ids.piece_layout.reload()
    
    def set_font(self, font):
        print("setting font for game")
        self.ids.status.font_name = font
        self.ids.score1.font_name = font
        self.ids.score2.font_name = font
#        self.ids.undo.font_name = font
#        self.ids.redo.font_name = font
#        self.ids.reset.font_name = font
#        self.ids._reload.font_name = font
    
    def set_game_variant(self, variant):
        print("setting game variant")
        if self.variant != variant:
            self.variant = variant
            self.game = Game(self.game.board.size, variant)
            self.ids.piece_layout.populate(self.game.board)
            self.ids.status.text = GameScreen.status_verbose['init']
    
    def set_game_size(self, size):
        print("setting game size")
        self.game = Game(size)
        self.ids.piece_layout.populate(self.game.board)
        self.ids.status.text = GameScreen.status_verbose['init']
    
    def load_game(self):
        self.game.load_game()
        self.ids.piece_layout.populate(self.game.board)
        self.update(False)
    
    def save_game(self):
        self.game.save_game()
    
    # Should only be called whenever the game state is altered, that is
    # when either player makes a move, or when undo/reset/redo is triggered.
    def update(self, ismove=True, upd_status=True):
        print("update received upd_status", upd_status)
        if upd_status:
            status = self.game.board.get_state()
            self.ids.status.text = GameScreen.status_verbose[status]
        self.ids.score1.text = "[color=d4af37]" + str(self.game.board.score1) + "[/color]"
        self.ids.score2.text = "[color=b0c4de]" + str(self.game.board.score2) + "[/color]"
        self.ids.piece_layout.update()
        if self.sound == "enabled" and ismove:      # Consider encapsulating this
            if self.game.board.capture:             # within a separate method.
                self.capture_sound.play()
            elif len(self.game.board.moves) % 2 == 0:
                self.move_sound1.play()
            else:
                self.move_sound2.play()
        self.start_turn(0)
    
    def import_settings(self, settings):
        print("game importing the following settings:")
        pprint(settings)
        self.player1    = settings['player1']
        self.player2    = settings['player2']
        self.mode       = settings['mode']
        self.difficulty = settings['difficulty']
        self.sound      = settings['sound']
        self.grid       = settings['grid']
        self.speed      = settings['speed']
        self.allowed    = settings['allowed']
        self.ids.piece_layout.set_mode(self.mode)
        self.ids.piece_layout.set_grid(self.grid)
        self.ids.piece_layout.set_speed(self.speed)
        self.ids.piece_layout.set_allowed(self.allowed)
        size_x, size_y = self.game.board.size
        new_x = settings['size_x']
        new_y = settings['size_y']
        if new_x != size_x or new_y != size_y:
            self.set_game_size((new_x, new_y))
        setvar = lambda dt: self.set_game_variant(settings['variant'])
        Clock.schedule_once(setvar, 0.25)
    
    # This way settings altered during gameplay will persist.
    def export_settings(self):
        return {
            'size_x':       self.game.board.size[0],
            'size_y':       self.game.board.size[1],
            'mode':         self.mode,
            'player1':      self.player1,
            'player2':      self.player2,
            'difficulty':   self.difficulty,
            'sound':        self.sound,
            'speed':        self.speed,
            'grid':         self.grid,
            'allowed':      self.allowed,
            'font':         self.ids.status.font_name,   # arbitrary choice
            'variant':      self.variant
        }


class PieceLayout(FloatLayout):
    move_indicator = ListProperty()
    
    def __init__(self, **kwargs):
        super(PieceLayout, self).__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)
        Window.bind(size=self.on_window_size)
        self.mode = "drag"
        self.speed = "fast"
        self.allowed = "enabled"
        self.animating = False
        self.anim_from = None
        self.anim_to = None
        self.animation = None
        self.populated = False
        self.populating = False
        self.enabled = False
        self.move_indicator = []
        self.selected = None
        self.offset = None
        self.X = None
        self.Y = None
        self.hold = False
    
    speed_map = {
        'immediate': 0,
        'fast': 0.12,
        'slow': 0.3
    }
    def animate_move(self, move, stop_callback):
        if self.abort_animation():  # concurrent animations will cause a crash
            restart_animation = lambda dt: self.animate_move(move, stop_callback)
            Clock.schedule_once(restart_animation, .1)
            return
        self.animating = True
        print("starting piece animation")
        self.anim_from = move['from pos']
        self.anim_to = move['to pos']
        self.show_anim(True)
        from_pos = self.coords_to_pos(self.anim_from)
        self.moving.pos = from_pos
        x, y = self.anim_from
        Clock.schedule_once(lambda dx: self.moving.set_value(self.board.piece_map[x][y]), 0.05)
        Clock.schedule_once(lambda dx: self.piece_map[x][y].set_value(0), 0.05)
        tox, toy = self.coords_to_pos(self.anim_to)
        trans = AnimationTransition.in_out_circ
        speed = PieceLayout.speed_map[self.speed]
        self.animation = Animation(x=tox, y=toy, duration=speed, transition=trans)
        self.animation.bind(on_complete=self.on_anim_stop)
        self.animation.bind(on_complete=stop_callback)
        Clock.schedule_once(lambda dx: self.piece_map[x][y].reload(), 0.05)
        Clock.schedule_once(lambda dx: self.moving.reload(), 0.05)
        self.animation.start(self.moving)
    
    def abort_animation(self):
        if self.animating:
            print("animation interrupted")
            self.show_anim(False)
            self.animation.stop(self.moving)
            return True
        return False
    
    def on_anim_stop(self, animation, widget):
        print("piece animation complete")
        self.show_anim(False)
        x, y = self.anim_from
        value = self.board.piece_map[x][y]
        self.piece_map[x][y].set_value(value)
        self.moving.set_value(0)
        self.anim_from = None
        self.anim_to = None
        self.animating = False
    
    # For some reason, within this method and animate_move, changes to certain
    # piece states cause some piece textures to glitch black unless the state
    # changes are scheduled. It might have something to do with the updates
    # needing to take place within the main UI thread. 
    def show_anim(self, show):
        if (not self.anim_from is None) and (not self.anim_to is None):
            fx, fy = self.anim_from
            tx, ty = self.anim_to
            if show:
                state = self.board.get_state()
                if state == 'player1' or state == 'init':
                    Clock.schedule_once(lambda dx: self.piece_map[fx][fy].set_state('player1'), 0.05)
                elif state == 'player2':
                    Clock.schedule_once(lambda dx: self.piece_map[fx][fy].set_state('player2'), 0.05)
                Clock.schedule_once(lambda dx: self.piece_map[tx][ty].set_state('allowed'), 0.05)
            else:
                Clock.schedule_once(lambda dx: self.piece_map[fx][fy].set_state('unselected'), 0.05)
                Clock.schedule_once(lambda dx: self.piece_map[tx][ty].set_state('unselected'), 0.05)
            
        
    def enable(self):
        if self.populated:
            self.enabled = True
        else:
            self.enabled = False
    
    def disable(self):
        self.enabled = False
    
    def set_mode(self, mode):
        self.unselect()
        self.mode = mode
    
    def set_grid(self, grid):
        for col in self.piece_map:
            for piece in col:
                piece.set_grid(grid)
        self.moving.set_grid(grid)
    
    def set_speed(self, speed):
        if speed in PieceLayout.speed_map.keys():
            self.speed = speed
        else:
            raise ValueError
    
    def set_allowed(self, allowed):
        self.allowed = allowed
        if allowed == 'disabled':
            self.hide_allowed()
    
    def on_move_indicator(self, instance, value):
        Clock.schedule_once(self.reset_indicator, 0.1)
    
    def reset_indicator(self, dt):
        self.move_indicator = []
    
    def on_touch_down(self, touch):
        if self.hold:
            return
        self.start_hold()
        if not self.collide_point(*touch.pos):
            self.unselect()
            return False
        if self.selected is None and self.enabled:
            self.select(touch)
        elif (not self.selected is None) and (not self.offset is None) and \
           self.enabled and self.mode == "click":
            dest = self.pos_to_coords(touch.pos)
            if self.valid_coords(self.selected) and self.valid_coords(dest):
                self.move_indicator = [*self.selected, *dest]
            self.unselect()
        else:
            print("piece layout on_touch_down rejected")
    
    def start_hold(self):
        self.hold = True
        Clock.schedule_once(self.end_hold, 0.1)
    
    def end_hold(self, dt):
        self.hold = False
    
    def on_touch_up(self, touch):
        print("piece layout on_touch_up received.")
        if (not self.selected is None) and (not self.offset is None) and \
           self.enabled and self.mode == "drag":
            dest = self.pos_to_coords(touch.pos)
            if self.valid_coords(self.selected) and self.valid_coords(dest):
                self.move_indicator = [*self.selected, *dest]
            self.unselect()
    
    def on_mouse_pos(self, mouse, pos):
        if (not self.selected is None) and (not self.offset is None) and \
           self.enabled and self.mode == "drag":
            px = pos[0] + self.offset[0]
            py = pos[1] + self.offset[1]
            self.moving.pos = (px, py)
        elif not self.animating and self.mode == "drag":
            self.update_offset(pos)
            px = pos[0] + self.offset[0]
            py = pos[1] + self.offset[1]
            self.moving.pos = (px, py)
    
    def select(self, touch):
        print("piece layout on_touch_down processed")
        self.selected = self.pos_to_coords(touch.pos)
        x, y = self.selected
#        if x >= self.board.size[0] or y >= self.board.size[1]:
#            self.selected = None
#            return
        self.update_offset(touch.pos)
        if self.mode == "drag":
            self.piece_map[x][y].set_value(0)
            self.moving.set_value(self.board.piece_map[x][y])
        state = self.board.get_state()
        if state == 'player1' or state == 'init':
            self.piece_map[x][y].set_state('player1')
        elif state == 'player2':
            self.piece_map[x][y].set_state('player2')
        else:
            self.selected = None
            self.offset = None
        self.show_allowed()
    
    def unselect(self):
        if self.selected:
            x, y = self.selected
            self.moving.set_value(0)
            self.piece_map[x][y].set_value(self.board.piece_map[x][y])
            self.piece_map[x][y].set_state('unselected')
            self.selected = None
            self.offset = None
            self.hide_allowed()
    
    def show_allowed(self):
        if self.allowed == 'disabled':
            return
        if (not self.selected is None) and (not self.board is None):
            allowed = self.board.get_allowed(*self.selected)
            for x, y in allowed:
                self.piece_map[x][y].set_state('allowed')
    
    def hide_allowed(self):
        for x in range(self.board.size[0]):
            for y in range(self.board.size[1]):
                self.piece_map[x][y].hide_allowed()
    
    def update_offset(self, pos):
        coords = self.pos_to_coords(pos)
        corner = self.coords_to_pos(coords)
        x_off = corner[0] - pos[0]
        y_off = corner[1] - pos[1]
        self.offset = (x_off, y_off)
    
    def on_parent(self, _, parent):
        parent.bind(height=self.on_parent_height)
    
    def on_window_size(self, _window, _size):
        self.update_dimensions()
    
    def on_parent_height(self, parent, height):
        self.update_dimensions()
    
    def update_dimensions(self):
        if (not self.X is None) and (not self.Y is None):
            max_height = self.parent.height
            max_width = self.parent.width   
            w_from_h = max_height * self.X / self.Y
            h_from_w = max_width * self.Y / self.X
            if w_from_h <= max_width:
                self.width = w_from_h
                self.height = max_height
            else:
                self.width = max_width
                self.height = h_from_w
            self.x = self.parent.x + (max_width - self.width) / 2
            self.y = self.parent.y + (max_height - self.height) / 2
        else:
            print("rejecting update dimensions")
    
    def valid_coords(self, coords):
        return coords[0] < self.X and coords[1] < self.Y
    
    def coords_to_pos(self, coords):
        piece_w = self.width / self.X
        piece_h = self.height / self.Y
        x = self.x + coords[0] * piece_w
        y = self.y + coords[1] * piece_h
        return (x, y)
    
    def pos_to_coords(self, pos):
        piece_w = self.width / self.X
        piece_h = self.height / self.Y
        x = floor((pos[0] - self.x) / piece_w)
        y = floor((pos[1] - self.y) / piece_h)
        return (x, y)
        
    # An instance of this class must be populated before any of its methods or
    # variables are accessed.
    def populate(self, board):
        print("preparing to populate PieceLayout")
        if self.populating:
            print("prevented collision in PieceLayout.populate")
            retry = lambda dt: self.populate(board)
            Clock.schedule_once(retry, .2)
            return
        self.populating = True
        if not isinstance(board, Board):
            raise ValueError
        self.clear_widgets()
        self.moving = None
        self.board = board
        self.X = board.size[0]
        self.Y = board.size[1]
        if max(board.size) <= 7:
            self.populate_pieces(board)
        else:
            self.populate_chips(board)
        self.update_dimensions()
        self.populated = True
        self.populating = False
    
    def populate_pieces(self, board):
        self.piece_map = []
        for x in range(self.X):
            self.piece_map.append([])
            for y in range(self.Y):
                value = board.piece_map[x][y]
                piece = Piece()
                piece._init(board.size, (x, y))
                self.piece_map[x].append(piece)
                self.add_widget(piece)
        self.moving = Piece()
        self.moving._init(board.size, (0, 0))
        self.moving.set_value(0)
        self.moving.set_state("transparent")
        self.add_widget(self.moving)
    
    def populate_chips(self, board):
        self.piece_map = []
        for x in range(self.X):
            self.piece_map.append([])
            for y in range(self.Y):
                value = board.piece_map[x][y]
                piece = ChipPiece()
                piece._init(board.size, (x, y))
                self.piece_map[x].append(piece)
                self.add_widget(piece)
        self.moving = ChipPiece()
        self.moving._init(board.size, (0, 0))
        self.moving.set_value(0)
        self.moving.set_state("transparent")
        self.add_widget(self.moving)
    
    # update must be called by the parent whenever the board state changes in
    # order for the changes to be reflected in the UI.
    def update(self):
        for x in range(self.X):
            for y in range(self.Y):
                value = self.board.piece_map[x][y]
                self.piece_map[x][y].set_value(value)
    
    def reload(self):
        for col in self.piece_map:
            for piece in col:
                piece.reload()
        self.moving.reload()

class ChipPiece(FloatLayout):
    gray = {
        0: "images/chips/poker 0.png",
        1: "images/chips/poker 1-1.png",
        2: "images/chips/poker 1-2.png",
        3: "images/chips/poker 1-3.png",
        4: "images/chips/poker 1-4.png",
        5: "images/chips/poker 1-5.png",
        6: "images/chips/poker 1-6.png"
    }
    gray_front = {
        0: "images/chips/poker 0.png",
        1: "images/chips/poker 1-1-f.png",
        2: "images/chips/poker 1-2-f.png",
        3: "images/chips/poker 1-3-f.png",
        4: "images/chips/poker 1-4-f.png",
        5: "images/chips/poker 1-5-f.png",
        6: "images/chips/poker 1-6-f.png"
    }
    gray_back = {
        0: "images/chips/poker 0.png",
        1: "images/chips/poker 1-1-b.png",
        2: "images/chips/poker 1-2-b.png",
        3: "images/chips/poker 1-3-b.png",
        4: "images/chips/poker 1-4-b.png",
        5: "images/chips/poker 1-5-b.png",
        6: "images/chips/poker 1-6-b.png"
    }
    red = {
        0: "images/chips/poker 0.png",
        1: "images/chips/poker 5-1.png",
        2: "images/chips/poker 5-2.png",
        3: "images/chips/poker 5-3.png",
        4: "images/chips/poker 5-4.png",
        5: "images/chips/poker 5-5.png",
        6: "images/chips/poker 5-6.png"
    }
    red_front = {
        0: "images/chips/poker 0.png",
        1: "images/chips/poker 5-1-f.png",
        2: "images/chips/poker 5-2-f.png",
        3: "images/chips/poker 5-3-f.png",
        4: "images/chips/poker 5-4-f.png",
        5: "images/chips/poker 5-5-f.png",
        6: "images/chips/poker 5-6-f.png"
    }
    red_back = {
        0: "images/chips/poker 0.png",
        1: "images/chips/poker 5-1-b.png",
        2: "images/chips/poker 5-2-b.png",
        3: "images/chips/poker 5-3-b.png",
        4: "images/chips/poker 5-4-b.png",
        5: "images/chips/poker 5-5-b.png",
        6: "images/chips/poker 5-6-b.png"
    }
    background = {
        'transparent':  "images/tiles/square_transparent.png",
        'unselected':   "images/tiles/square_empty.png",
        'grid':         "images/tiles/square_grid.png",
        'player1':      "images/tiles/player-1-square.png",
        'player2':      "images/tiles/player-2-square.png",
        'allowed':      "images/tiles/allowed-1.png"
    }
    
    def __init__(self, **kwargs):
        super(ChipPiece, self).__init__(**kwargs)
        self.coords = None
        self.grid = 'enabled'
        self.set_value(1)
        self.state = 'unselected'
        self.set_state(self.state)
    
    def _init(self, size, coords):
        self.X = size[0]
        self.Y = size[1]
        self.coords = coords
    
    def on_parent(self, instance, parent):
        if not parent is None:
            parent.bind(size=self.update_dimensions)
            parent.bind(pos=self.update_dimensions)
    
    def update_dimensions(self, _instance, _value):
        if not self.coords is None and not self.size is None and not self.parent is None:
            self.width = self.parent.width / self.X
            self.height = self.parent.height / self.Y
            self.x = self.parent.x + self.coords[0] * self.width
            self.y = self.parent.y + self.coords[1] * self.height
    
    def reload(self):
        self.ids.gray.reload()
        self.ids.red.reload()
        self.ids.background.reload()
    
    def set_grid(self, grid):
        self.grid = grid
        self.set_state(self.state)
    
    def set_value(self, value):
        if not self.is_value(value):
            raise ValueError
        gval = value % 5
        rval = int(value / 5)
        if rval == 0 or gval == 0:
            self.ids.gray.source = ChipPiece.gray[gval]
            self.ids.red.source = ChipPiece.red[rval]
        else:
            self.ids.gray.source = ChipPiece.gray_back[gval]
            self.ids.red.source = ChipPiece.red_front[rval]
    
    def is_value(self, value):
        c1 = 0 <= value <= 42
        c2 = type(value) == type(0)
        return c1 and c2
    
    # Set the state of the piece to "unselected", "player1", or "player2".
    def set_state(self, state):
        if state not in ChipPiece.background.keys():
            raise ValueError
        self.state = state
        if state == 'unselected' and self.grid == "enabled":
            self.ids.background.source = ChipPiece.background['grid']
        else:
            self.ids.background.source = ChipPiece.background[state]
    
    def hide_allowed(self):
        print("piece.hide_allowed called.")
        if self.state == "allowed":
            print("state is allowed, changing.")
            self.set_state("unselected")
    

class Piece(FloatLayout):
    f_srcs = {
        0: "images/pieces/cylinder 0.png",
        1: "images/pieces/cylinder 1.png",      
        2: "images/pieces/cylinder 2.png",
        3: "images/pieces/cylinder 3.png",
        4: "images/pieces/cylinder 4.png",
        5: "images/pieces/cylinder 5.png",
        6: "images/pieces/cylinder 6.png"
    }
    b_srcs = {
        'transparent':  "images/tiles/square_transparent.png",
        'unselected':   "images/tiles/square_empty.png",
        'grid':         "images/tiles/square_grid.png",
        'player1':      "images/tiles/player-1-square.png",
        'player2':      "images/tiles/player-2-square.png",
        'allowed':      "images/tiles/allowed-1.png"
    }
    
    def __init__(self, **kwargs):
        super(Piece, self).__init__(**kwargs)
        self.coords = None
        self.grid = 'enabled'
        self.set_value(1)
        self.state = 'unselected'
        self.set_state(self.state)
    
    def _init(self, size, coords):
        self.X = size[0]
        self.Y = size[1]
        self.coords = coords
    
#    def on_pos(self, instance, pos):
#        self.reload()
    
    def on_parent(self, instance, parent):
        if not parent is None:
            parent.bind(size=self.update_dimensions)
            parent.bind(pos=self.update_dimensions)
    
    def update_dimensions(self, _instance, _value):
        if not self.coords is None and not self.size is None and not self.parent is None:
            self.width = self.parent.width / self.X
            self.height = self.parent.height / self.Y
            self.x = self.parent.x + self.coords[0] * self.width
            self.y = self.parent.y + self.coords[1] * self.height
    
    def reload(self):
        print("Piece received reload call")
        self.ids.foreground.reload()
        self.ids.background.reload()
    
    def set_grid(self, grid):
        self.grid = grid
        self.set_state(self.state)
    
    # Set the value of the piece to an integer such that 0 <= value <= 6.
    def set_value(self, value):
        if value not in Piece.f_srcs.keys():
            raise ValueError
        self.ids.foreground.source = Piece.f_srcs[value]
    
    # Set the state of the piece to "unselected", "player1", or "player2".
    def set_state(self, state):
        if state not in Piece.b_srcs.keys():
            raise ValueError
        self.state = state
        if state == 'unselected' and self.grid == "enabled":
            self.ids.background.source = Piece.b_srcs['grid']
        else:
            self.ids.background.source = Piece.b_srcs[state]
    
    def hide_allowed(self):
        if self.state == "allowed":
            self.set_state("unselected")
        

























