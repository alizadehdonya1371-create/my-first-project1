def show_info_page():
    running = True
    while running:
        menu_screen.blit(background, (0, 0))
        title = menu_font.render("Info", True, (255, 223, 0))
        menu_screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

        info_text = menu_small_font.render("Chess is a strategic two-player game played on an 8x8 board.", True, WHITE)
        menu_screen.blit(info_text, (SCREEN_WIDTH // 2 - info_text.get_width() // 2, 200))

        back_button = pygame.Rect((SCREEN_WIDTH - 200) // 2, 300, 200, 50)
        draw_button(back_button, "Back", chess_icon)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    click_sound.play()
                    running = False

def show_difficulty_menu():
    button_labels = ['Easy', 'Medium', 'Hard', 'Back']
    buttons = {}
    button_height = 60
    spacing = 20
    total_height = len(button_labels) * (button_height + spacing) - spacing
    start_y = (SCREEN_HEIGHT - total_height) // 2

    for i, label in enumerate(button_labels):
        x = (SCREEN_WIDTH - 300) // 2
        y = start_y + i * (button_height + spacing)
        buttons[label] = pygame.Rect(x, y, 300, button_height)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for label, rect in buttons.items():
                    if rect.collidepoint(event.pos):
                        click_sound.play()
                        if label == "Back":
                            return None
                        return label

        menu_screen.blit(background, (0, 0))
        title = menu_font.render("Select Difficulty", True, (255, 223, 0))
        menu_screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))

        for label, rect in buttons.items():
            draw_button(rect, label, chess_icon)

        pygame.display.update()

def show_menu_and_get_difficulty():
    button_labels = ['Start', 'Info', 'Exit']
    buttons = {}
    button_height = 60
    spacing = 20
    total_height = len(button_labels) * (button_height + spacing) - spacing
    start_y = (SCREEN_HEIGHT - total_height) // 2

    for i, label in enumerate(button_labels):
        x = (SCREEN_WIDTH - 300) // 2
        y = start_y + i * (button_height + spacing)
        buttons[label] = pygame.Rect(x, y, 300, button_height)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for label, rect in buttons.items():
                    if rect.collidepoint(event.pos):
                        click_sound.play()
                        if label == "Exit":
                            pygame.quit(); sys.exit()
                        elif label == "Info":
                            show_info_page()
                        elif label == "Start":
                            result = show_difficulty_menu()
                            if result:
                                return result

        menu_screen.blit(background, (0, 0))
        title = menu_font.render("Chess Game", True, (255, 223, 0))
        menu_screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))

        for label, rect in buttons.items():
            draw_button(rect, label, chess_icon)

        pygame.display.update()

import threading
import pygame
import sys
import random

# Initialize Pygame and window constants
pygame.init()
WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
DARK_BROWN, LIGHT_BROWN = (181, 136, 99), (240, 217, 181)
BLUE, GRAY, YELLOW = (0, 0, 255), (50, 50, 50), (255, 215, 0)


ai_move_ready = False
ai_move_result = None
thinking = False
# ------------------ AI LOGIC (from ChessAI) ------------------
set_depth = 4
checkmate_points = 1000
stalemate_points = 0

