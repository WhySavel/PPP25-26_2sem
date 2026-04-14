from abc import ABC, abstractmethod

class Position:
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def __eq__(self, other):
        return isinstance(other, Position) and self.row == other.row and self.col == other.col

    def __hash__(self):
        return hash((self.row, self.col))

    def __str__(self):
        return f"{chr(self.col + 97)}{8 - self.row}"

    def __repr__(self):
        return str(self)


class Move:
    def __init__(self, piece, start, end, captured=None):
        self.piece = piece
        self.start = start
        self.end = end
        self.captured = captured
        self.was_moved_before = piece.has_moved


class Piece(ABC):
    def __init__(self, color, position):
        self.color = color
        self.position = position
        self.has_moved = False

    def enemy(self, piece):
        return piece is not None and piece.color != self.color

    def allied(self, piece):
        return piece is not None and piece.color == self.color

    @abstractmethod
    def symbol(self):
        pass

    @abstractmethod
    def get_moves(self, board):
        pass

    def step_moves(self, board, directions, limit=1):
        moves = []
        for dr, dc in directions:
            r, c = self.position.row, self.position.col
            steps = 0
            while True:
                r += dr
                c += dc
                steps += 1
                if not board.inside(r, c):
                    break
                target = board.get(r, c)
                if target is None:
                    moves.append(Position(r, c))
                elif self.enemy(target):
                    moves.append(Position(r, c))
                    break
                else:
                    break
                if limit is not None and steps >= limit:
                    break
        return moves


class Pawn(Piece):
    def symbol(self):
        return 'P' if self.color == 'white' else 'p'

    def get_moves(self, board):
        moves = []
        direction = -1 if self.color == 'white' else 1
        r, c = self.position.row, self.position.col
        one = r + direction
        two = r + 2 * direction
        if board.inside(one, c) and board.empty(one, c):
            moves.append(Position(one, c))
            if not self.has_moved and board.inside(two, c) and board.empty(two, c):
                moves.append(Position(two, c))
        for dc in (-1, 1):
            nr, nc = r + direction, c + dc
            if board.inside(nr, nc):
                target = board.get(nr, nc)
                if self.enemy(target):
                    moves.append(Position(nr, nc))
        return moves


class Rook(Piece):
    def symbol(self):
        return 'R' if self.color == 'white' else 'r'

    def get_moves(self, board):
        return self.step_moves(board, [(1, 0), (-1, 0), (0, 1), (0, -1)], None)


class Bishop(Piece):
    def symbol(self):
        return 'B' if self.color == 'white' else 'b'

    def get_moves(self, board):
        return self.step_moves(board, [(1, 1), (1, -1), (-1, 1), (-1, -1)], None)


class Knight(Piece):
    def symbol(self):
        return 'N' if self.color == 'white' else 'n'

    def get_moves(self, board):
        moves = []
        jumps = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
        for dr, dc in jumps:
            r = self.position.row + dr
            c = self.position.col + dc
            if board.inside(r, c):
                target = board.get(r, c)
                if target is None or self.enemy(target):
                    moves.append(Position(r, c))
        return moves


class Queen(Piece):
    def symbol(self):
        return 'Q' if self.color == 'white' else 'q'

    def get_moves(self, board):
        return Rook.get_moves(self, board) + Bishop.get_moves(self, board)


class King(Piece):
    def symbol(self):
        return 'K' if self.color == 'white' else 'k'

    def get_moves(self, board):
        return self.step_moves(board, [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)], 1)


class Archbishop(Piece):
    def symbol(self):
        return 'A' if self.color == 'white' else 'a'

    def get_moves(self, board):
        return Bishop.get_moves(self, board) + Knight.get_moves(self, board)


class Chancellor(Piece):
    def symbol(self):
        return 'C' if self.color == 'white' else 'c'

    def get_moves(self, board):
        return Rook.get_moves(self, board) + Knight.get_moves(self, board)


class Camel(Piece):
    def symbol(self):
        return 'M' if self.color == 'white' else 'm'

    def get_moves(self, board):
        moves = []
        jumps = [(3, 1), (3, -1), (-3, 1), (-3, -1), (1, 3), (1, -3), (-1, 3), (-1, -3)]
        for dr, dc in jumps:
            r = self.position.row + dr
            c = self.position.col + dc
            if board.inside(r, c):
                target = board.get(r, c)
                if target is None or self.enemy(target):
                    moves.append(Position(r, c))
        return moves


