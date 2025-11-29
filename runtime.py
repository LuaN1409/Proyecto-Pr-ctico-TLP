# -*- coding: utf-8 -*-
"""
runtime.py - Runtime que carga los JSON generados por el compiler (Entrega 3)
Compatible con Python 2.7 (Tkinter) - Carga /games/snake.json y /games/tetris.json
Menú inicial y ejecuciones de ambos juegos (versión completa pero simple).
"""

import os
import sys
import json
import random
import Tkinter as tk
import tkMessageBox
import time

# --- base path (garantiza que el runtime busque siempre en la carpeta del proyecto) ---
BASE = os.path.dirname(os.path.abspath(__file__))

# --------------------------
#  MENU
# --------------------------
class MenuInicio(object):
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Motor Brik - Menú de Juegos")
        self.root.geometry("420x300")
        self.root.configure(bg="#1a1a1a")

        tk.Label(self.root, text="MOTOR BRIK", fg="white", bg="#1a1a1a",
                 font=("Consolas", 24, "bold")).pack(pady=18)
        tk.Label(self.root, text="Elige un juego", fg="gray", bg="#1a1a1a",
                 font=("Consolas", 12)).pack(pady=6)

        btn_snake = tk.Button(self.root, text="Jugar SNAKE", width=18, height=2,
                              command=lambda: self.seleccionar("snake"),
                              bg="#00aa00", fg="white", font=("Consolas", 12, "bold"))
        btn_snake.pack(pady=10)

        btn_tetris = tk.Button(self.root, text="Jugar TETRIS", width=18, height=2,
                               command=lambda: self.seleccionar("tetris"),
                               bg="#0066cc", fg="white", font=("Consolas", 12, "bold"))
        btn_tetris.pack(pady=10)

        tk.Label(self.root, text="Atajos: S = Snake, T = Tetris", fg="gray",
                 bg="#1a1a1a", font=("Consolas", 10)).pack(pady=8)

        self.root.bind("<Key>", self.leer_tecla)
        self.juego_elegido = None

    def leer_tecla(self, evento):
        k = evento.keysym.lower()
        if k == "s": self.seleccionar("snake")
        elif k == "t": self.seleccionar("tetris")

    def seleccionar(self, juego):
        self.juego_elegido = juego
        self.root.destroy()

    def iniciar(self):
        self.root.mainloop()
        return self.juego_elegido

