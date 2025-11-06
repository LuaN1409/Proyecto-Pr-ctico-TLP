# -*- coding: utf-8 -*-
"""
motor_runtime.py
Motor de juego simple con bucle principal, render y entrada
Compatible con Python 2.7 / Windows XP
"""

import time
from render import Renderizador
from input import GestorEntrada

# configuración del ladrillo
POS_X = 300
POS_Y = 220
VELOCIDAD = 5

def main():
    motor = Renderizador("Motor Brik - Entrega 2")
    entrada = GestorEntrada(motor.root)

    global POS_X, POS_Y
    corriendo = True

    motor.dibujar_texto(320, 30, "Usa las flechas para mover el ladrillo", "yellow", 14)

    while corriendo:
        # === 1. Entrada ===
        if entrada.tecla_activa("Escape"):
            corriendo = False
            break

        dx = 0
        dy = 0
        if entrada.tecla_activa("Left"):
            dx = -VELOCIDAD
        if entrada.tecla_activa("Right"):
            dx = VELOCIDAD
        if entrada.tecla_activa("Up"):
            dy = -VELOCIDAD
        if entrada.tecla_activa("Down"):
            dy = VELOCIDAD

        POS_X += dx
        POS_Y += dy

        # Limitar dentro de la ventana
        POS_X = max(0, min(POS_X, 600))
        POS_Y = max(0, min(POS_Y, 440))

        # === 2. Actualización lógica ===
        # (en este motor básico no hay más lógica por ahora)

        # === 3. Renderizado ===
        motor.limpiar()
        motor.dibujar_texto(320, 30, "Usa las flechas para mover el ladrillo", "yellow", 14)
        motor.dibujar_ladrillo(POS_X, POS_Y, "red", 40)
        motor.actualizar()

        time.sleep(0.016)  # ~60 FPS

    motor.cerrar()

if __name__ == "__main__":
    main()