class Wizard(Piece):
    def symbol(self):
        return 'W' if self.color == 'white' else 'w'

    def get_moves(self, board):
        moves = []
        dirs = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
        for dr, dc in dirs:
            r, c = self.position.row, self.position.col
            jumped = False
            while True:
                r += dr
                c += dc
                if not board.inside(r, c):
                    break
                target = board.get(r, c)
                if target is None:
                    moves.append(Position(r, c))
                elif not jumped:
                    jumped = True
                    r += dr
                    c += dc
                    if board.inside(r, c) and (board.empty(r, c) or self.enemy(board.get(r, c))):
                        moves.append(Position(r, c))
                    break
                else:
                    break
        return moves


class CheckersPiece(Piece):
    def symbol(self):
        return 'o' if self.color == 'white' else 'x'

    def get_moves(self, board):
        moves = []
        direction = -1 if self.color == 'white' else 1
        r, c = self.position.row, self.position.col
        for dc in (-1, 1):
            nr, nc = r + direction, c + dc
            jr, jc = r + 2 * direction, c + 2 * dc
            if board.inside(nr, nc) and board.empty(nr, nc):
                moves.append(Position(nr, nc))
            if board.inside(jr, jc):
                middle = board.get(nr, nc) if board.inside(nr, nc) else None
                if middle is not None and self.enemy(middle) and board.empty(jr, jc):
                    moves.append(Position(jr, jc))
        return moves


class CheckersKing(CheckersPiece):
    def symbol(self):
        return 'O' if self.color == 'white' else 'X'

    def get_moves(self, board):
        moves = []
        for dr, dc in [(1,1),(1,-1),(-1,1),(-1,-1)]:
            r = self.position.row + dr
            c = self.position.col + dc
            if board.inside(r, c) and board.empty(r, c):
                moves.append(Position(r, c))
        return moves


class Board:
    def __init__(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]

    def inside(self, r, c):
        return 0 <= r < 8 and 0 <= c < 8

    def get(self, r, c):
        if not self.inside(r, c):
            return None
        return self.grid[r][c]

    def empty(self, r, c):
        return self.inside(r, c) and self.grid[r][c] is None

    def place(self, piece):
        self.grid[piece.position.row][piece.position.col] = piece

    def move(self, move):
        sr, sc = move.start.row, move.start.col
        er, ec = move.end.row, move.end.col
        piece = self.grid[sr][sc]
        move.captured = self.grid[er][ec]
        self.grid[er][ec] = piece
        self.grid[sr][sc] = None
        piece.position = Position(er, ec)
        piece.has_moved = True
        if isinstance(piece, Pawn):
            if piece.color == 'white' and er == 0:
                self.grid[er][ec] = Queen('white', Position(er, ec))
            elif piece.color == 'black' and er == 7:
                self.grid[er][ec] = Queen('black', Position(er, ec))
        if isinstance(piece, CheckersPiece):
            if piece.color == 'white' and er == 0:
                self.grid[er][ec] = CheckersKing('white', Position(er, ec))
            elif piece.color == 'black' and er == 7:
                self.grid[er][ec] = CheckersKing('black', Position(er, ec))

    def undo(self, move):
        sr, sc = move.start.row, move.start.col
        er, ec = move.end.row, move.end.col
        piece = self.grid[er][ec]
        self.grid[sr][sc] = piece
        self.grid[er][ec] = move.captured
        piece.position = Position(sr, sc)
        piece.has_moved = move.was_moved_before

    def setup_chess(self, variant='standard'):
        for i in range(8):
            self.place(Pawn('white', Position(6, i)))
            self.place(Pawn('black', Position(1, i)))
        if variant == 'new':
            back = [Rook, Wizard, Archbishop, Queen, King, Chancellor, Knight, Rook]
        else:
            back = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for i, cls in enumerate(back):
            self.place(cls('white', Position(7, i)))
            self.place(cls('black', Position(0, i)))

    def setup_checkers(self):
        for r in range(3):
            for c in range(8):
                if (r + c) % 2 == 1:
                    self.place(CheckersPiece('black', Position(r, c)))
        for r in range(5, 8):
            for c in range(8):
                if (r + c) % 2 == 1:
                    self.place(CheckersPiece('white', Position(r, c)))

    def print_board(self, threatened=None, check_pos=None):
        threatened = set(threatened or [])
        print()
        for r in range(8):
            print(8 - r, end=' ')
            for c in range(8):
                piece = self.grid[r][c]
                if piece is None:
                    ch = '.'
                else:
                    ch = piece.symbol()
                    if check_pos and (r, c) == check_pos:
                        ch = '!' + ch
                    elif (r, c) in threatened:
                        ch = '!' + ch
                print(ch, end=' ')
            print()
        print('  a b c d e f g h')


