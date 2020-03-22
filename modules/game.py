from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.properties import ListProperty, OptionProperty, BooleanProperty
from kivy.animation import Animation, AnimationTransition
from kivy.core.window import Window
from kivy.clock import Clock

import pygame

from modules.board import Board

import threading

from math import floor
from pprint import pprint

class Game():
    def __init__(self, size=(7, 7)):
        self.board = Board(size)
        self.line = []
        self.indx = -1      # no moves yet
    
    def get_state(self):
        return self.board.state()
    
    def make_move(self, frompos, topos):
        if self.indx + 1 < len(self.line):
            c1 = self.line[self.indx+1]['from pos'] == frompos
            c2 = self.line[self.indx+1]['to pos'] == topos
            if c1 and c2:
                print("make_move converted into redo")
                assert(self.redo() == True)
                return True
        try:
            self.board.push({'from pos': frompos, 'to pos': topos})
        except ValueError:
            return False
        self.indx = len(self.board.moves) - 1
        self.line = [move for move in self.board.moves]
        return True
    
    def choose_move(self, callback, difficulty):
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
        elif difficulty == "infuriating":
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
        if self.indx >= 0:
            pop = self.board.pop()
            self.indx -= 1
            print("popped the following move:", pop)
            print("index changed from %d to %d" % (self.indx + 1, self.indx))
            return True
        else:
            return False
    
    def redo(self):
        if self.indx + 1 < len(self.line):
            self.indx += 1
            self.board.push(self.line[self.indx])
            return True
        else:
            return False
    
    def reset(self):
        if self.line:
            self.board = Board()
            self.line = []
            self.indx = -1
            return True
        else:
            return False


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
#    gameover = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        Window.bind(size=self.on_window_size)
        self.game = Game()
        self.turns = 0
#        self.gameover = False
        self.searching = False
        self.difficulty = "challening"
        self.font = "fonts/Brendohand.otf"
        self.grid = "enabled"
        self.sound = "enabled"
        pygame.mixer.pre_init(22050, -16, 2, 2048) 
        pygame.mixer.init()
        self.move_sound1 = pygame.mixer.Sound("audio/move.wav")
        self.move_sound2 = pygame.mixer.Sound("audio/move.wav")
        self.capture_sound = pygame.mixer.Sound("audio/capture.wav")
        self.pending = None
        self.animations_complete = 0    # for debugging
        self.minimaxes_complete = 0     # also for debugging
        self.ids.piece_layout.populate(self.game.board)
        self.ids.piece_layout.bind(move_indicator=self.on_move_indicator)
        self.ids.piece_layout.bind(size=self.on_piece_layout_size)
        self.ids.status.text = GameScreen.status_verbose['init']
    
#    def on_gameover(self, instance, value):
#        print("gameover set to ", value)
    
    def on_touch_up(self, touch):
        if self.paused and self.ids.piece_layout.collide_point(*touch.pos):
            print("game screen on_touch_up digested.")
            status = self.game.board.get_state()
            self.ids.status.text = GameScreen.status_verbose[status]
            self.paused = False
            return True
        else:
            print("game screen on_touch_up ignored")
            super(GameScreen, self).on_touch_up(touch)
            return False
    
    def on_enter(self):
        self.reload()
        if self.human_turn():
            self.start_turn(0)
        else:
            self.paused = True
    
    def on_paused(self, instance, paused):
        print("on_paused received value %r" % paused)
        if paused:
            self.ids.status.text = "Game Paused"
            self.ids.piece_layout.disable()
        else:
#            status = self.game.board.get_state()
#            self.ids.status.text = GameScreen.status_verbose[status]
            if not self.human_turn():
                self.redo()
            self.start_turn(0)
    
    def start_turn(self, dt):
        if self.game.board.game_over():
            print("caught gameover from start_turn")
#            self.gameover = True
        else:
#            self.turns += 1
#            if self.turns == 10:
#                self.ids.piece_layout.reload() # prevent black textures glitch.
            print("")
            if self.human_turn():
                print("New turn for human player.")
                self.paused = False
                self.ids.piece_layout.enable()
            else:
                print("New turn for computer player.")
                self.ids.piece_layout.disable()
                self.choose_move(0)
    
    def human_turn(self):
        h1 = self.player1 == "human" and len(self.game.board.moves) % 2 == 0
        h2 = self.player2 == "human" and len(self.game.board.moves) % 2 == 1
        return h1 or h2
    
    def choose_move(self, dt):
        if not self.paused:
            print("choosing new move for the computer")
            self.game.choose_move(self.minimax_callback, self.difficulty)
            self.searching = True
    
    def minimax_callback(self, move):
        if self.searching:
            print("minimax callback reached %d times." % self.minimaxes_complete)
            self.minimaxes_complete += 1
