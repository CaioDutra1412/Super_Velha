"""
Jogo da Velha Móvel 5x5 com Janela 3x3 - Interface Gráfica (Tkinter)

Como usar:
- Rode: python jogo_da_velha_gui.py
- Clique nas células para colocar X/O.
- Use os botões de seta ou as teclas de seta para mover a janela (consome a vez).
- Se um jogador mover a janela, o próximo jogador deve obrigatoriamente colocar uma peça.
- Vitória é verificada apenas dentro da janela 3x3.

Requisitos: Python 3.x (Tkinter já vem com a maioria das distribuições)

"""

import tkinter as tk
from tkinter import messagebox
from typing import List, Tuple

BOARD_SIZE = 5
WINDOW_SIZE = 3
EMPTY = ''
PLAYERS = ['X', 'O']

# Visual constants
CELL_SIZE = 90
PADDING = 20
FONT = ("Helvetica", 28, "bold")
SMALL_FONT = ("Helvetica", 12)
BG = "#0f1724"  # deep navy
CELL_BG = "#0b1220"
CELL_BORDER = "#1f2a44"
WINDOW_COLOR = "#ffd166"  # warm yellow
X_COLOR = "#ff6b6b"  # coral red
O_COLOR = "#4ecdc4"  # teal
HIGHLIGHT = "#ffe8b2"

