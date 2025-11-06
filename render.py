# -*- coding: utf-8 -*-
"""
render.py
Módulo de renderizado usando tkinter (compatible con Python 2.7 / Windows XP)
"""

try:
    import Tkinter as tk  # Python 2.x
except ImportError:
    import tkinter as tk  # compatibilidad

ANCHO_VENTANA = 640
ALTO_VENTANA = 480
COLOR_FONDO = "black"

class Renderizador(object):
    def __init__(self, titulo="Motor Brik"):
        self.root = tk.Tk()
        self.root.title(titulo)
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(
            self.root,
            width=ANCHO_VENTANA,
            height=ALTO_VENTANA,
            bg=COLOR_FONDO,
            highlightthickness=0
        )
        self.canvas.pack()

    def limpiar(self):
        self.canvas.delete("all")

    def dibujar_ladrillo(self, x, y, color="red", tam=40):
        # Dibuja un bloque cuadrado centrado en (x, y)
        self.canvas.create_rectangle(
            x, y, x + tam, y + tam,
            fill=color, outline="white"
        )

    def dibujar_texto(self, x, y, texto, color="white", tam=14):
        self.canvas.create_text(
            x, y, text=texto,
            fill=color, font=("Arial", tam, "bold")
        )

    def actualizar(self):
        self.root.update_idletasks()
        self.root.update()

    def cerrar(self):
        self.root.destroy()