class Game:
    def __init__(self):
        self.board = Board()
        mode = input('Choose game (chess/checkers): ').strip().lower()
        if mode == 'checkers':
            self.board.setup_checkers()
            self.mode = 'checkers'
        else:
            variant = input('Choose chess variant (standard/new): ').strip().lower()
            if variant not in ('standard', 'new'):
                variant = 'standard'
            self.board.setup_chess(variant)
            self.mode = 'chess'
        self.turn = 'white'
        self.history = []

    def help(self):
        print()
        print('Commands:')
        print('e2 e4 - move')
        print('show e2 - show moves')
        print('undo - undo move')
        print('help - show help')
        print('info - show figure info')
        print('exit - quit')

    def parse(self, s):
        s = s.strip().lower()
        return Position(8 - int(s[1]), ord(s[0]) - 97)

    def show_moves(self, piece):
        moves = piece.get_moves(self.board)
        print('Moves:')
        for m in moves:
            print(m, end=' ')
        print()

    def threatened_pieces(self, color):
        threatened = []
        for r in range(8):
            for c in range(8):
                piece = self.board.get(r, c)
                if piece and piece.color == color:
                    for rr in range(8):
                        for cc in range(8):
                            enemy = self.board.get(rr, cc)
                            if enemy and enemy.color != color:
                                for m in enemy.get_moves(self.board):
                                    if (m.row, m.col) == (r, c):
                                        threatened.append((r, c))
                                        break
        return threatened

    def in_check_position(self, color):
        king_pos = None
        for r in range(8):
            for c in range(8):
                piece = self.board.get(r, c)
                if piece and isinstance(piece, King) and piece.color == color:
                    king_pos = (r, c)
                    break
            if king_pos:
                break
        if king_pos is None:
            return None
        for r in range(8):
            for c in range(8):
                enemy = self.board.get(r, c)
                if enemy and enemy.color != color:
                    for m in enemy.get_moves(self.board):
                        if (m.row, m.col) == king_pos:
                            return king_pos
        return None

    def info(self):
        print()
        print('Chess Figures:')
        print('Pawn (P/p) - forward 1, 2 on first move, captures diagonally, promotion on last rank')
        print('Rook (R/r) - any distance horizontal/vertical')
        print('Knight (N/n) - L-shape jumps')
        print('Bishop (B/b) - any distance diagonal')
        print('Queen (Q/q) - any distance horizontal, vertical, diagonal')
        print('King (K/k) - 1 cell any direction')
        print('Archbishop (A/a) - Bishop + Knight moves')
        print('Chancellor (C/c) - Rook + Knight moves')
        print('Camel (M/m) - jumps 3+1')
        print('Wizard (W/w) - like Queen, can jump over 1 piece once')
        print()
        print('Checkers:')
        print('Checker (o/x) - forward diagonal 1, captures by jumping')
        print('King (O/X) - diagonal 1 any direction')

    def play(self):
        self.help()
        while True:
            threat = self.threatened_pieces(self.turn)
            check_pos = self.in_check_position(self.turn)
            self.board.print_board(threatened=threat, check_pos=check_pos)
            if check_pos:
                print('CHECK!')
            print(self.turn, 'move')
            cmd = input('> ').strip()
            if cmd == 'help':
                self.help()
                continue
            if cmd == 'info':
                self.info()
                continue
            if cmd == 'exit':
                break
            if cmd == 'undo':
                if self.history:
                    move = self.history.pop()
                    self.board.undo(move)
                    self.turn = 'white' if self.turn == 'black' else 'black'
                continue
            if cmd.startswith('show '):
                try:
                    pos = self.parse(cmd.split()[1])
                    piece = self.board.get(pos.row, pos.col)
                    if piece:
                        self.show_moves(piece)
                except:
                    print('invalid input')
                continue
            try:
                a, b = cmd.split()
                start = self.parse(a)
                end = self.parse(b)
            except:
                print('invalid input')
                continue
            piece = self.board.get(start.row, start.col)
            if not piece or piece.color != self.turn:
                print('wrong piece')
                continue
            valid_moves = piece.get_moves(self.board)
            if end not in valid_moves:
                print('illegal move')
                continue
            mv = Move(piece, start, end)
            self.board.move(mv)
            self.history.append(mv)
            self.turn = 'white' if self.turn == 'black' else 'black'


if __name__ == '__main__':
    game = Game()
    game.play()
