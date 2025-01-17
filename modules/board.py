import random
from math import floor


# Within the Board class, 'moves' is a list of dictionaries, where each 'move',
# or dictionary, has the following elements:
#   'from pos'  - set by user
#   'to pos'    - set by user
#   'from val'  - inferred by Board
#   'to val'    - inferred by Board
class Board():
    def __init__(self, size=(7, 7), moves=[], rules="standard"):
        print("Creating new board of size %d, %d" % size)
        self.size = size
        self.minsize = min(size)
        self.piece_map = self.new_piece_map()
        self.moves = [] # managed by self.push
        self.score1 = 0
        self.score2 = 0
        self.capture = False # true iff recent push involved a capture
        self.minimax_count = 0
        if not self.valid_size():
            raise ValueError
        for move in moves:
            self.push(move)
    
    # Maximum allowable minsize is capped by the highest number of
    # pieces in a single 'cylinder n[c].png'.
    def valid_size(self):
        if min(self.size) >= 3 and min(self.size) <= 42:
            return True
        else:
            return False
    
    # Return a two dimensional list of 1s, left->right, bottom->top.
    def new_piece_map(self):
        print("creating new piece map and size is %d, %d" % self.size)
        piece_map = []
        for i in range(self.size[0]):
            piece_map.append([])
            for j in range(self.size[1]):
                piece_map[i].append(1)
        return piece_map
    
    #end_states = ['player1 win', 'player2 win', 'stalemate']
    def game_over(self):
        if len(self.legal_moves()) == 0:
            return True
        else:
            return False
#        if self.get_state() in Board.end_states:
#            return True
#        else:
#            return False
    
    # init; player1; player2; player1 win; player2 win; stalemate
    def get_state(self):
        l = len(self.moves)
        if l == 0:
            return 'init'