#            self.pending = move
#            assert(not move is None)
#            self.ids.piece_layout.animate_move(move, self.on_anim_complete)
            self.searching = False
            self.animate_move(move)
        else:
            print("minimax callback ignored.")
    
    def animate_move(self, move):
        self.pending = move
        assert(not move is None)
        self.ids.piece_layout.animate_move(move, self.on_anim_complete)
    
    def on_anim_complete(self, animation, widget):
        print("on_anim_complete reached %d times." % self.animations_complete)
        self.animations_complete += 1
        self.game.make_move(self.pending['from pos'], self.pending['to pos'])
        self.pending = None
        self.update()
    
    def on_move_indicator(self, instance, value):
        if len(value) == 4:
            print("received", value, "from move indicator")
            frompos = tuple(value[:2])
            topos   = tuple(value[2:])
            if self.game.make_move(frompos, topos):
                self.update()
            else:
                print("self.game.make_move returned False.")
    
    def on_window_size(self, window, size):
        self.update_controls()
    
    def on_piece_layout_size(self, instance, size):
        self.update_controls()
    
    def update_controls(self):
        width = self.ids.piece_layout.width
        self.ids.controls.width = min(width * 4 / 3, Window.size[0])
        self.ids.controls.x = (Window.size[0] - self.ids.controls.width) / 2
    
    def undo(self, dt=0):
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
        if self.ids.piece_layout.animating:
            print("rescheduling redo")
            self.ids.piece_layout.abort_animation()
            Clock.schedule_once(self.redo, 0.05)
            return
        print("committing to redo")
        self.searching = False
#        res = self.game.redo()
        move = self.game.next_move()
        if not move is None:
            self.paused = True
            self.animate_move(self.game.next_move())
            self.update(True, False)
            self.paused = True
    
    def reset(self, dt=0):
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
    
    def reload(self):
        self.ids.piece_layout.reload()
    
    def set_font(self, font):
        print("setting font for game")
        self.ids.status.font_name = font
        self.ids.score1.font_name = font
        self.ids.score2.font_name = font
        self.ids.undo.font_name = font
        self.ids.redo.font_name = font
        self.ids.reset.font_name = font
        self.ids._reload.font_name = font
    
    def set_game_size(self, size):
        self.game = Game(size)
        self.ids.piece_layout.populate(self.game.board)
        self.ids.status.text = GameScreen.status_verbose['init']
    
    # Should only be called whenever the game state is altered, that is
    # when either player makes a move, or when undo/reset/redo is triggered.
    def update(self, ismove=True, upd_status=True):
#        if self.game.board.game_over():
#            self.gameover = True
#        else:
#            self.gameover = False
        if upd_status:
            status = self.game.board.get_state()
            self.ids.status.text = GameScreen.status_verbose[status]
        self.ids.score1.text = str(self.game.board.score1)
        self.ids.score2.text = str(self.game.board.score2)
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
        self.player1    = settings['player1']
        self.player2    = settings['player2']
        self.difficulty = settings['difficulty']
        self.sound      = settings['sound']
        self.grid       = settings['grid']
        self.ids.piece_layout.set_grid(self.grid)
        size_x, size_y = self.game.board.size
        new_x = settings['size_x']
        new_y = settings['size_y']
        if new_x != size_x or new_y != size_y:
            self.set_game_size((new_x, new_y))
    
    # This way settings altered during gameplay will persist.
    def export_settings(self):
        return {
            'size_x':       self.game.board.size[0],
            'size_y':       self.game.board.size[1],
            'mode':         "drag",
            'player1':      self.player1,
            'player2':      self.player2,
            'difficulty':   self.difficulty,
            'sound':        self.sound,
            'speed':        "fast",
            'grid':         self.grid,
            'font':         self.ids.status.font_name   # arbitrary choice
        }


