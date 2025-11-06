# -*- coding: utf-8 -*-
"""
Módulo manejo entradas teclado
"""

class GestorEntrada(object):
    def __init__(self, root):
        # Guarda las teclas presionadas
        self.teclas_presionadas = set()
        root.bind("<KeyPress>", self._presionar)
        root.bind("<KeyRelease>", self._soltar)

    def _presionar(self, evento):
        # Añade la tecla presionada al conjunto
        self.teclas_presionadas.add(evento.keysym)

    def _soltar(self, evento):
        # Elimina la tecla al soltarla
        if evento.keysym in self.teclas_presionadas:
            self.teclas_presionadas.remove(evento.keysym)

    def tecla_activa(self, tecla):
        # Devuelve True si la tecla está presionada
        return tecla in self.teclas_presionadas