#        elif self.four_move_rep():
        elif self.game_over():
            if self.score1 > self.score2:
                return 'player1 win'
            elif self.score1 < self.score2:
                return 'player2 win'
            else:
                return 'stalemate'
        elif l % 2 == 0:
            return 'player1'
        else:
            return 'player2' 
    
    def four_move_rep(self):
        if len(self.moves) < 4:
            return False
        c1 = self.moves[-1]['from pos'] == self.moves[-3]['from pos']
        c2 = self.moves[-2]['from pos'] == self.moves[-4]['from pos']
        c3 = self.moves[-1]['to pos'] == self.moves[-3]['to pos']
        c4 = self.moves[-2]['to pos'] == self.moves[-4]['to pos']
        if c1 and c2 and c3 and c4:
            return True
        else:
            return False
    
    # Will raise a ValueError if move is not a legal one.
    # piece_map is expected to be a two dimensional python array with shape
    # (self.height, self.width). move is expected to be a dictionary which maps
    # the strings 'from' and 'to' to respective indices into the piece_map.
    def push(self, move):
        if not self.is_legal(move):
            print("board.push failed.")
            raise ValueError
        print("pushing following move to board:", move)
        fpos = move['from pos']
        tpos = move['to pos']
        fval = self.piece_map[fpos[0]][fpos[1]]
        tval = self.piece_map[tpos[0]][tpos[1]]
        if fval + tval >= self.minsize - 1:
            self.capture = True
            if len(self.moves) % 2 == 0:
                self.score1 += fval + tval
            else:
                self.score2 += fval + tval
            tval = 0
        else:
            self.capture = False
            tval = tval + fval
        move['from val'] = self.piece_map[fpos[0]][fpos[1]]
        move['to val'] = self.piece_map[tpos[0]][tpos[1]]
        self.piece_map[fpos[0]][fpos[1]] = 0
        self.piece_map[tpos[0]][tpos[1]] = tval
        self.moves.append(move)
    
    def pop(self):
        move = self.moves.pop()
        fpos = move['from pos']
        tpos = move['to pos']
        fval = move['from val']
        tval = move['to val']
        if fval + tval >= self.minsize - 1 and len(self.moves) % 2 == 0:  # player one
            self.score1 -= fval + tval
        elif fval + tval >= self.minsize - 1 and len(self.moves) % 2 == 1:
            self.score2 -= fval + tval
        self.piece_map[fpos[0]][fpos[1]] = fval
        self.piece_map[tpos[0]][tpos[1]] = tval
        return move
    
    def copy(self):
        newboard = self.__class__(self.size)    # using Board would require
        for move in self.moves:                 # subclasses to reimplement
            newboard.push(move)
        return newboard
    
    # Distance is defined as a list of possible distances.
    #   1. The distance between two squares that are not on the same horizontal
    #      or vertical level is not defined, and the function returns empty.
    #   2. The distance between two squares of equal pos is irrelevant, and
    #      the function will also return empty in this case.
    #   3. If the distance is defined, then the three possibilities are
    #       i.   distance between the squares
    #       ii.  the sum of the relevant position values of the squares
    #       iii. the sum of the relevant shifted pos values of the squares.
    def distance(self, A, B):
        if A[0] == B[0] and A[1] != B[1]:
            return [           abs(A[1] - B[1]),
                                   A[1] + B[1],
                    (self.size[1] - A[1] - 1) + (self.size[1] - B[1] - 1)]
        elif A[1] == B[1] and A[0] != B[0]:
            return [           abs(A[0] - B[0]),
                                   A[0] + B[0],
                    (self.size[0] - A[0] - 1) + (self.size[0] - B[0] - 1)]
        return []
    
    def is_legal(self, move):
        fpos = move['from pos']
        tpos = move['to pos']
        fval = self.piece_map[fpos[0]][fpos[1]]
        tval = self.piece_map[tpos[0]][tpos[1]]
        if fval in self.distance(fpos, tpos) and tval > 0:
            return True
        else:
            return False
    
    # Return a list of legal moves via brute force. On a 7x7 grid this will take
    # 7 ** 4 = 2401 iterations. 'from val' and 'to val' are included to assist
    # sorting moves before each minimax search.
    def legal_moves(self):
        legal_moves = []
        for x1 in range(self.size[0]):
            for y1 in range(self.size[1]):
                for x2 in range(self.size[0]):
                    for y2 in range(self.size[1]):
                        move = {'from pos': (x1, y1),
                                'to pos': (x2, y2),
                                'from val': self.piece_map[x1][y1],
                                'to val': self.piece_map[x2][y2]
                        }
                        if self.is_legal(move):
                            legal_moves += [move]
        return legal_moves
   
    def get_allowed(self, x, y):
        allowed = []
        for x2 in range(self.size[0]):
            for y2 in range(self.size[1]):
                move = {'from pos': (x, y),
                        'to pos': (x2, y2),
                        'from val': self.piece_map[x][y],
                        'to val': self.piece_map[x2][y2]
                }
                if self.is_legal(move):
                    allowed.append((x2, y2))
        return allowed
    
    # Produces the best move for the current player using minimax search.
    def best_move(self, callback, depth=1, breadth=16, handicap=0):
        print("Note that board has a size of", self.size)
        assert(type(breadth) == type(0))
        print("Searching for best move with d=%d, b=%d, h=%d" % (depth, breadth, handicap))
        sb = self.copy()    # search board, so that current state isn't altered
        ib = breadth + handicap     # index used to obtain moves of size breadth
        self.minimax_count = 0
        moves = self.legal_moves()
        print("%d legal moves to choose from" % len(moves))
        self.sort(moves)
        moves = moves if len(moves) <= breadth else moves[:ib]
        print("%d moves after sorting and narrowing" % len(moves))
        moves = self.purge(moves, handicap)
        print("%d moves after applying handicap" % len(moves))
        if len(moves) == 1:
            callback(moves[0])
            return
        print("preparing to evaluate %d moves" % len(moves))
        if len(self.moves) % 2 == 0:
            scores = [sb.minimax(move, depth, breadth, True) for move in moves]
            callback(max(scores, key=lambda x: x[1])[0])
        else:
            scores = [sb.minimax(move, depth, breadth, False) for move in moves]
            callback(min(scores, key=lambda x: x[1])[0])
    
    # Evaluates the given move to produce a minimax score.
    def minimax(self, move, depth, breadth, max_player1):
        self.minimax_count += 1
        if self.minimax_count % 50 == 0:
            #print("minimax iteration %d reached" % self.minimax_count)
            pass
        if self.minimax_count % 10000 == 0:
            raise RuntimeError
        self.push(move)
        moves = self.legal_moves()
        self.sort(moves)
        moves = moves if len(moves) <= breadth else moves[:breadth]
        random.shuffle(moves)   # remove this to get the annoying strategy back
        if len(moves) == 0 or depth == 0:
            score = self.score1 - self.score2
            return (self.pop(), score)
        if max_player1:
            scores = [self.minimax(move, depth - 1, breadth, not max_player1)[1]
                      for move in moves]
            return (self.pop(), min(scores))
        else:
            scores = [self.minimax(move, depth - 1, breadth, not max_player1)[1]
                      for move in moves]
            return (self.pop(), max(scores))
    
    def sort(self, moves):
        moves.sort(key=lambda move: move['from val'] + move['to val'])
        moves.reverse()
    
    # Remove n randomly selected elements of moves. 
    def purge(self, moves, n):
        max_n = floor(len(moves) / 3)
        n = min(n, max_n)
#        print("preparing to purge %d moves from" % n, moves)
        selection = random.sample(moves, k=n)
        for item in selection:
            moves.remove(item)
        return moves


class GolfVariant(Board):
    def get_state(self):
        l = len(self.moves)
        if l == 0:
            return 'init'
