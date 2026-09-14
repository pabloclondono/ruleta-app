from ruleta.constantes import color_numero
from ruleta.modelos.estrategia_corners import EstrategiaCorners
from ruleta.vistas.tab_corners import VistaCorners


class ControladorCorners:
    """Conecta el modelo de "12 Corners" con su vista."""

    def __init__(self):
        self.modelo = EstrategiaCorners(banca=200)
        self.vista = VistaCorners()
        v = self.vista
        v.numero_ingresado.connect(self.registrar)
        v.cero_toggle.connect(self.toggle_cero)
        v.banca_ingresada.connect(self.aplicar_banca)
        v.retiro_pedido.connect(self.retirar)
        v.nueva_ronda_pedida.connect(self.nueva_ronda)
        v.ficha_seleccionada.connect(self.cambiar_chip)
        v.render(self.modelo.estado())

    def cambiar_chip(self, valor):
        self.modelo.set_chip(valor)
        self.vista.render(self.modelo.estado())

    def registrar(self, n):
        m = self.modelo
        v = self.vista
        logs = m.registrar_numero(n)
        v._agregar_historial(n, color_numero(n))
        for l in logs:
            v._log(l)
        v.render(m.estado())
        v.entry_num.setFocus()

    def toggle_cero(self, v):
        self.vista._log(self.modelo.set_incluir_cero(v))
        self.vista.render(self.modelo.estado())

    def aplicar_banca(self, valor):
        self.vista._log(self.modelo.set_banca(valor))
        self.vista.render(self.modelo.estado())

    def retirar(self):
        self.vista._log(self.modelo.retirar())
        self.vista.render(self.modelo.estado())

    def nueva_ronda(self):
        if not self.vista._preguntar(
                "Nueva ronda",
                "¿Reiniciar sesión (saldo, mejor saldo, corners e "
                "historial)?"):
            return
        m = self.modelo
        v = self.vista
        logs = m.nueva_ronda()
        v.limpiar_paneles()
        v.render(m.estado())
        for l in logs:
            v._log(l)
        v.entry_num.setFocus()