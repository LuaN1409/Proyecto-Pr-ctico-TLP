# -*- coding: utf-8 -*-
"""
Motor Brik - Entrega 2
Runtime del motor de juego
Versión final con cierre limpio y manejo de errores
"""

import time
import sys
import traceback
from render import Renderizador
from input import GestorEntrada

POS_X = 300
POS_Y = 220
VELOCIDAD = 5

def main():
    try:
        motor = Renderizador("Motor Brik - Entrega 2")
        entrada = GestorEntrada(motor.root)

        global POS_X, POS_Y
        corriendo = True

        motor.dibujar_texto(320, 30, "Usa las flechas para mover el ladrillo", "yellow", 14)

        while corriendo:
            # Entrada
            if entrada.tecla_activa("Escape"):
                corriendo = False
                break

            dx = dy = 0
            if entrada.tecla_activa("Left"): dx = -VELOCIDAD
            if entrada.tecla_activa("Right"): dx = VELOCIDAD
            if entrada.tecla_activa("Up"): dy = -VELOCIDAD
            if entrada.tecla_activa("Down"): dy = VELOCIDAD

            POS_X += dx
            POS_Y += dy

            # Límites
            POS_X = max(0, min(POS_X, 600))
            POS_Y = max(0, min(POS_Y, 440))

            # Render
            motor.limpiar()
            motor.dibujar_texto(320, 30, "Usa las flechas para mover el ladrillo", "yellow", 14)
            motor.dibujar_ladrillo(POS_X, POS_Y, "red", 40)
            motor.actualizar()

            time.sleep(0.016)

        motor.cerrar()

        # Salida limpia del proceso
        sys.exit(0)

    except Exception as e:
        # Captura errores y los guarda en un archivo
        with open("error_log.txt", "w") as f:
            f.write(traceback.format_exc())
        print("Error fatal en motor_runtime: %s" % e)
        sys.exit(1)

if __name__ == "__main__":
    main()
