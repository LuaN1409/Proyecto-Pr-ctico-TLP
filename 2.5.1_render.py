# -*- coding: utf-8 -*-

try:
    import Tkinter as tk  
except ImportError:
    import tkinter as tk  

# Constantes de configuración
ANCHO_VENTANA = 640
ALTO_VENTANA = 480
COLOR_FONDO = "black"


class Renderizador(object):
    def __init__(self, titulo="Motor Brik"):
        # Crea ventana principal
        self.root = tk.Tk()
        self.root.title(titulo)
        self.root.resizable(False, False)

        # Crea lienzo de dibujo
        self.canvas = tk.Canvas(
            self.root,
            width=ANCHO_VENTANA,
            height=ALTO_VENTANA,
            bg=COLOR_FONDO,
            highlightthickness=0
        )
        self.canvas.pack()

    def limpiar(self):
        # Limpia todo el lienzo
        self.canvas.delete("all")

    def dibujar_ladrillo(self, x, y, color="red", tam=40):
        # Dibuja un bloque cuadrado
        self.canvas.create_rectangle(
            x, y, x + tam, y + tam,
            fill=color, outline="white"
        )

    def dibujar_texto(self, x, y, texto, color="white", tam=14):
        # Dibuja texto en la pantalla
        self.canvas.create_text(
            x, y, text=texto,
            fill=color, font=("Arial", tam, "bold")
        )

    def actualizar(self):
        # Actualiza la ventana
        self.root.update_idletasks()
        self.root.update()

    def cerrar(self):
        # Cierra la ventana
        self.root.destroy()
