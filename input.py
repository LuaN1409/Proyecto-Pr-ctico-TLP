# -*- coding: utf-8 -*-
"""
Módulo entradas teclado (tkinter)
"""

class GestorEntrada(object):
    def __init__(self, root):
        self.teclas_presionadas = set()
        root.bind("<KeyPress>", self._presionar)
        root.bind("<KeyRelease>", self._soltar)

    def _presionar(self, evento):
        self.teclas_presionadas.add(evento.keysym)

    def _soltar(self, evento):
        if evento.keysym in self.teclas_presionadas:
            self.teclas_presionadas.remove(evento.keysym)

    def tecla_activa(self, tecla):
        """Devuelve True si la tecla indicada está presionada"""
        return tecla in self.teclas_presionadas