# --------------------------
#  JUEGO (soporta Snake y Tetris)
# --------------------------
class Juego(object):
    def __init__(self, datos):
        self.datos = datos
        # detect type by campo "juego"
        tipo = datos.get("juego") or datos.get("tipo_juego") or "unknown"
        self.tipo = tipo.upper()
        # pantalla config
        pantalla = datos.get("pantalla", {})
        self.grid_w = int(pantalla.get("ancho", pantalla.get("width", 10)))
        self.grid_h = int(pantalla.get("alto", pantalla.get("height", 20)))
        # cell size: some json (snake) includes tamano_celda, tetris may not
        self.cell = int(pantalla.get("tamano_celda", 25))

        # window & canvas
        self.root = tk.Tk()
        title = datos.get("titulo", "Juego").encode("utf-8") if isinstance(datos.get("titulo"), unicode) else datos.get("titulo")
        self.root.title("Motor Brik - " + (title or self.tipo))
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar)

        self.canvas = tk.Canvas(self.root, width=self.grid_w * self.cell,
                                height=self.grid_h * self.cell, bg="#111111")
        self.canvas.pack(side=tk.LEFT, padx=6, pady=6)

        side = tk.Frame(self.root, bg="#222222")
        side.pack(side=tk.RIGHT, fill=tk.Y)
        self.lbl_score = tk.Label(side, text="PUNTUACIÓN\n0", bg="#222222", fg="white",
                                  font=("Consolas", 14, "bold"))
        self.lbl_score.pack(padx=12, pady=30)
        self.lbl_info = tk.Label(side, text="Flechas: mover\nP: pausa", bg="#222222", fg="gray",
                                 font=("Consolas", 10))
        self.lbl_info.pack(padx=10, pady=10)

        self.root.bind("<Key>", self.on_key)

        # estado común
        self.score = 0
        self.game_over_flag = False
        self.timer = 0.0
        # velocidad default (seconds per gravity step)
        # for snake JSON niveles define velocidad en ms in Entrega 1 (200ms...), convert to seconds
        niveles = datos.get("niveles")
        if isinstance(niveles, list) and len(niveles) > 0:
            # take first level speed if exists and numeric
            v = niveles[0].get("velocidad")
            try:
                self.default_speed = float(v) / 1000.0
            except:
                self.default_speed = 0.15
        else:
            self.default_speed = 0.15

        # dispatch to initialize game type
        if self.tipo == "SNAKE":
            self.init_snake()
        elif self.tipo == "TETRIS":
            self.init_tetris()
        else:
            tkMessageBox.showerror("Error", "Tipo de juego desconocido: %s" % self.tipo)
            self.root.destroy()
            sys.exit(1)

        self.loop_id = None

    # --------------------
    #  KEY HANDLING
    # --------------------
    def on_key(self, ev):
        k = ev.keysym.upper()
        if k == "P":
            self.toggle_pause()
            return
        if self.tipo == "SNAKE":
            if k in ("UP","DOWN","LEFT","RIGHT"):
                self.snake_set_direction(k)
        elif self.tipo == "TETRIS":
            if k == "LEFT": self.tetris_move("LEFT")
            if k == "RIGHT": self.tetris_move("RIGHT")
            if k == "DOWN": self.tetris_move("DOWN")
            if k == "UP": self.tetris_rotate()

    # --------------------
    #  GAME LOOP
    # --------------------
    def run(self):
        # use fixed tick every 50ms
        self.root.after(50, self._loop)
        self.root.mainloop()

    def _loop(self):
        if self.game_over_flag:
            self.show_game_over()
            return
        self.timer += 0.05
        if self.timer >= (self.gravity_speed if hasattr(self, "gravity_speed") else self.default_speed):
            self.timer = 0
            # tick
            if self.tipo == "SNAKE":
                self.snake_tick()
            else:
                self.tetris_tick()
        self.draw()
        self.loop_id = self.root.after(50, self._loop)

    def cerrar(self):
        if self.loop_id:
            self.root.after_cancel(self.loop_id)
        self.root.destroy()
        sys.exit(0)

    def toggle_pause(self):
        if self.loop_id:
            # simple pause by canceling and re-scheduling
            try:
                self.root.after_cancel(self.loop_id)
            except:
                pass
            self.loop_id = None
            tkMessageBox.showinfo("Pausa", "Juego en pausa. Pulsa OK para continuar.")
            self.loop_id = self.root.after(50, self._loop)

    # --------------------
    #  DRAW
    # --------------------
    def draw_cell(self, x, y, color):
        x1 = x * self.cell
        y1 = y * self.cell
        x2 = x1 + self.cell
        y2 = y1 + self.cell
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#000000")

    def draw(self):
        self.canvas.delete("all")
        # draw grid background fixed blocks if any (tetris)
        if self.tipo == "TETRIS":
            for y in range(self.grid_h):
                for x in range(self.grid_w):
                    if self.grid[y][x] == 1:
                        self.draw_cell(x, y, "#303030")
            # draw current piece
            if self.current_piece is not None:
                mat = self.current_piece[self.current_rotation]
                for ry, row in enumerate(mat):
                    for rx, v in enumerate(row):
                        if v:
                            px = self.px + rx
                            py = self.py + ry
                            if 0 <= px < self.grid_w and 0 <= py < self.grid_h:
                                self.draw_cell(px, py, "#00FFFF")
        elif self.tipo == "SNAKE":
            # draw food
            if self.food is not None:
                fx, fy = self.food
                self.draw_cell(fx, fy, "#FF0000")
            # draw snake
            for i, (sx, sy) in enumerate(self.snake_body):
                color = "#00FF00" if i == 0 else "#33CC33"
                self.draw_cell(sx, sy, color)

        # score
        try:
            self.lbl_score.config(text="PUNTUACIÓN\n%d" % self.score)
        except:
            pass

    # --------------------
    #  SNAKE IMPLEMENTATION
    # --------------------
    def init_snake(self):
        cfg = self.datos.get("serpiente", {})
        pos = cfg.get("posicion_inicial", [self.grid_w//2, self.grid_h//2])
        self.snake_body = [(int(pos[0]), int(pos[1]))]
        # initial length
        initial_len = int(cfg.get("longitud_inicial", 3))
        # extend body to the left (default RIGHT direction)
        for i in range(1, initial_len):
            self.snake_body.append((self.snake_body[0][0]-i, self.snake_body[0][1]))
        dir_map = {"UP":(0,-1),"DOWN":(0,1),"LEFT":(-1,0),"RIGHT":(1,0)}
        d = cfg.get("direccion_inicial", "RIGHT")
        self.snake_dir = dir_map.get(d.upper(), (1,0))
        # spawn food and score
        self.food = None
        self.spawn_food()
        self.score = 0
        # speed: use default_speed (converted earlier)
        self.gravity_speed = self.default_speed
        # flags
        self.grow_pending = 0

    def spawn_food(self):
        # use frutas probabilities if present
        frutas = self.datos.get("frutas", {})
        # simple spawn random free cell
        free = []
        for y in range(self.grid_h):
            for x in range(self.grid_w):
                if (x,y) not in self.snake_body:
                    free.append((x,y))
        if not free:
            self.food = None
            return
        self.food = random.choice(free)

    def snake_set_direction(self, key):
        dir_map = {"UP":(0,-1),"DOWN":(0,1),"LEFT":(-1,0),"RIGHT":(1,0)}
        newd = dir_map.get(key)
        if not newd: return
        # avoid reversing
        if (newd[0] == -self.snake_dir[0] and newd[1] == -self.snake_dir[1]):
            return
        self.snake_dir = newd

    def snake_tick(self):
        hx, hy = self.snake_body[0]
        dx, dy = self.snake_dir
        nx, ny = hx + dx, hy + dy
        # collisions with walls
        mec = self.datos.get("mecanicas", {})
        paredes = mec.get("paredes_solidas", True)
        atravesar = mec.get("atravesar_bordes", False)
        if not (0 <= nx < self.grid_w and 0 <= ny < self.grid_h):
            if atravesar:
                nx %= self.grid_w
                ny %= self.grid_h
            elif paredes:
                self.game_over_flag = True
                return
        # collision with self
        if (nx, ny) in self.snake_body[:-1]:
            self.game_over_flag = True
            return
        # move
        self.snake_body.insert(0, (nx, ny))
        # eat?
        if self.food and (nx, ny) == self.food:
            # score
            puntos = self.datos.get("puntuacion", {}).get("por_fruta_normal", 10)
            self.score += int(puntos)
            self.grow_pending += int(self.datos.get("serpiente", {}).get("crecimiento_por_fruta", 1))
            self.spawn_food()
        else:
            if self.grow_pending > 0:
                self.grow_pending -= 1
            else:
                self.snake_body.pop()

    # --------------------
    #  TETRIS IMPLEMENTATION
    # --------------------
    def init_tetris(self):
        # grid: 0 empty, 1 filled
        self.grid = [[0 for _ in range(self.grid_w)] for _ in range(self.grid_h)]
        # shapes: unify structure from JSON: piezas -> piece -> forma -> rotations
        piezas = self.datos.get("piezas", {})
        self.shapes = {}
        for name, info in piezas.items():
            forma = info.get("forma", [])
            # normalize: sometimes parser produced extra nesting; flatten if necessary
            # expecting forma = [ rotation1 (2D list), rotation2, ... ]
            # if we have an extra outer list (1 element that is list of rotations), unwrap
            if len(forma) == 1 and isinstance(forma[0], list) and len(forma[0]) and isinstance(forma[0][0], list):
                # inspect depth: if the inner elements are lists of lists, assume unwrap
                inner = forma[0]
                self.shapes[name] = inner
            else:
                self.shapes[name] = forma
        self.current_piece = None
        self.current_rotation = 0
        self.px = 0; self.py = 0
        self.gravity_speed = max(0.05, (self.default_speed))  # tetris gravity faster often
        self.score = 0
        # spawn first piece
        self.tetris_spawn()

    def choose_random_shape(self):
        keys = self.shapes.keys()
        if not keys: return None
        return random.choice(keys)

    def tetris_spawn(self):
        name = self.choose_random_shape()
        if not name:
            self.current_piece = None
            return
        piece = self.shapes[name]
        # ensure data shape: piece is list of rotations, each rotation is 2D list of ints
        # sometimes rotations may have inner extra nesting, normalize each rotation
        norm = []
        for rot in piece:
            # rot should be list of rows; if it's nested an extra level deep, try to unwrap
            if len(rot) and isinstance(rot[0][0], list):
                # unwrap one level
                norm.append(rot[0])
            else:
                norm.append(rot)
        self.current_piece = norm
        self.current_rotation = 0
        # spawn x centered
        width = len(self.current_piece[0][0]) if isinstance(self.current_piece[0][0], list) else len(self.current_piece[0])
        # safer compute: rotation matrix height/width
        rot0 = self.current_piece[self.current_rotation]
        h = len(rot0)
        w = len(rot0[0]) if h>0 else 1
        self.px = max(0, (self.grid_w // 2) - (w // 2))
        self.py = 0
        # if collision at spawn -> game over
        if self.tetris_collision(self.px, self.py, self.current_rotation):
            self.game_over_flag = True

    def tetris_collision(self, x, y, rotation_index):
        if not self.current_piece: return False
        matrix = self.current_piece[rotation_index]
        for ry, row in enumerate(matrix):
            for rx, v in enumerate(row):
                if v:
                    nx = x + rx; ny = y + ry
                    if not (0 <= nx < self.grid_w and 0 <= ny < self.grid_h):
                        return True
                    if self.grid[ny][nx] == 1:
                        return True
        return False

    def tetris_move(self, direction):
        if not self.current_piece: return
        dx = 0; dy = 0
        if direction == "LEFT": dx = -1
        if direction == "RIGHT": dx = 1
        if direction == "DOWN": dy = 1
        nx = self.px + dx; ny = self.py + dy
        if not self.tetris_collision(nx, ny, self.current_rotation):
            self.px = nx; self.py = ny
        else:
            # if trying to move down and collides -> fix piece
            if dy == 1:
                self.tetris_fix()

    def tetris_rotate(self):
        if not self.current_piece: return
        nr = (self.current_rotation + 1) % len(self.current_piece)
        if not self.tetris_collision(self.px, self.py, nr):
            self.current_rotation = nr

    def tetris_tick(self):
        # move piece down
        if not self.current_piece:
            self.tetris_spawn()
            return
        if not self.tetris_collision(self.px, self.py + 1, self.current_rotation):
            self.py += 1
        else:
            self.tetris_fix()

    def tetris_fix(self):
        # copy current piece into grid
        mat = self.current_piece[self.current_rotation]
        for ry, row in enumerate(mat):
            for rx, v in enumerate(row):
                if v:
                    gx = self.px + rx; gy = self.py + ry
                    if 0 <= gx < self.grid_w and 0 <= gy < self.grid_h:
                        self.grid[gy][gx] = 1
        # clear complete lines
        newgrid = [row for row in self.grid if not all(row)]
        lines_cleared = self.grid_h - len(newgrid)
        if lines_cleared > 0:
            self.grid = [[0]*self.grid_w for _ in range(lines_cleared)] + newgrid
            self.score += lines_cleared * self.datos.get("puntuacion", {}).get("linea_simple", 100)
        # spawn next piece
        self.current_piece = None
        self.tetris_spawn()

    # --------------------
    #  TICK / DRAW wrapper
    # --------------------
    def tetris_tick(self):
        # gravity
        if not self.current_piece:
            self.tetris_spawn()
            return
        if not self.tetris_collision(self.px, self.py + 1, self.current_rotation):
            self.py += 1
        else:
            self.tetris_fix()

    # --------------------
    #  GAME OVER + EXIT
    # --------------------
    def show_game_over(self):
        tkMessageBox.showinfo("Fin del juego", "Puntuación: %d" % self.score)
        self.root.destroy()
        sys.exit(0)

# --------------------------
#  MAIN
# --------------------------
def main():
    menu = MenuInicio()
    juego = menu.iniciar()
    if not juego:
        sys.exit(0)

    ruta = os.path.join(BASE, "games", "%s.json" % juego)
    # diagnostic print to console (also helpful when double-click)
    print("[DEBUG] Cargando JSON:", ruta)
    if not os.path.exists(ruta):
        tkMessageBox.showerror("Error", "No se pudo cargar:\n" + ruta)
        sys.exit(1)

    try:
        with open(ruta, "r") as f:
            datos = json.load(f)
    except Exception as e:
        tkMessageBox.showerror("Error", "No se pudo parsear JSON:\n%s\n\n%s" % (ruta, str(e)))
        sys.exit(1)

    juego_obj = Juego(datos)
    juego_obj.run()

if __name__ == "__main__":
    main()
