# -*- coding: utf-8 -*-
"""
runtime.py - Motor de juegos BRIK optimizado (Entrega 3)
Compatible con Python 2.7 + Tkinter
Soporta Snake y Tetris con mecánicas básicas
"""

import os
import sys
import json
import random
import Tkinter as tk
import tkMessageBox
import time

BASE = os.path.dirname(os.path.abspath(__file__))

# ========== MAPEO DE COLORES ==========
COLOR_MAP = {
    "negro": "#000000", "blanco": "#FFFFFF",
    "rojo": "#FF0000", "verde": "#00FF00", "azul": "#0000FF",
    "amarillo": "#FFFF00", "cyan": "#00FFFF", "magenta": "#FF00FF",
    "naranja": "#FF8800", "rosa": "#FF69B4", "morado": "#9932CC",
    "gris": "#808080", "gris_oscuro": "#404040",
    "verde_claro": "#90EE90", "amarillo_claro": "#FFFFE0",
    "azul_electrico": "#00BFFF", "rojo_brillante": "#FF4444",
    "morado_brillante": "#DD44DD", "dorado": "#FFD700"
}

def get_color(nombre):
    """Convierte nombre de color a hexadecimal"""
    return COLOR_MAP.get(nombre, nombre if nombre.startswith("#") else "#FFFFFF")

# ========== MENÚ INICIAL ==========
class MenuInicio(object):
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Motor Brik - Menu Principal")
        self.root.geometry("450x350")
        self.root.configure(bg="#1a1a1a")
        self.root.resizable(False, False)
        
        # Título
        tk.Label(self.root, text="MOTOR BRIK", fg="#00FF00", bg="#1a1a1a",
                 font=("Consolas", 28, "bold")).pack(pady=25)
        
        tk.Label(self.root, text="Entrega 3 - TLP 2025", fg="gray", bg="#1a1a1a",
                 font=("Consolas", 10)).pack(pady=5)
        
        tk.Label(self.root, text="Selecciona un juego", fg="white", bg="#1a1a1a",
                 font=("Consolas", 12)).pack(pady=15)
        
        # Botones
        btn_snake = tk.Button(self.root, text="🐍 SNAKE", width=20, height=2,
                              command=lambda: self.seleccionar("snake"),
                              bg="#00aa00", fg="white", 
                              font=("Consolas", 13, "bold"),
                              activebackground="#00dd00")
        btn_snake.pack(pady=8)
        
        btn_tetris = tk.Button(self.root, text="🧱 TETRIS", width=20, height=2,
                               command=lambda: self.seleccionar("tetris"),
                               bg="#0066cc", fg="white", 
                               font=("Consolas", 13, "bold"),
                               activebackground="#0088ff")
        btn_tetris.pack(pady=8)
        
        tk.Label(self.root, text="Atajos: S = Snake | T = Tetris | ESC = Salir",
                 fg="#666666", bg="#1a1a1a", font=("Consolas", 9)).pack(pady=20)
        
        self.root.bind("<Key>", self.on_key)
        self.juego_elegido = None
    
    def on_key(self, ev):
        k = ev.keysym.lower()
        if k == "s": self.seleccionar("snake")
        elif k == "t": self.seleccionar("tetris")
        elif k == "escape": self.root.destroy()
    
    def seleccionar(self, juego):
        self.juego_elegido = juego
        self.root.destroy()
    
    def iniciar(self):
        self.root.mainloop()
        return self.juego_elegido