#        elif self.four_move_rep():
        elif self.game_over():
            if self.score1 > self.score2:
                return 'player2 win'
            elif self.score1 < self.score2:
                return 'player1 win'
            else:
                return 'stalemate'
        elif l % 2 == 0:
            return 'player1'
        else:
            return 'player2' 
    
    def best_move(self, callback, depth=1, breadth=16, handicap=0):
        print("Note that board has a size of", self.size)
        assert(type(breadth) == type(0))
        print("Searching for best move with d=%d, b=%d, h=%d" % (depth, breadth, handicap))
        sb = self.copy()    # search board, so that current state isn't altered
        ib = breadth + handicap     # index used to obtain moves of size breadth
        self.minimax_count = 0
        moves = self.legal_moves()
        random.shuffle(moves)
        print("%d legal moves to choose from" % len(moves))
        moves = moves if len(moves) <= breadth else moves[:ib]
        print("%d moves after sorting and narrowing" % len(moves))
        moves = self.purge(moves, handicap)
        print("%d moves after applying handicap" % len(moves))
        if len(moves) == 1:
            callback(moves[0])
            return
        print("preparing to evaluate %d moves" % len(moves))
        if len(self.moves) % 2 == 0:
            scores = [sb.minimax(move, depth, breadth, True) for move in moves]
            callback(max(scores, key=lambda x: x[1])[0])
        else:
            scores = [sb.minimax(move, depth, breadth, False) for move in moves]
            callback(min(scores, key=lambda x: x[1])[0])
    
    def minimax(self, move, depth, breadth, max_player1):
        self.minimax_count += 1
        if self.minimax_count % 10000 == 0:
            raise RuntimeError
        self.push(move)
        moves = self.legal_moves()
        moves = moves if len(moves) <= breadth else moves[:breadth]
        if len(moves) == 0 or depth == 0:
            score = self.score2 - self.score1
            return (self.pop(), score)
        if max_player1:
            scores = [self.minimax(move, depth - 1, breadth, not max_player1)[1]
                      for move in moves]
            return (self.pop(), min(scores))
        else:
            scores = [self.minimax(move, depth - 1, breadth, not max_player1)[1]
                      for move in moves]
            return (self.pop(), max(scores))


class CheckersVariant(Board):
    def push(self, move):
        if not self.is_legal(move):
            raise ValueError
        fpos = move['from pos']
        tpos = move['to pos']
        fval = self.piece_map[fpos[0]][fpos[1]]
        tval = self.piece_map[tpos[0]][tpos[1]]
        inters = self.intermediates(move)
        inters_vals = 0
        inters_map = {}
        for coords in inters:
            x, y = coords
            inters_map[coords] = self.piece_map[x][y]
            inters_vals += inters_map[coords]
            self.piece_map[x][y] = 0
        if fval + tval >= self.minsize - 1:
            self.capture = True
            if len(self.moves) % 2 == 0:
                self.score1 += fval + tval + inters_vals
            else:
                self.score2 += fval + tval + inters_vals
            tval = 0
        else:
            if len(self.moves) % 2 == 0:
                self.score1 += inters_vals
            else:
                self.score2 += inters_vals
            if inters_vals == 0:
                self.capture = False
            else:
                self.capture = True
            tval = tval + fval
        move['from val'] = self.piece_map[fpos[0]][fpos[1]]
        move['to val'] = self.piece_map[tpos[0]][tpos[1]]
        move['inters'] = inters_map
        self.piece_map[fpos[0]][fpos[1]] = 0
        self.piece_map[tpos[0]][tpos[1]] = tval
        self.moves.append(move)
    
    def pop(self):
        move = self.moves.pop()
        inters = move['inters']
        inters_vals = 0
        for coords in inters:
            x, y = coords
            inters_vals += inters[coords]
            self.piece_map[x][y] = inters[coords]
        fpos = move['from pos']
        tpos = move['to pos']
        fval = move['from val']
        tval = move['to val']
        if fval + tval >= self.minsize - 1 and len(self.moves) % 2 == 0:  # player one
            self.score1 -= fval + tval
        elif fval + tval >= self.minsize - 1 and len(self.moves) % 2 == 1:
            self.score2 -= fval + tval
        if len(self.moves) % 2 == 0:
            self.score1 -= inters_vals
        elif len(self.moves) % 2 == 1:
            self.score2 -= inters_vals
        self.piece_map[fpos[0]][fpos[1]] = fval
        self.piece_map[tpos[0]][tpos[1]] = tval
        return move
    
    # Returns a list of positions (coordinates) between from pos and to pos.
    def intermediates(self, move):
        fx, fy = move['from pos']
        tx, ty = move['to pos']
        if fx == tx and fy != ty:
            ys = range(min(fy, ty) + 1, max(fy, ty))
            return [(fx, y) for y in ys]
        elif fy == ty and fx != tx:
            xs = range(min(fx, tx) + 1, max(fx, tx))
            return [(x, fy) for x in xs]
        else:
            raise ValueError