class PieceLayout(FloatLayout):
    move_indicator = ListProperty()
    
    def __init__(self, **kwargs):
        super(PieceLayout, self).__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)
        Window.bind(size=self.on_window_size)
        self.animating = False
        self.anim_from = None
        self.anim_to = None
        self.animation = None
        self.populated = False
        self.enabled = False
        self.move_indicator = []
        self.selected = None
        self.offset = None
        self.X = None
        self.Y = None
    
    def animate_move(self, move, stop_callback):
        self.animating = True
        print("starting piece animation")
        self.anim_from = move['from pos']
        self.anim_to = move['to pos']
        from_pos = self.coords_to_pos(self.anim_from)
        self.moving.pos = from_pos
        x, y = self.anim_from
        self.moving.set_value(self.board.piece_map[x][y])
        self.piece_map[x][y].set_value(0)
        tox, toy = self.coords_to_pos(self.anim_to)
        trans = AnimationTransition.in_out_circ
        self.animation = Animation(x=tox, y=toy, duration=0.1, transition=trans)
        self.animation.bind(on_complete=self.on_anim_stop)
        self.animation.bind(on_complete=stop_callback)
        self.animation.start(self.moving)
    
    def set_grid(self, grid):
        for col in self.piece_map:
            for piece in col:
                piece.set_grid(grid)
        self.moving.set_grid(grid)
    
    def abort_animation(self):
        if self.animating:
            self.animation.stop(self.moving)
            return True
        return False
    
    def on_anim_stop(self, animation, widget):
        print("piece animation complete")
        x, y = self.anim_from
        value = self.board.piece_map[x][y]
        self.piece_map[x][y].set_value(value)
        self.moving.set_value(0)
        self.anim_from = None
        self.anim_to = None
        self.animating = False
        
    def enable(self):
        if self.populated:
            self.enabled = True
        else:
            self.enabled = False
    
    def disable(self):
        self.enabled = False
    
    def on_move_indicator(self, instance, value):
        Clock.schedule_once(self.reset_indicator, 0.1)
    
    def reset_indicator(self, dt):
        self.move_indicator = []
    
    def on_touch_down(self, touch):
        if self.enabled:
            self.selected = self.pos_to_coords(touch.pos)
            x, y = self.selected
            if x >= self.board.size[0] or y >= self.board.size[1]:
                self.selected = None
                return
            self.update_offset(touch.pos)
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
    
    def on_touch_up(self, touch):
        print("piece layout on_touch_up received.")
        if (not self.selected is None) and (not self.offset is None) and self.enabled:
            dest = self.pos_to_coords(touch.pos)
            self.move_indicator = [*self.selected, *dest]
            x, y = self.selected
            self.moving.set_value(0)
            self.piece_map[x][y].set_value(self.board.piece_map[x][y])
            self.piece_map[x][y].set_state('unselected')
            self.selected = None
            self.offset = None
    
    def on_mouse_pos(self, mouse, pos):
        if (not self.selected is None) and (not self.offset is None) and self.enabled:
            px = pos[0] + self.offset[0]
            py = pos[1] + self.offset[1]
            self.moving.pos = (px, py)
        elif not self.animating:
            self.update_offset(pos)
            px = pos[0] + self.offset[0]
            py = pos[1] + self.offset[1]
            self.moving.pos = (px, py)
    
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
        if not self.X is None and not self.Y is None:
            max_height = self.parent.height
            max_width = Window.size[0]
            w_from_h = max_height * self.X / self.Y
            h_from_w = max_width * self.Y / self.X
            if w_from_h <= max_width:
                self.width = w_from_h
                self.height = max_height
            else:
                self.width = max_width
                self.height = h_from_w
            self.x = (max_width - self.width) / 2
            self.y = max_height * 0.1
    
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
        if not isinstance(board, Board):
            raise ValueError
        for child in self.children:
            self.remove_widget(child)
        self.moving = None
        self.board = board
        self.piece_map = []
        self.X = board.size[0]  # for quick access
        self.Y = board.size[1]
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
        self.update_dimensions()
        self.populated = True
    
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
        'player1':      "images/tiles/square_red.png",
        'player2':      "images/tiles/square_blue.png"
    }
    
    def __init__(self, **kwargs):
        super(Piece, self).__init__(**kwargs)
        self.coords = None
        self.grid = "enabled"
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
    
    def reload(self):
        print("Piece received reload call")
        self.ids.foreground.reload()
        self.ids.background.reload()
    
    def update_dimensions(self, _instance, _value):
        if not self.coords is None and not self.size is None and not self.parent is None:
            self.width = self.parent.width / self.X
            self.height = self.parent.height / self.Y
            self.x = self.parent.x + self.coords[0] * self.width
            self.y = self.parent.y + self.coords[1] * self.height
    
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
        
