# ========== MOTOR DE JUEGO ==========
class Juego(object):
    def __init__(self, datos):
        self.datos = datos
        self.tipo = datos.get("juego", "").upper()
        
        # Configuración de pantalla
        pantalla = datos.get("pantalla", {})
        self.grid_w = int(pantalla.get("ancho", 20))
        self.grid_h = int(pantalla.get("alto", 20))
        self.cell = int(pantalla.get("tamano_celda", 25))
        
        # Ventana principal
        self.root = tk.Tk()
        titulo = datos.get("titulo", self.tipo)
        if isinstance(titulo, unicode):
            titulo = titulo.encode("utf-8")
        self.root.title("Motor Brik - " + str(titulo))
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar)
        self.root.resizable(False, False)
        
        # Canvas de juego
        self.canvas = tk.Canvas(self.root, 
                                width=self.grid_w * self.cell,
                                height=self.grid_h * self.cell, 
                                bg=get_color(pantalla.get("color_fondo", "negro")),
                                highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Panel lateral
        side = tk.Frame(self.root, bg="#222222", width=220)
        side.pack(side=tk.RIGHT, fill=tk.Y)
        side.pack_propagate(False)
        
        self.lbl_score = tk.Label(side, text="PUNTOS\n0", bg="#222222", 
                                  fg="#00FF00", font=("Consolas", 18, "bold"))
        self.lbl_score.pack(padx=15, pady=25)
        
        self.lbl_nivel = tk.Label(side, text="NIVEL 1", bg="#222222", 
                                  fg="#00FFFF", font=("Consolas", 13, "bold"))
        self.lbl_nivel.pack(padx=15, pady=10)
        
        self.lbl_info = tk.Label(side, text="", bg="#222222", fg="#AAAAAA",
                                 font=("Consolas", 9), justify=tk.LEFT)
        self.lbl_info.pack(padx=12, pady=15, anchor=tk.W)
        
        tk.Label(side, text="P = Pausa\nESC = Salir", bg="#222222", 
                fg="#666666", font=("Consolas", 8)).pack(side=tk.BOTTOM, pady=15)
        
        # Estado del juego
        self.score = 0
        self.nivel_actual = 0
        self.game_over_flag = False
        self.paused = False
        self.timer = 0.0
        
        self.root.bind("<Key>", self.on_key)
        
        # Inicializar juego específico
        if self.tipo == "SNAKE":
            self.init_snake()
        elif self.tipo == "TETRIS":
            self.init_tetris()
        else:
            tkMessageBox.showerror("Error", "Tipo de juego desconocido: " + self.tipo)
            self.root.destroy()
            sys.exit(1)
        
        self.loop_id = None
    
    def on_key(self, ev):
        k = ev.keysym.upper()
        
        if k == "ESCAPE":
            self.cerrar()
            return
        
        if k == "P":
            self.toggle_pause()
            return
        
        if self.paused or self.game_over_flag:
            return
        
        # Controles específicos del juego
        if self.tipo == "SNAKE":
            if k in ("UP", "DOWN", "LEFT", "RIGHT"):
                self.snake_set_direction(k)
        
        elif self.tipo == "TETRIS":
            if k == "LEFT": 
                self.tetris_move("LEFT")
            elif k == "RIGHT": 
                self.tetris_move("RIGHT")
            elif k == "DOWN": 
                self.tetris_move("DOWN")
            elif k == "UP": 
                self.tetris_rotate()
            elif k == "SPACE": 
                self.tetris_hard_drop()
    
    def toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            self.lbl_info.config(text="\n  PAUSADO\n  (P para continuar)\n")
        else:
            if self.tipo == "SNAKE":
                self.actualizar_info_snake()
            else:
                self.actualizar_info_tetris()
    
    def run(self):
        """Inicia el loop principal"""
        self.root.after(50, self._loop)
        self.root.mainloop()
    
    def _loop(self):
        """Loop de juego (cada 50ms)"""
        if self.game_over_flag:
            self.show_game_over()
            return
        
        if self.paused:
            self.loop_id = self.root.after(50, self._loop)
            return
        
        self.timer += 0.05
        
        # Tick de gravedad
        if self.timer >= self.gravity_speed:
            self.timer = 0
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
    
    def draw_cell(self, x, y, color):
        """Dibuja una celda en el grid"""
        x1 = x * self.cell
        y1 = y * self.cell
        x2 = x1 + self.cell - 1
        y2 = y1 + self.cell - 1
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#1a1a1a", width=1)
    
    def draw(self):
        """Dibuja el frame actual"""
        self.canvas.delete("all")
        
        if self.tipo == "SNAKE":
            self.draw_snake()
        else:
            self.draw_tetris()
        
        # Actualizar labels
        self.lbl_score.config(text="PUNTOS\n%d" % self.score)
    
    def show_game_over(self):
        msg = "GAME OVER\n\nPuntuacion: %d\nNivel: %d" % (self.score, self.nivel_actual + 1)
        tkMessageBox.showinfo("Fin del juego", msg)
        self.cerrar()
    
    # ==================== SNAKE ====================
    def init_snake(self):
        """Inicializa el juego Snake"""
        cfg = self.datos.get("serpiente", {})
        pos = cfg.get("posicion_inicial", [self.grid_w//2, self.grid_h//2])
        
        # Cuerpo de la serpiente
        self.snake_body = [(int(pos[0]), int(pos[1]))]
        initial_len = int(cfg.get("longitud_inicial", 3))
        for i in range(1, initial_len):
            self.snake_body.append((self.snake_body[0][0] - i, self.snake_body[0][1]))
        
        # Dirección inicial
        dir_map = {"UP":(0,-1), "DOWN":(0,1), "LEFT":(-1,0), "RIGHT":(1,0)}
        d = cfg.get("direccion_inicial", "RIGHT").upper()
        self.snake_dir = dir_map.get(d, (1, 0))
        
        # Comida
        self.food = None
        self.food_type = "manzana"
        self.food_spawn_time = 0
        self.spawn_food()
        
        # Velocidad
        niveles = self.datos.get("niveles", [])
        if niveles and len(niveles) > 0:
            self.gravity_speed = float(niveles[0].get("velocidad", 150)) / 1000.0
        else:
            self.gravity_speed = 0.15
        
        # Contadores
        self.frutas_comidas = 0
        
        self.actualizar_info_snake()
    
    def spawn_food(self):
        """Genera nueva comida con probabilidades"""
        frutas = self.datos.get("frutas", {})
        
        # Elegir tipo de fruta
        rand = random.random()
        acum = 0.0
        self.food_type = "manzana"
        
        for nombre, info in frutas.items():
            prob = float(info.get("probabilidad", 0.0 if nombre != "manzana" else 1.0))
            acum += prob
            if rand <= acum:
                self.food_type = nombre
                break
        
        # Buscar posición libre
        free_cells = []
        for y in range(self.grid_h):
            for x in range(self.grid_w):
                if (x, y) not in self.snake_body:
                    free_cells.append((x, y))
        
        if free_cells:
            self.food = random.choice(free_cells)
            self.food_spawn_time = time.time()
    
    def snake_set_direction(self, key):
        """Cambia dirección de la serpiente"""
        dir_map = {"UP":(0,-1), "DOWN":(0,1), "LEFT":(-1,0), "RIGHT":(1,0)}
        newd = dir_map.get(key)
        if not newd:
            return
        
        # Evitar reversa
        if (newd[0] == -self.snake_dir[0] and newd[1] == -self.snake_dir[1]):
            return
        
        self.snake_dir = newd
    
    def snake_tick(self):
        """Actualización de Snake"""
        hx, hy = self.snake_body[0]
        dx, dy = self.snake_dir
        nx, ny = hx + dx, hy + dy
        
        # Mecánicas de bordes
        mec = self.datos.get("mecanicas", {})
        
        if not (0 <= nx < self.grid_w and 0 <= ny < self.grid_h):
            if mec.get("atravesar_bordes", False):
                nx = nx % self.grid_w
                ny = ny % self.grid_h
            elif mec.get("paredes_solidas", True):
                self.game_over_flag = True
                return
        
        # Colisión consigo mismo
        if (nx, ny) in self.snake_body[:-1]:
            self.game_over_flag = True
            return
        
        # Mover serpiente
        self.snake_body.insert(0, (nx, ny))
        
        # ¿Comió fruta?
        if self.food and (nx, ny) == self.food:
            self.comer_fruta()
        else:
            self.snake_body.pop()
            
            # Verificar si la fruta expiró (solo frutas especiales)
            if self.food and self.food_type != "manzana":
                frutas = self.datos.get("frutas", {})
                fruta_info = frutas.get(self.food_type, {})
                tiempo_vida = fruta_info.get("tiempo_vida", 0)
                
                if tiempo_vida > 0:
                    tiempo_actual = time.time()
                    if (tiempo_actual - self.food_spawn_time) * 1000 > tiempo_vida:
                        # Fruta expiró, generar nueva
                        self.spawn_food()
    
    def comer_fruta(self):
        """Lógica al comer una fruta"""
        frutas = self.datos.get("frutas", {})
        fruta_info = frutas.get(self.food_type, {})
        
        # Puntos
        puntos = int(fruta_info.get("puntos", 10))
        self.score += puntos
        self.frutas_comidas += 1
        
        # No quitar cola (la serpiente crece)
        crecer = int(fruta_info.get("crecimiento_por_fruta", 
                     self.datos.get("serpiente", {}).get("crecimiento_por_fruta", 1)))
        
        for _ in range(crecer - 1):
            self.snake_body.append(self.snake_body[-1])
        
        # Nueva fruta
        self.spawn_food()
        self.actualizar_info_snake()
        
        # Verificar cambio de nivel
        niveles = self.datos.get("niveles", [])
        if self.nivel_actual < len(niveles) - 1:
            req = niveles[self.nivel_actual].get("frutas_requeridas", 999)
            if self.frutas_comidas >= req:
                self.nivel_actual += 1
                self.frutas_comidas = 0
                self.cambiar_nivel_snake()
    
    def cambiar_nivel_snake(self):
        """Cambia al siguiente nivel"""
        niveles = self.datos.get("niveles", [])
        if self.nivel_actual < len(niveles):
            nivel = niveles[self.nivel_actual]
            self.gravity_speed = float(nivel.get("velocidad", 150)) / 1000.0
            self.lbl_nivel.config(text="NIVEL %d\n%s" % 
                                 (self.nivel_actual + 1, nivel.get("nombre", "")))
    
    def actualizar_info_snake(self):
        """Actualiza panel de información"""
        info = "Frutas: %d\nLongitud: %d" % (self.frutas_comidas, len(self.snake_body))
        self.lbl_info.config(text=info)
    
    def draw_snake(self):
        """Dibuja Snake"""
        # Dibujar comida
        if self.food:
            frutas = self.datos.get("frutas", {})
            fruta_info = frutas.get(self.food_type, {})
            color = get_color(fruta_info.get("color", "rojo"))
            self.draw_cell(self.food[0], self.food[1], color)
        
        # Dibujar serpiente
        cfg = self.datos.get("serpiente", {})
        for i, (x, y) in enumerate(self.snake_body):
            if i == 0:
                color = get_color(cfg.get("color_cabeza", "verde_claro"))
            else:
                color = get_color(cfg.get("color_cuerpo", "verde"))
            self.draw_cell(x, y, color)
    
    # ==================== TETRIS ====================
    def init_tetris(self):
        """Inicializa el juego Tetris"""
        # Grid vacío
        self.grid = [[0 for _ in range(self.grid_w)] for _ in range(self.grid_h)]
        
        # Cargar piezas desde JSON
        piezas_data = self.datos.get("piezas", {})
        self.shapes = {}
        
        for nombre, info in piezas_data.items():
            color = get_color(info.get("color", "blanco"))
            formas = info.get("forma", [])
            
            # Normalizar estructura de rotaciones
            rotaciones = []
            for forma in formas:
                if isinstance(forma, list) and len(forma) > 0:
                    if isinstance(forma[0], list):
                        rotaciones.append(forma)
            
            if rotaciones:
                self.shapes[nombre] = {"color": color, "rotations": rotaciones}
        
        # Pieza actual
        self.current_piece = None
        self.current_piece_name = None
        self.current_rotation = 0
        self.px = 0
        self.py = 0
        
        # Velocidad
        niveles = self.datos.get("niveles", [])
        if niveles and len(niveles) > 0:
            self.gravity_speed = float(niveles[0].get("velocidad", 1000)) / 1000.0
        else:
            self.gravity_speed = 1.0
        
        # Contadores
        self.lineas_eliminadas = 0
        
        # Spawear primera pieza
        self.tetris_spawn()
        self.actualizar_info_tetris()
    
    def tetris_spawn(self):
        """Genera nueva pieza"""
        if not self.shapes:
            return
        
        nombre = random.choice(self.shapes.keys())
        shape_info = self.shapes[nombre]
        
        self.current_piece_name = nombre
        self.current_piece = shape_info
        self.current_rotation = 0
        
        # Centrar pieza
        mat = shape_info["rotations"][0]
        w = len(mat[0]) if len(mat) > 0 else 1
        self.px = (self.grid_w - w) // 2
        self.py = 0
        
        # Verificar colisión al spawear (Game Over)
        if self.tetris_collision(self.px, self.py, self.current_rotation):
            self.game_over_flag = True
    
    def tetris_collision(self, x, y, rot):
        """Verifica colisión de pieza"""
        if not self.current_piece:
            return False
        
        mat = self.current_piece["rotations"][rot]
        
        for ry, row in enumerate(mat):
            for rx, val in enumerate(row):
                if val:
                    nx = x + rx
                    ny = y + ry
                    
                    # Fuera de límites
                    if not (0 <= nx < self.grid_w and 0 <= ny < self.grid_h):
                        return True
                    
                    # Colisión con bloques fijos
                    if self.grid[ny][nx] == 1:
                        return True
        
        return False
    
    def tetris_move(self, direction):
        """Mueve pieza horizontalmente o hacia abajo"""
        if not self.current_piece:
            return
        
        dx = 0
        dy = 0
        
        if direction == "LEFT":
            dx = -1
        elif direction == "RIGHT":
            dx = 1
        elif direction == "DOWN":
            dy = 1
        
        nx = self.px + dx
        ny = self.py + dy
        
        if not self.tetris_collision(nx, ny, self.current_rotation):
            self.px = nx
            self.py = ny
        elif dy == 1:  # Intentó bajar pero colisionó
            self.tetris_lock()
    
    def tetris_rotate(self):
        """Rota pieza"""
        if not self.current_piece:
            return
        
        num_rotations = len(self.current_piece["rotations"])
        new_rot = (self.current_rotation + 1) % num_rotations
        
        if not self.tetris_collision(self.px, self.py, new_rot):
            self.current_rotation = new_rot
    
    def tetris_hard_drop(self):
        """Caída instantánea"""
        if not self.current_piece:
            return
        
        while not self.tetris_collision(self.px, self.py + 1, self.current_rotation):
            self.py += 1
        
        self.tetris_lock()
    
    def tetris_tick(self):
        """Gravedad de Tetris"""
        if not self.current_piece:
            self.tetris_spawn()
            return
        
        if not self.tetris_collision(self.px, self.py + 1, self.current_rotation):
            self.py += 1
        else:
            self.tetris_lock()
    
    def tetris_lock(self):
        """Fija pieza en el grid"""
        if not self.current_piece:
            return
        
        mat = self.current_piece["rotations"][self.current_rotation]
        
        # Copiar pieza al grid
        for ry, row in enumerate(mat):
            for rx, val in enumerate(row):
                if val:
                    nx = self.px + rx
                    ny = self.py + ry
                    if 0 <= nx < self.grid_w and 0 <= ny < self.grid_h:
                        self.grid[ny][nx] = 1
        
        # Eliminar líneas completas
        self.tetris_clear_lines()
        
        # Nueva pieza
        self.current_piece = None
        self.tetris_spawn()
    
    def tetris_clear_lines(self):
        """Elimina líneas completas"""
        lineas = 0
        new_grid = []
        
        for row in self.grid:
            if not all(row):  # Si la fila NO está completa
                new_grid.append(row)
            else:
                lineas += 1
        
        # Agregar filas vacías arriba
        while len(new_grid) < self.grid_h:
            new_grid.insert(0, [0] * self.grid_w)
        
        self.grid = new_grid
        
        if lineas > 0:
            self.lineas_eliminadas += lineas
            
            # Calcular puntos
            puntos_cfg = self.datos.get("puntuacion", {})
            if lineas == 1:
                puntos = puntos_cfg.get("linea_simple", 100)
            elif lineas == 2:
                puntos = puntos_cfg.get("linea_doble", 300)
            elif lineas == 3:
                puntos = puntos_cfg.get("linea_triple", 500)
            else:
                puntos = puntos_cfg.get("tetris", 800)
            
            self.score += puntos
            self.actualizar_info_tetris()
            
            # Verificar cambio de nivel
            niveles = self.datos.get("niveles", [])
            if self.nivel_actual < len(niveles) - 1:
                req = niveles[self.nivel_actual].get("lineas_requeridas", 999)
                if self.lineas_eliminadas >= req:
                    self.nivel_actual += 1
                    self.lineas_eliminadas = 0
                    self.cambiar_nivel_tetris()
    
    def cambiar_nivel_tetris(self):
        """Cambia al siguiente nivel"""
        niveles = self.datos.get("niveles", [])
        if self.nivel_actual < len(niveles):
            nivel = niveles[self.nivel_actual]
            self.gravity_speed = float(nivel.get("velocidad", 1000)) / 1000.0
            self.lbl_nivel.config(text="NIVEL %d\n%s" % 
                                 (self.nivel_actual + 1, nivel.get("nombre", "")))
    
    def actualizar_info_tetris(self):
        """Actualiza panel de información"""
        info = "Lineas: %d\nPieza: %s" % (self.lineas_eliminadas, 
                                           self.current_piece_name or "?")
        self.lbl_info.config(text=info)
    
    def draw_tetris(self):
        """Dibuja Tetris"""
        # Dibujar bloques fijos
        for y in range(self.grid_h):
            for x in range(self.grid_w):
                if self.grid[y][x] == 1:
                    self.draw_cell(x, y, "#444444")
        
        # Dibujar pieza actual
        if self.current_piece:
            mat = self.current_piece["rotations"][self.current_rotation]
            color = self.current_piece["color"]
            
            for ry, row in enumerate(mat):
                for rx, val in enumerate(row):
                    if val:
                        nx = self.px + rx
                        ny = self.py + ry
                        if 0 <= nx < self.grid_w and 0 <= ny < self.grid_h:
                            self.draw_cell(nx, ny, color)

# ==================== MAIN ====================
def main():
    """Función principal"""
    print("\n" + "="*50)
    print("MOTOR BRIK - Runtime v3.0")
    print("="*50 + "\n")
    
    # Mostrar menú
    menu = MenuInicio()
    juego_elegido = menu.iniciar()
    
    if not juego_elegido:
        print("Cancelado por el usuario")
        sys.exit(0)
    
    # Cargar JSON del juego
    ruta_json = os.path.join(BASE, "games", "%s.json" % juego_elegido)
    print("[INFO] Cargando: %s" % ruta_json)
    
    if not os.path.exists(ruta_json):
        tkMessageBox.showerror("Error", "Archivo no encontrado:\n" + ruta_json)
        sys.exit(1)
    
    try:
        with open(ruta_json, "r") as f:
            datos = json.load(f)
        print("[OK] JSON cargado correctamente")
    except Exception as e:
        tkMessageBox.showerror("Error", "Error al cargar JSON:\n%s\n\n%s" % (ruta_json, str(e)))
        sys.exit(1)
    
    # Iniciar juego
    print("[INFO] Iniciando juego: %s\n" % juego_elegido.upper())
    juego = Juego(datos)
    juego.run()

if __name__ == "__main__":
    main()