class JogoVelhaMovel:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Jogo da Velha Móvel 5x5")
        root.configure(bg=BG)

        self.board: List[List[str]] = [[EMPTY]*BOARD_SIZE for _ in range(BOARD_SIZE)]
        # window top-left (row, col)
        self.win_topleft = (1,1)
        self.current = 0
        self.last_action_was_move = False
        self.cell_ids = [[None]*BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.text_ids = [[None]*BOARD_SIZE for _ in range(BOARD_SIZE)]

        self.setup_ui()
        self.draw_board()
        self.update_status()

        # keyboard bindings for arrows
        root.bind('<Left>', lambda e: self.attempt_move('l'))
        root.bind('<Right>', lambda e: self.attempt_move('r'))
        root.bind('<Up>', lambda e: self.attempt_move('u'))
        root.bind('<Down>', lambda e: self.attempt_move('d'))

    def setup_ui(self):
        top_frame = tk.Frame(self.root, bg=BG)
        top_frame.pack(side=tk.TOP, pady=(12,0))

        title = tk.Label(top_frame, text="Jogo da Velha Móvel", font=("Helvetica",18,"bold"), fg=WINDOW_COLOR, bg=BG)
        title.pack()

        self.status_label = tk.Label(self.root, text="", font=SMALL_FONT, fg="#e6eef8", bg=BG)
        self.status_label.pack(pady=(6,6))

        main_frame = tk.Frame(self.root, bg=BG)
        main_frame.pack(padx=12, pady=12)

        canvas_w = BOARD_SIZE * CELL_SIZE + 2*PADDING
        canvas_h = BOARD_SIZE * CELL_SIZE + 2*PADDING
        self.canvas = tk.Canvas(main_frame, width=canvas_w, height=canvas_h, bg=BG, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, padx=(0,12))
        self.canvas.bind('<Button-1>', self.on_canvas_click)

        ctrl_frame = tk.Frame(main_frame, bg=BG)
        ctrl_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Movement buttons
        mv_label = tk.Label(ctrl_frame, text="Mover janela", fg="white", bg=BG, font=SMALL_FONT)
        mv_label.pack(pady=(6,4))

        btn_up = tk.Button(ctrl_frame, text="↑", command=lambda: self.attempt_move('u'), width=4, height=1)
        btn_up.pack()
        row = tk.Frame(ctrl_frame, bg=BG)
        row.pack(pady=6)
        btn_left = tk.Button(row, text="←", command=lambda: self.attempt_move('l'), width=4, height=1)
        btn_left.pack(side=tk.LEFT, padx=4)
        btn_right = tk.Button(row, text="→", command=lambda: self.attempt_move('r'), width=4, height=1)
        btn_right.pack(side=tk.LEFT, padx=4)
        btn_down = tk.Button(ctrl_frame, text="↓", command=lambda: self.attempt_move('d'), width=4, height=1)
        btn_down.pack()

        # Controls
        tk.Label(ctrl_frame, text="", bg=BG).pack(pady=6)
        restart_btn = tk.Button(ctrl_frame, text="Reiniciar", command=self.reiniciar)
        restart_btn.pack(fill=tk.X, pady=4)

        hint = tk.Label(ctrl_frame, text="Clique numa célula para jogar\nTeclas: setas para mover janela", font=("Helvetica",9), fg="#cfe8ff", bg=BG)
        hint.pack(pady=(10,0))

    def draw_board(self):
        self.canvas.delete('all')
        start_x = PADDING
        start_y = PADDING
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x1 = start_x + c*CELL_SIZE
                y1 = start_y + r*CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill=CELL_BG, outline=CELL_BORDER, width=2, tags=(f'cell_{r}_{c}',))
                self.cell_ids[r][c] = rect
                # draw piece if any
                if self.board[r][c] != EMPTY:
                    text_id = self.canvas.create_text((x1+x2)//2, (y1+y2)//2, text=self.board[r][c], font=FONT,
                                                      fill=X_COLOR if self.board[r][c]=='X' else O_COLOR)
                    self.text_ids[r][c] = text_id
        self.draw_window_highlight()

    def draw_window_highlight(self):
        # draw semi-transparent rectangle around window cells
        wx, wy = self.win_topleft
        start_x = PADDING + wy*CELL_SIZE
        start_y = PADDING + wx*CELL_SIZE
        end_x = start_x + WINDOW_SIZE*CELL_SIZE
        end_y = start_y + WINDOW_SIZE*CELL_SIZE
        # highlight background (subtle)
        self.canvas.create_rectangle(start_x, start_y, end_x, end_y, outline=WINDOW_COLOR, width=4, tags='window')
        # also slightly lighten each cell in window
        for r in range(wx, wx+WINDOW_SIZE):
            for c in range(wy, wy+WINDOW_SIZE):
                rect_id = self.cell_ids[r][c]
                # overlay a light rectangle with low alpha - tkinter doesn't support alpha well, use color fill
                self.canvas.itemconfig(rect_id, fill="#0f2a24")

    def on_canvas_click(self, event):
        # map event coords to cell
        x = event.x - PADDING
        y = event.y - PADDING
        if x < 0 or y < 0:
            return
        c = x // CELL_SIZE
        r = y // CELL_SIZE
        if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
            return
        self.attempt_place(r, c)

    def attempt_place(self, r: int, c: int):
        if self.board[r][c] != EMPTY:
            messagebox.showinfo("Espaço ocupado", "Essa célula já está ocupada.")
            return
        # place piece
        player = PLAYERS[self.current]
        self.board[r][c] = player
        # draw piece
        x1 = PADDING + c*CELL_SIZE
        y1 = PADDING + r*CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        text_id = self.canvas.create_text((x1+x2)//2, (y1+y2)//2, text=player, font=FONT,
                                          fill=X_COLOR if player=='X' else O_COLOR)
        self.text_ids[r][c] = text_id

        # check win
        if self.check_win_in_window(player):
            self.draw_window_highlight()
            messagebox.showinfo("Vitória!", f"Jogador {player} venceu!")
            self.highlight_winning_line(player)
            return

        # check full
        if all(self.board[i][j] != EMPTY for i in range(BOARD_SIZE) for j in range(BOARD_SIZE)):
            messagebox.showinfo("Empate", "Tabuleiro cheio: Empate!")
            return

        # placing resets last_action_was_move
        self.last_action_was_move = False
        self.current = 1 - self.current
        self.update_status()

    def attempt_move(self, direction: str):
        if self.last_action_was_move:
            # cannot move again
            messagebox.showinfo('Movimento não permitido', 'O jogador anterior moveu a janela — você deve colocar uma peça.')
            return
        possible, new_top = self.can_move_window(self.win_topleft, direction)
        if not possible:
            # invalid
            self.pulse_border(self.win_topleft)
            return
        self.win_topleft = new_top
        # redraw board appearance
        self.draw_board()
        # moving consumes the turn
        self.last_action_was_move = True
        self.current = 1 - self.current
        self.update_status()

    def pulse_border(self, top_left):
        # small animation to signal invalid move
        wx, wy = top_left
        for _ in range(2):
            self.canvas.after(0, lambda: self.canvas.create_rectangle(0,0,0,0))
        # a simpler feedback: flash status
        old = self.status_label.cget('fg')
        def flash(step=0):
            if step%2==0:
                self.status_label.config(fg='#ffb4b4')
            else:
                self.status_label.config(fg='#e6eef8')
            if step<3:
                self.root.after(120, lambda: flash(step+1))
        flash()

    def can_move_window(self, win_topleft: Tuple[int,int], direction: str) -> Tuple[bool, Tuple[int,int]]:
        wx, wy = win_topleft
        if direction == 'u':
            nx, ny = wx-1, wy
        elif direction == 'd':
            nx, ny = wx+1, wy
        elif direction == 'l':
            nx, ny = wx, wy-1
        elif direction == 'r':
            nx, ny = wx, wy+1
        else:
            return False, win_topleft
        if 0 <= nx <= BOARD_SIZE - WINDOW_SIZE and 0 <= ny <= BOARD_SIZE - WINDOW_SIZE:
            return True, (nx, ny)
        return False, win_topleft

    def check_win_in_window(self, player: str) -> bool:
        wx, wy = self.win_topleft
        # rows
        for r in range(wx, wx+WINDOW_SIZE):
            if all(self.board[r][c] == player for c in range(wy, wy+WINDOW_SIZE)):
                return True
        # cols
        for c in range(wy, wy+WINDOW_SIZE):
            if all(self.board[r][c] == player for r in range(wx, wx+WINDOW_SIZE)):
                return True
        # diagonals
        if all(self.board[wx+i][wy+i] == player for i in range(WINDOW_SIZE)):
            return True
        if all(self.board[wx+i][wy+(WINDOW_SIZE-1-i)] == player for i in range(WINDOW_SIZE)):
            return True
        return False

    def highlight_winning_line(self, player: str):
        # highlight the winning line inside the window (if any)
        wx, wy = self.win_topleft
        # check rows
        for r in range(wx, wx+WINDOW_SIZE):
            if all(self.board[r][c] == player for c in range(wy, wy+WINDOW_SIZE)):
                for c in range(wy, wy+WINDOW_SIZE):
                    self.flash_cell(r, c)
                return
        for c in range(wy, wy+WINDOW_SIZE):
            if all(self.board[r][c] == player for r in range(wx, wx+WINDOW_SIZE)):
                for r in range(wx, wx+WINDOW_SIZE):
                    self.flash_cell(r, c)
                return
        if all(self.board[wx+i][wy+i] == player for i in range(WINDOW_SIZE)):
            for i in range(WINDOW_SIZE):
                self.flash_cell(wx+i, wy+i)
            return
        if all(self.board[wx+i][wy+(WINDOW_SIZE-1-i)] == player for i in range(WINDOW_SIZE)):
            for i in range(WINDOW_SIZE):
                self.flash_cell(wx+i, wy+(WINDOW_SIZE-1-i))
            return

    def flash_cell(self, r: int, c: int):
        rect = self.cell_ids[r][c]
        def step(i=0):
            if i%2==0:
                self.canvas.itemconfig(rect, fill=HIGHLIGHT)
            else:
                self.canvas.itemconfig(rect, fill="#0f2a24")
            if i<5:
                self.root.after(200, lambda: step(i+1))
        step()

    def update_status(self):
        player = PLAYERS[self.current]
        if self.last_action_was_move:
            txt = f"Vez de {player} — (anterior jogador moveu a janela; você deve colocar uma peça)"
        else:
            txt = f"Vez de {player} — clique numa célula para colocar ou mova a janela (setas)"
        self.status_label.config(text=txt)

    def reiniciar(self):
        self.board = [[EMPTY]*BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.win_topleft = (1,1)
        self.current = 0
        self.last_action_was_move = False
        self.draw_board()
        self.update_status()


if __name__ == '__main__':
    root = tk.Tk()
    app = JogoVelhaMovel(root)
    root.mainloop()
