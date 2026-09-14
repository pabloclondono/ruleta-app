from ruleta.constantes import color_numero
from ruleta.modelos.estrategia_3reps import EstrategiaTresRepeticiones
from ruleta.vistas.tab_3reps import VistaTresReps


class ControladorTresReps:
    """Conecta el modelo de "3 Repeticiones" con su vista."""

    def __init__(self):
        self.modelo = EstrategiaTresRepeticiones(banca=200)
        self.vista = VistaTresReps()
        v = self.vista
        v.numero_ingresado.connect(self.registrar)
        v.reiniciar_conteo_pedido.connect(self.reiniciar_conteo)
        v.nueva_ronda_pedida.connect(self.nueva_ronda)
        v.nueva_ronda_rapida_pedida.connect(self.nueva_ronda_rapida)
        v.banca_ingresada.connect(self.aplicar_banca)
        v.apuesta_realizada.connect(self.apuesta)
        v.apuestas_limpiadas.connect(self.limpiar_apuestas)
        v.ficha_seleccionada.connect(self.cambiar_ficha)
        v.render(self.modelo.estado())

    def registrar(self, n):
        m = self.modelo
        v = self.vista
        logs = m.registrar_numero(n)
        v._agregar_historial(n, color_numero(n))
        v.resaltar(str(n))
        for l in logs:
            v._log(l)
        v.render(m.estado())
        v.entry_num.setFocus()

    def reiniciar_conteo(self):
        self.vista._log(self.modelo.reiniciar_conteo())
        self.vista.render(self.modelo.estado())

    def aplicar_banca(self, valor):
        self.vista._log(self.modelo.set_banca(valor))
        self.vista.render(self.modelo.estado())

    def apuesta(self, loc, es_derecho):
        if es_derecho:
            self.modelo.quitar_apuesta(loc)
        else:
            self.modelo.agregar_apuesta(loc)
        self.vista.render(self.modelo.estado())

    def limpiar_apuestas(self):
        self.modelo.limpiar_apuestas()
        self.vista.render(self.modelo.estado())

    def cambiar_ficha(self, valor):
        self.modelo.set_chip(valor)
        self.vista.render(self.modelo.estado())

    def nueva_ronda(self):
        if not self.vista._preguntar(
                "Nueva ronda",
                "¿Reiniciar toda la sesión (apuestas, historial y jugada)?"):
            return
        m = self.modelo
        v = self.vista
        logs = m.nueva_ronda()
        v.limpiar_paneles()
        v.resaltar(None)
        v.render(m.estado())
        for l in logs:
            v._log(l)
        v.entry_num.setFocus()

    def nueva_ronda_rapida(self):
        m = self.modelo
        v = self.vista
        cola = m.ultimas_rondas()
        if not cola:
            self.nueva_ronda()
            return
        if not v._preguntar(
                "Nueva ronda con últimas rondas",
                "¿Empezar nueva ronda conservando los últimos %d números "
                "y sus repeticiones?" % len(cola)):
            return
        logs = m.nueva_ronda_rapida(cola)
        v.limpiar_paneles()
        for n in cola:
            v._agregar_historial(n, color_numero(n))
        v.resaltar(None)
        v.render(m.estado())
        for l in logs:
            v._log(l)
        v.entry_num.setFocus()