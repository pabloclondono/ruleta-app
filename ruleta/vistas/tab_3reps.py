from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QVBoxLayout, QWidget,
)

from ruleta.constantes import ORO, SUB, TEXTO
from ruleta.vistas.base import BaseTab
from ruleta.vistas.fichas import ChipBar
from ruleta.vistas.mesa import MesaWidget


class VistaTresReps(BaseTab):
    """Interfaz de la estrategia "3 Repeticiones" (sin lógica de negocio)."""

    numero_ingresado = Signal(int)
    numero_sin_apuesta = Signal(int)
    reiniciar_conteo_pedido = Signal()
    nueva_ronda_pedida = Signal()
    nueva_ronda_rapida_pedida = Signal()
    banca_ingresada = Signal(int)
    apuesta_realizada = Signal(str, bool)
    apuestas_limpiadas = Signal()
    ficha_seleccionada = Signal(int)

    def __init__(self):
        super().__init__()
        self.bets = {}
        self.estrategia = {}
        self.ultima_celda = None
        self.chip = 500

        self._construir()
        self.render({
            "fase": "obs", "juego_tiros": 0, "tiros": 0,
            "estrategia": {}, "perdida": 0, "limite": None, "unidad": 1,
            "banca": 200, "saldo": 200, "beneficio": 0, "bets": {},
            "chip": 500, "juego_count": {},
        })
        self.mesa.apuesta.connect(self.apuesta_realizada)
        self.chips.ficha.connect(self.ficha_seleccionada)
        self.entry_num.setFocus()

    # ---------- construcción ----------

    def _construir(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        self._fila_registro(layout)
        self._paneles(layout)
        layout.addWidget(self._cinta_estrategia())
        self._marco_mesa(layout)
        self._btn_nueva(layout)

    def _fila_registro(self, layout):
        fila = QHBoxLayout()
        fila.setSpacing(8)
        fila.addWidget(self._etiqueta("REGISTRAR NÚMERO", ORO, "peq"))

        self.entry_num = QLineEdit()
        self.entry_num.setMaxLength(2)
        self.entry_num.setFixedWidth(64)
        self.entry_num.setAlignment(Qt.AlignCenter)
        self.entry_num.setStyleSheet(
            "QLineEdit{background:#0d0d0d;color:white;border:1px solid #2c2c2c;"
            "padding:4px;}")
        self._reg_fuente(self.entry_num, "hist")
        self.entry_num.returnPressed.connect(self._emitir_numero)
        fila.addWidget(self.entry_num)

        fila.addWidget(self._btn("Registrar", self._emitir_numero,
                                 ORO, "#1a1a1a", "peq"))
        fila.addWidget(self._btn("Registrar sin apuesta",
                                 self._emitir_numero_sin_apuesta,
                                 "#6b4f1f", "white", "peq"))
        fila.addWidget(self._btn("Limpiar apuestas manuales",
                                 self.apuestas_limpiadas.emit,
                                 "#3a3a3a", TEXTO, "sub"))

        fila.addStretch(1)
        self.lbl_tiros = self._etiqueta("Tiros: 0", TEXTO, "sub")
        self.lbl_saldo = self._etiqueta("Saldo: $200", ORO, "peq")
        fila.addWidget(self.lbl_tiros)
        fila.addWidget(self.lbl_saldo)
        layout.addLayout(fila, 0)

    def _cinta_estrategia(self):
        cinta = QFrame()
        cinta.setStyleSheet(
            "QFrame{background:#101010;border:1px solid #2c2c2c;}")
        h = QHBoxLayout(cinta)
        h.setContentsMargins(8, 6, 8, 6)
        h.setSpacing(10)

        def bloque(titulo, widget, stretch=1):
            caja = QVBoxLayout()
            caja.setSpacing(1)
            t = self._etiqueta(titulo, SUB, "sub")
            t.setAlignment(Qt.AlignHCenter)
            if isinstance(widget, QLabel):
                widget.setAlignment(Qt.AlignHCenter)
                widget.setWordWrap(True)
            caja.addWidget(t)
            caja.addWidget(widget)
            h.addLayout(caja, stretch)

        luces = QWidget()
        lh = QHBoxLayout(luces)
        lh.setContentsMargins(0, 0, 0, 0)
        lh.setSpacing(4)
        self.luz_amar = self._luz("#ffc933", "Observando")
        self.luz_verde = self._luz("#2ecc40", "Jugando")
        lh.addWidget(self.luz_amar, 0, Qt.AlignHCenter)
        lh.addWidget(self.luz_verde, 0, Qt.AlignHCenter)
        bloque("FASE", luces, 0)

        self.lbl_apostados = self._etiqueta("—", TEXTO, "peq")
        bloque("APOSTADOS", self.lbl_apostados, 2)

        self.lbl_perdida = self._etiqueta("-0 ficha(s)", TEXTO, "peq")
        caja_perd = QVBoxLayout()
        caja_perd.setSpacing(1)
        t = self._etiqueta("PÉRDIDA", SUB, "sub")
        t.setAlignment(Qt.AlignHCenter)
        self.lbl_perdida.setAlignment(Qt.AlignHCenter)
        self.lbl_perdida.setWordWrap(True)
        caja_perd.addWidget(t)
        caja_perd.addWidget(self.lbl_perdida)
        caja_perd.addWidget(self._btn("Reiniciar conteo",
                                      self.reiniciar_conteo_pedido.emit,
                                      "#7a4d1a", "white", "sub"),
                            0, Qt.AlignHCenter)
        h.addLayout(caja_perd, 2)

        self.lbl_unidad = self._etiqueta("1 ficha(s)", TEXTO, "peq")
        bloque("UNIDAD", self.lbl_unidad, 0)

        self.entry_banca = QLineEdit()
        self.entry_banca.setFixedWidth(70)
        self.entry_banca.setAlignment(Qt.AlignCenter)
        self.entry_banca.setStyleSheet(
            "QLineEdit{background:#1a1a1a;color:white;border:1px solid #2c2c2c;"
            "padding:2px 4px;}")
        self._reg_fuente(self.entry_banca, "sub")
        self.entry_banca.setText("200")
        caja_ban = QVBoxLayout()
        caja_ban.setSpacing(1)
        t = self._etiqueta("BANCA", SUB, "sub")
        t.setAlignment(Qt.AlignHCenter)
        fila_ban = QHBoxLayout()
        fila_ban.setSpacing(4)
        fila_ban.addWidget(self.entry_banca, 0, Qt.AlignHCenter)
        fila_ban.addWidget(self._btn("OK", self._emitir_banca,
                                     "#3a3a3a", TEXTO, "sub"))
        caja_ban.addWidget(t)
        caja_ban.addLayout(fila_ban)
        h.addLayout(caja_ban, 1)

        self.lbl_benef = self._etiqueta("+$0", "#4caf50", "peq")
        bloque("BENEFICIO", self.lbl_benef, 0)
        return cinta

    def _paneles(self, layout):
        zona = QHBoxLayout()
        zona.setSpacing(6)
        self._marco_hist, self.txt_historial = self._caja_texto("HISTORIAL")
        self._marco_rep, self.txt_repetidos = self._caja_texto(
            "REPETIDOS EN ESTA JUGADA")
        self._marco_log, self.txt_log = self._caja_texto("RESULTADOS")
        zona.addWidget(self._marco_hist, 1)
        zona.addWidget(self._marco_rep, 1)
        zona.addWidget(self._marco_log, 1)
        layout.addLayout(zona, 2)

    def _marco_mesa(self, layout):
        contenedor = QWidget()
        v = QVBoxLayout(contenedor)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(2)
        self.mesa = MesaWidget(self)
        self.chips = ChipBar(self)
        v.addWidget(self.mesa, 1)
        v.addWidget(self.chips, 0)
        layout.addWidget(contenedor, 5)

    def _btn_nueva(self, layout):
        row = QHBoxLayout()
        row.setSpacing(6)
        b1 = self._btn("NUEVA RONDA", self.nueva_ronda_pedida.emit,
                       "#9c1010", "white", "btn")
        b2 = self._btn("NUEVA RONDA CON ÚLTIMAS RONDAS",
                       self.nueva_ronda_rapida_pedida.emit, "#7a4d1a",
                       "white", "btn")
        b1.setMinimumHeight(38)
        b2.setMinimumHeight(38)
        row.addWidget(b1, 1)
        row.addWidget(b2, 1)
        layout.addLayout(row, 0)

    # ---------- entrada de datos ----------

    def _emitir_numero(self):
        n = self._leer_numero()
        if n is None:
            return
        self.entry_num.clear()
        self.numero_ingresado.emit(n)

    def _emitir_numero_sin_apuesta(self):
        n = self._leer_numero()
        if n is None:
            return
        self.entry_num.clear()
        self.numero_sin_apuesta.emit(n)

    def _leer_numero(self):
        texto = self.entry_num.text().strip()
        if not texto:
            return None
        try:
            n = int(texto)
        except ValueError:
            QMessageBox.warning(self, "Error", "Ingresa un número válido.")
            return None
        if n < 0 or n > 36:
            QMessageBox.warning(self, "Error",
                                "El número debe estar entre 0 y 36.")
            return None
        return n

    def _emitir_banca(self):
        texto = self.entry_banca.text().strip()
        try:
            valor = int(texto)
        except ValueError:
            QMessageBox.warning(self, "Error", "Banca inválida.")
            return
        self.banca_ingresada.emit(valor)

    # ---------- acciones de la vista ----------

    def resaltar(self, loc):
        self.ultima_celda = loc
        self.mesa.update()

    def limpiar_paneles(self):
        self.txt_historial.clear()
        self.txt_log.clear()
        self.txt_repetidos.clear()
        self._insertar_pane(self.txt_repetidos, "Ninguno todavía", TEXTO)

    def render(self, e):
        self.bets = e["bets"]
        self.estrategia = e["estrategia"]
        self.chip = e["chip"]
        fase = e["fase"]
        juego_tiros = e["juego_tiros"]
        perdida = e["perdida"]
        limite = e["limite"]
        unidad = e["unidad"]
        n_num = len(e["estrategia"])

        if fase == "obs":
            self._set_luz(self.luz_amar, True)
            self._set_luz(self.luz_verde, False)
            tip = "Observando · giro %d" % juego_tiros
            if 9 <= juego_tiros <= 20:
                tip += "\nZona amarilla: un repetido es más probable."
            self.luz_amar.setToolTip(tip)
            self.luz_verde.setToolTip("Jugando (números apostados)")
        else:
            self._set_luz(self.luz_amar, False)
            self._set_luz(self.luz_verde, True)
            self.luz_amar.setToolTip("Observando (sin apuestas)")
            self.luz_verde.setToolTip("Jugando con %d número(s)" % n_num)

        self.lbl_apostados.setText(
            ", ".join(str(k) for k in e["estrategia"]) or "—")

        if limite is None:
            self.lbl_perdida.setText("-%d ficha(s)" % perdida)
            self.lbl_perdida.setStyleSheet("color:%s;" % TEXTO)
            self.lbl_perdida.setToolTip("Pérdida acumulada en esta jugada.")
        else:
            self.lbl_perdida.setText("-%d / -%d" % (perdida, limite))
            if perdida >= limite * 0.75:
                self.lbl_perdida.setStyleSheet("color:#ff5252;")
            else:
                self.lbl_perdida.setStyleSheet("color:%s;" % TEXTO)
            apuesta_giro = n_num * unidad
            falta = max(0, limite - perdida)
            self.lbl_perdida.setToolTip(
                "Pérdida en esta jugada: %d ficha(s)\n"
                "Cada giro pierdes %d × %d = %d ficha(s)\n"
                "Límite = fichas apostadas × 36 − 12 = %d × 36 − 12 = %d\n"
                "Faltan %d ficha(s) para sumar 1 ficha por número.\n"
                "Al superarlo subes a %d ficha(s) por número."
                % (perdida, n_num, unidad, apuesta_giro, unidad, limite,
                   falta, unidad + 1))

        self.lbl_unidad.setText("%d ficha(s)" % unidad)
        self.lbl_tiros.setText("Tiros: %d" % e["tiros"])
        saldo = e["saldo"]
        color_saldo = "#ff5252" if saldo < 0 else ORO
        self.lbl_saldo.setText("Saldo: $%d" % saldo)
        self.lbl_saldo.setStyleSheet("color:%s;" % color_saldo)
        self.lbl_saldo.setToolTip(
            "Tu saldo en dinero.\n"
            "Baja cada giro según lo que apuestas en ese momento "
            "(apostados × unidad × ficha) y sube cuando aciertas la "
            "3ª repetición (+unidad × 36 × ficha).\n"
            "Se reinicia al establecer una nueva banca.")
        self.lbl_benef.setText("+$%d" % e["beneficio"])

        self._actualizar_repetidos(e["juego_count"])
        self.mesa.update()
        self.chips.update()

    def _actualizar_repetidos(self, juego_count):
        repetidos = [(n, c) for n, c in juego_count.items() if c >= 2]
        repetidos.sort(key=lambda x: (-x[1], x[0]))
        self.txt_repetidos.clear()
        if repetidos:
            for n, c in repetidos:
                sufijo = "  <- ¡3ª!" if n in self.estrategia and c >= 3 else ""
                self._insertar_pane(self.txt_repetidos,
                                    "%3d  ->  %d veces%s" % (n, c, sufijo),
                                    TEXTO)
        else:
            self._insertar_pane(self.txt_repetidos, "Ninguno todavía", TEXTO)