piece_scores = {
    'K': 200.0, 'Q': 9.0, 'R': 5.0, 'B': 3.3, 'N': 3.2, 'P': 1.0
}
piece_positions = {
    'wP': [
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0],
        [1.0, 1.0, 2.0, 3.0, 3.0, 2.0, 1.0, 1.0],
        [0.5, 0.5, 1.0, 2.5, 2.5, 1.0, 0.5, 0.5],
        [0.0, 0.0, 0.0, 2.0, 2.0, 0.0, 0.0, 0.0],
        [0.5, -0.5, -1.0, 0.0, 0.0, -1.0, -0.5, 0.5],
        [0.5, 1.0, 1.0, -2.0, -2.0, 1.0, 1.0, 0.5],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    ],
    'bP': [
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.5, 1.0, 1.0, -2.0, -2.0, 1.0, 1.0, 0.5],
        [0.5, -0.5, -1.0, 0.0, 0.0, -1.0, -0.5, 0.5],
        [0.0, 0.0, 0.0, 2.0, 2.0, 0.0, 0.0, 0.0],
        [0.5, 0.5, 1.0, 2.5, 2.5, 1.0, 0.5, 0.5],
        [1.0, 1.0, 2.0, 3.0, 3.0, 2.0, 1.0, 1.0],
        [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    ],
    'wN': [
        [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0],
        [-4.0, -2.0, 0.0, 0.0, 0.0, 0.0, -2.0, -4.0],
        [-3.0, 0.0, 1.0, 1.5, 1.5, 1.0, 0.0, -3.0],
        [-3.0, 0.5, 1.5, 2.0, 2.0, 1.5, 0.5, -3.0],
        [-3.0, 0.0, 1.5, 2.0, 2.0, 1.5, 0.0, -3.0],
        [-3.0, 0.5, 1.0, 1.5, 1.5, 1.0, 0.5, -3.0],
        [-4.0, -2.0, 0.0, 0.5, 0.5, 0.0, -2.0, -4.0],
        [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0]
    ],
    'bN': [
        [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0],
        [-4.0, -2.0, 0.0, 0.5, 0.5, 0.0, -2.0, -4.0],
        [-3.0, 0.5, 1.0, 1.5, 1.5, 1.0, 0.5, -3.0],
        [-3.0, 0.0, 1.5, 2.0, 2.0, 1.5, 0.0, -3.0],
        [-3.0, 0.5, 1.5, 2.0, 2.0, 1.5, 0.5, -3.0],
        [-3.0, 0.0, 1.0, 1.5, 1.5, 1.0, 0.0, -3.0],
        [-4.0, -2.0, 0.0, 0.0, 0.0, 0.0, -2.0, -4.0],
        [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0]
    ],
    'wB': [
        [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0],
        [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0],
        [-1.0, 0.0, 0.5, 1.0, 1.0, 0.5, 0.0, -1.0],
        [-1.0, 0.5, 0.5, 1.0, 1.0, 0.5, 0.5, -1.0],
        [-1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, -1.0],
        [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0],
        [-1.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.5, -1.0],
        [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0]
    ],
    'bB': [
        [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0],
        [-1.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.5, -1.0],
        [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0],
        [-1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, -1.0],
        [-1.0, 0.5, 0.5, 1.0, 1.0, 0.5, 0.5, -1.0],
        [-1.0, 0.0, 0.5, 1.0, 1.0, 0.5, 0.0, -1.0],
        [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0],
        [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0]
    ],
    'wR': [
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5],
        [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
        [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
        [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
        [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
        [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
        [0.0, 0.0, 0.0, 0.5, 0.5, 0.0, 0.0, 0.0]
    ],
    'bR': [
        [0.0, 0.0, 0.0, 0.5, 0.5, 0.0, 0.0, 0.0],
        [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
        [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
        [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
        [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
        [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
        [0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    ],
    'wQ': [
        [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0],
        [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0],
        [-1.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -1.0],
        [-0.5, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -0.5],
        [0.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -0.5],
        [-1.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -1.0],
        [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0],
        [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0]
    ],
    'bQ': [
        [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0],
        [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0],
        [-1.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -1.0],
        [-0.5, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -0.5],
        [0.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -0.5],
        [-1.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -1.0],
        [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0],
        [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0]
    ],
    'wK': [
        [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
        [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
        [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
        [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
        [-2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0],
        [-1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0],
        [2.0, 2.0, 0.0, 0.0, 0.0, 0.0, 2.0, 2.0],
        [2.0, 3.0, 1.0, 0.0, 0.0, 1.0, 3.0, 2.0]
    ],
    'bK': [
        [2.0, 3.0, 1.0, 0.0, 0.0, 1.0, 3.0, 2.0],
        [2.0, 2.0, 0.0, 0.0, 0.0, 0.0, 2.0, 2.0],
        [-1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0],
        [-2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0],
        [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
        [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
        [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
        [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0]
    ]
}

def score_board(game_state):
    """Positive if good for white, negative if good for black."""
    if game_state.checkmate:
        return -checkmate_points if game_state.white_to_move else checkmate_points
    if game_state.stalemate:
        return stalemate_points
    score = 0
    for r in range(8):
        for c in range(8):
            piece = game_state.board[r][c]
            if piece == '--': continue
            val = piece_scores[piece[1]]
            pst = piece_positions[piece]
            score += (val + pst[r][c]) if piece[0] == 'w' else -(val + pst[r][c])
    return score


def find_negamax_move_alphabeta(game_state, valid_moves, depth, alpha, beta, turn_multiplier):
    global next_move
    if depth == 0:
        return turn_multiplier * score_board(game_state)
    max_score = -checkmate_points
    for move in valid_moves:
        game_state.make_move(move)
        next_moves = game_state.get_valid_moves()
        score = -find_negamax_move_alphabeta(game_state, next_moves, depth-1, -beta, -alpha, -turn_multiplier)
        game_state.undo_move()
        if score > max_score:
            max_score = score
            if depth == set_depth:
                next_move = move
        alpha = max(alpha, max_score)
        if alpha >= beta:
            break
    return max_score


def find_best_move(game_state, valid_moves):
    global next_move
    next_move = None
    random.shuffle(valid_moves)
    find_negamax_move_alphabeta(game_state, valid_moves, set_depth, -checkmate_points, checkmate_points,
                                1 if game_state.white_to_move else -1)
    return next_move

# Adapter to wrap board and move methods for AI
class GameStateAdapter:
    def __init__(self, board, white_to_move):
        self.board = [row[:] for row in board]
        self.white_to_move = white_to_move
        self.checkmate = False
        self.stalemate = False
        self._move_stack = []
    def make_move(self, move):
        (r1, c1), (r2, c2) = move
        self._move_stack.append((r1, c1, r2, c2, self.board[r2][c2]))
        self.board[r2][c2] = self.board[r1][c1]
        self.board[r1][c1] = '--'
        self.white_to_move = not self.white_to_move
    def undo_move(self):
        r1, c1, r2, c2, captured = self._move_stack.pop()
        self.board[r1][c1] = self.board[r2][c2]
        self.board[r2][c2] = captured
        self.white_to_move = not self.white_to_move
    def get_valid_moves(self):
        return get_all_legal_moves(self.board, 'w' if self.white_to_move else 'b')


def ai_move(board, color):
    gs = GameStateAdapter(board, color=='w')
    valid_moves = gs.get_valid_moves()
    return find_best_move(gs, valid_moves) if valid_moves else None

# ------------------ Game Logic & UI ------------------
def promote_pawn(win, color):
    font = pygame.font.SysFont('comicsans', 30)
    options = ['Q', 'R', 'B', 'N']
    selected = 0
    clock = pygame.time.Clock()
    while True:
        win.fill(GRAY)
        prompt = font.render(f"Promote {color} Pawn to:", True, WHITE)
        win.blit(prompt, (WIDTH//2 - prompt.get_width()//2, 100))
        for i, opt in enumerate(options):
            clr = YELLOW if i == selected else WHITE
            lbl = font.render(opt, True, clr)
            win.blit(lbl, (WIDTH//2 - lbl.get_width()//2, 150 + i*40))
        
        
        # Draw Back Button styled like menu
        back_btn_rect = pygame.Rect(WIDTH - 120, 10, 100, 40)
        back_color = (34, 139, 34)
        if back_btn_rect.collidepoint(pygame.mouse.get_pos()):
            back_color = (100, 100, 100)
        pygame.draw.rect(win, back_color, back_btn_rect, border_radius=15)
        win.blit(chess_icon, (back_btn_rect.x + 10, back_btn_rect.y + 5))
        back_text = pygame.font.SysFont("Poppins", 20).render("Back", True, WHITE)
        win.blit(back_text, (back_btn_rect.x + 40, back_btn_rect.y + 10))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                if event.key == pygame.K_RETURN:
                    return color + options[selected]
        clock.tick(30)

def draw_board(win):
    for r in range(8):
        for c in range(8):
            clr = LIGHT_BROWN if (r+c)%2==0 else DARK_BROWN
            pygame.draw.rect(win, clr, (c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces(win, board, images, selected=None):
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece!='--':
                if selected==(r,c):
                    pygame.draw.rect(win, BLUE, (c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                win.blit(images[piece], (c*SQUARE_SIZE, r*SQUARE_SIZE))

def get_square_clicked(pos):
    x,y=pos; return y//SQUARE_SIZE, x//SQUARE_SIZE

def is_path_clear(board, start, end):
    sr,sc=start; er,ec=end
    dr = (er-sr)//max(1,abs(er-sr)) if er!=sr else 0
    dc = (ec-sc)//max(1,abs(ec-sc)) if ec!=sc else 0
    r,c=sr+dr,sc+dc
    while (r,c)!=(er,ec):
        if board[r][c] != '--': return False
        r+=dr; c+=dc
    return True

def is_move_legal(piece, start, end, board):
    sr,sc=start; er,ec=end
    target = board[er][ec]
    if piece=='--' or (target!='--' and target[0]==piece[0]): return False
    dr,dc=er-sr,ec-sc; abs_dr,abs_dc=abs(dr),abs(dc)
    kind=piece[1]; direction = -1 if piece[0]=='w' else 1
    if kind=='P':
        if dc==0 and ((dr==direction and target=='--') or (dr==2*direction and sr==(6 if piece[0]=='w' else 1) and board[sr+direction][sc]=='--' and target=='--')): return True
        if abs_dc==1 and dr==direction and target!='--' and target[0]!=piece[0]: return True
    elif kind=='R' and (sr==er or sc==ec): return is_path_clear(board,start,end)
    elif kind=='N' and (abs_dr,abs_dc) in [(2,1),(1,2)]: return True
    elif kind=='B' and abs_dr==abs_dc: return is_path_clear(board,start,end)
    elif kind=='Q' and (sr==er or sc==ec or abs_dr==abs_dc): return is_path_clear(board,start,end)
    elif kind=='K' and max(abs_dr,abs_dc)==1: return True
    return False

def find_king(board, color):
    for r in range(8):
        for c in range(8):
            if board[r][c]==color+'K': return (r,c)
    return None

def is_in_check(board, color):
    kp = find_king(board, color)
    if not kp: return False
    for r in range(8):
        for c in range(8):
            p=board[r][c]
            if p!='--' and p[0]!=color and is_move_legal(p,(r,c),kp,board): return True
    return False

def get_all_legal_moves(board, color):
    moves=[]
    for r in range(8):
        for c in range(8):
            p=board[r][c]
            if p!='--' and p[0]==color:
                for er in range(8):
                    for ec in range(8):
                        if is_move_legal(p,(r,c),(er,ec),board):
                            cap=board[er][ec]; board[er][ec]=p; board[r][c]='--'
                            if not is_in_check(board, color): moves.append(((r,c),(er,ec)))
                            board[r][c]=p; board[er][ec]=cap
    return moves

def is_checkmate(board, color):
    return is_in_check(board, color) and len(get_all_legal_moves(board,color))==0

def load_images():
    pieces = ['bR','bN','bB','bQ','bK','bP','wR','wN','wB','wQ','wK','wP']
    imgs={}
    for p in pieces:
        path=fr"C:/Users/Donya/Desktop/شطرنچ/chess_assets/{p}.png"
        imgs[p]=pygame.transform.scale(pygame.image.load(path),(SQUARE_SIZE,SQUARE_SIZE))
    return imgs

def load_logo():
    path="C:/Users/Donya/Desktop/شطرنچ/images.png"
    logo=pygame.image.load(path)
    return pygame.transform.scale(logo,(200,200))


def show_game_over(win, msg, logo):
    font = pygame.font.SysFont('comicsans', 50)
    small = pygame.font.SysFont('comicsans', 30)
    ov = pygame.Surface((WIDTH, HEIGHT)); ov.set_alpha(200); ov.fill(BLACK)
    win.blit(ov, (0, 0))
    text = font.render(msg, True, WHITE)
    rt = small.render("Press R to Restart or Q to Quit", True, WHITE)
    win.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 50))
    win.blit(rt, (WIDTH // 2 - rt.get_width() // 2, HEIGHT // 2 + 10))
    pygame.display.update()

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    return 'restart'
                elif e.key == pygame.K_q:
                    pygame.quit(); sys.exit()
        pygame.time.Clock().tick(30)
    
def threaded_ai(board_copy):
    global ai_move_result, ai_move_ready
    gs = GameStateAdapter(board_copy, False)
    valid_moves = gs.get_valid_moves()
    ai_move_result = find_best_move(gs, valid_moves)
    ai_move_ready = True

# ------------- Custom Menu Logic (Injected from منو.py) -------------
# MENU AND GAME LAUNCHER SETUP
SCREEN_WIDTH = WIDTH
SCREEN_HEIGHT = HEIGHT
menu_screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game Menu")

background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
for y in range(SCREEN_HEIGHT):
    color = (50 + int(50 * y / SCREEN_HEIGHT), 50 + int(50 * y / SCREEN_HEIGHT), 50 + int(50 * y / SCREEN_HEIGHT))
    pygame.draw.line(background, color, (0, y), (SCREEN_WIDTH, y))

chess_icon = pygame.image.load('C:/Users/Donya/Desktop/شطرنچ/chess_assets/wN.png')
chess_icon = pygame.transform.scale(chess_icon, (30, 30))

menu_font = pygame.font.SysFont("Poppins", 40)
menu_small_font = pygame.font.SysFont("Poppins", 24)
click_sound = pygame.mixer.Sound("C:/Users/Donya/Desktop/شطرنچ/Mouse Click - Sound Effect [fara-download.ir].mp3")

def draw_button(button, text, icon):
    mouse_pos = pygame.mouse.get_pos()
    color = (34, 139, 34)
    if button.collidepoint(mouse_pos):
        color = (100, 100, 100)
        pygame.draw.rect(menu_screen, color, button.inflate(10, 10), border_radius=15)
    else:
        pygame.draw.rect(menu_screen, color, button, border_radius=15)
    menu_screen.blit(icon, (button.x + 10, button.y + (button.height - icon.get_height()) // 2))
    text_surface = menu_small_font.render(text, True, WHITE)
    menu_screen.blit(text_surface, (button.x + icon.get_width() + 20, button.y + (button.height - text_surface.get_height()) // 2))
def main():
    global ai_move_ready,ai_move_result,thinking
    win=pygame.display.set_mode((WIDTH,HEIGHT))
    pygame.display.set_caption('Chess with AI')
    images=load_images()
    logo=load_logo()
    difficulty=show_menu_and_get_difficulty()

    if difficulty == "Easy":
        global set_depth
        set_depth = 2
    elif difficulty == "Medium":
        set_depth = 3
    elif difficulty == "Hard":
        set_depth = 5
    board=[
        ['bR','bN','bB','bQ','bK','bB','bN','bR'],
        ['bP']*8,
        ['--']*8,
        ['--']*8,
        ['--']*8,
        ['--']*8,
        ['wP']*8,
        ['wR','wN','wB','wQ','wK','wB','wN','wR']
    ]
    sel_sq=None; turn='w'; game_over=False; clock=pygame.time.Clock()
    pygame.mixer.init(); pygame.mixer.music.load("C:/Users/Donya/Desktop/شطرنچ/bikalam.mp3"); pygame.mixer.music.play(-1)
    while True:
        win.fill(BLACK); draw_board(win); draw_pieces(win,board,images,sel_sq);
        # Draw Back Button styled like menu
        back_btn_rect = pygame.Rect(WIDTH - 120, 10, 100, 40)
        back_color = (34, 139, 34)
        if back_btn_rect.collidepoint(pygame.mouse.get_pos()):
            back_color = (100, 100, 100)
        pygame.draw.rect(win, back_color, back_btn_rect, border_radius=15)
        win.blit(chess_icon, (back_btn_rect.x + 10, back_btn_rect.y + 5))
        back_text = pygame.font.SysFont("Poppins", 20).render("Back", True, WHITE)
        win.blit(back_text, (back_btn_rect.x + 40, back_btn_rect.y + 10))
        pygame.display.update()
        if is_checkmate(board,turn):
            winner='White' if turn=='b' else 'Black'
            result = show_game_over(win,f'{winner} wins by Checkmate!',logo)
            if result == 'restart': main()
            else: sys.exit()
            game_over=True
        if game_over:
            for e in pygame.event.get():
                if e.type==pygame.QUIT: pygame.quit();sys.exit()
                if e.type==pygame.KEYDOWN:
                    if e.key==pygame.K_r: main()
                    if e.key==pygame.K_q: pygame.quit();sys.exit()
            continue
        if turn == 'b':
            if not thinking and not ai_move_ready:
                board_copy = [row[:] for row in board]
                threading.Thread(target=lambda: threaded_ai(board_copy), daemon=True).start()
                thinking = True
            elif ai_move_ready:
                move = ai_move_result
                ai_move_ready = False
                thinking = False
                if move:
                    (r1,c1),(r2,c2)=move
                    board[r2][c2]=board[r1][c1]; board[r1][c1]='--'; turn='w'
                    if board[r2][c2][1]=='P' and r2==7: board[r2][c2]=promote_pawn(win,'b')
                continue
            else:
                font = pygame.font.SysFont('comicsans', 30)
                thinking_text = font.render("AI Thinking...", True, YELLOW)
                win.blit(thinking_text, (WIDTH//2 - thinking_text.get_width()//2, HEIGHT//2))
                pygame.display.update()
            continue
            if move:
                (r1,c1),(r2,c2)=move
                board[r2][c2]=board[r1][c1]; board[r1][c1]='--'; turn='w'
                if board[r2][c2][1]=='P' and r2==7: board[r2][c2]=promote_pawn(win,'b')
            continue
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit();sys.exit()
            if e.type==pygame.MOUSEBUTTONDOWN:
                if pygame.Rect(WIDTH - 120, 10, 100, 40).collidepoint(pygame.mouse.get_pos()):
                    click_sound.play()
                    return main()
                r,c=get_square_clicked(pygame.mouse.get_pos())
                if sel_sq:
                    sr,sc=sel_sq; piece=board[sr][sc]
                    if piece[0]=='w' and is_move_legal(piece,(sr,sc),(r,c),board):
                        cap=board[r][c]; board[r][c]=piece; board[sr][sc]='--'
                        if not is_in_check(board,'w'):
                            turn='b';
                            if piece[1]=='P' and r==0: board[r][c]=promote_pawn(win,'w')
                        else:
                            board[sr][sc]=piece; board[r][c]=cap
                        sel_sq=None
                    elif board[r][c]!='--' and board[r][c][0]=='w':
                        click_sound.play()
                        sel_sq=(r,c)
                    else: sel_sq=None
                else:
                    if board[r][c]!='--' and board[r][c][0]=='w':
                        click_sound.play()
                        click_sound.play()
                        sel_sq=(r,c)
        clock.tick(60)


if __name__=='__main__':
    main()