class CheckersVariant2(Board):
    def push(self, move):
        if len(self.moves) < 6:
            super(CheckersVariant2, self).push(move)
            return
        if not self.is_legal(move):
            raise ValueError
        fpos = move['from pos']
        tpos = move['to pos']
        fval = self.piece_map[fpos[0]][fpos[1]]
        tval = self.piece_map[tpos[0]][tpos[1]]
        inters = self.intermediates(move)
        inters_vals = 0
        inters_map = {}
        for coords in inters:
            x, y = coords
            inters_map[coords] = self.piece_map[x][y]
            inters_vals += inters_map[coords]
            self.piece_map[x][y] = 0
        if fval + tval >= self.minsize - 1:
            self.capture = True
            if len(self.moves) % 2 == 0:
                self.score1 += fval + tval + inters_vals
            else:
                self.score2 += fval + tval + inters_vals
            tval = 0
        else:
            if len(self.moves) % 2 == 0:
                self.score1 += inters_vals
            else:
                self.score2 += inters_vals
            if inters_vals == 0:
                self.capture = False
            else:
                self.capture = True
            tval = tval + fval
        move['from val'] = self.piece_map[fpos[0]][fpos[1]]
        move['to val'] = self.piece_map[tpos[0]][tpos[1]]
        move['inters'] = inters_map
        self.piece_map[fpos[0]][fpos[1]] = 0
        self.piece_map[tpos[0]][tpos[1]] = tval
        self.moves.append(move)
    
    def pop(self):
        if len(self.moves) <= 6:
            return super(CheckersVariant2, self).pop()
        move = self.moves.pop()
        inters = move['inters']
        inters_vals = 0
        for coords in inters:
            x, y = coords
            inters_vals += inters[coords]
            self.piece_map[x][y] = inters[coords]
        fpos = move['from pos']
        tpos = move['to pos']
        fval = move['from val']
        tval = move['to val']
        if fval + tval >= self.minsize - 1 and len(self.moves) % 2 == 0:  # player one
            self.score1 -= fval + tval
        elif fval + tval >= self.minsize - 1 and len(self.moves) % 2 == 1:
            self.score2 -= fval + tval
        if len(self.moves) % 2 == 0:
            self.score1 -= inters_vals
        elif len(self.moves) % 2 == 1:
            self.score2 -= inters_vals
        self.piece_map[fpos[0]][fpos[1]] = fval
        self.piece_map[tpos[0]][tpos[1]] = tval
        return move
    
    # Returns a list of positions (coordinates) between from pos and to pos.
    def intermediates(self, move):
        fx, fy = move['from pos']
        tx, ty = move['to pos']
        if fx == tx and fy != ty:
            ys = range(min(fy, ty) + 1, max(fy, ty))
            return [(fx, y) for y in ys]
        elif fy == ty and fx != tx:
            xs = range(min(fx, tx) + 1, max(fx, tx))
            return [(x, fy) for x in xs]
        else:
            raise ValueError
     
    def is_legal(self, move):
        if len(self.moves) < 6:
            return super(CheckersVariant2, self).is_legal(move)
        fpos = move['from pos']
        tpos = move['to pos']
        fval = self.piece_map[fpos[0]][fpos[1]]
        tval = self.piece_map[tpos[0]][tpos[1]]
        if fval in self.distance(fpos, tpos) and tval == 0:
            return True
        else:
            return False


class DiagonalVariant(Board):
    def vertical_dist(self, A, B):
        if A[1] != B[1]:
            return [           abs(A[1] - B[1]),
                                   A[1] + B[1],
                    (self.size[1] - A[1] - 1) + (self.size[1] - B[1] - 1)]
        return []
    
    def horizontal_dist(self, A, B):
        if A[0] != B[0]:
            return [           abs(A[0] - B[0]),
                                   A[0] + B[0],
                    (self.size[0] - A[0] - 1) + (self.size[0] - B[0] - 1)]
        return []
    
    def is_legal(self, move):
        fpos = move['from pos']
        tpos = move['to pos']
        fval = self.piece_map[fpos[0]][fpos[1]]
        tval = self.piece_map[tpos[0]][tpos[1]]
        odd1 = fval in self.vertical_dist(fpos, tpos)
        odd2 = fval in self.horizontal_dist(fpos, tpos)
        if len(self.moves) % 4 in [2, 3]:
#            print("odd turn")
            return (odd1 and odd2 and tval > 0)
        else:
#            print("even turn")
            return (fval in self.distance(fpos, tpos) and tval > 0)


class ShrinkingVariant(Board):
    pass













