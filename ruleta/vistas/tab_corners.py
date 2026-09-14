from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox, QFrame, QHBoxLayout, QLabel, QLineEdit, QMessageBox,
    QVBoxLayout, QWidget,
)

from ruleta.constantes import (
    ORO, SUB, TEXTO, CORNERES, _nom_corner,
)
from ruleta.vistas.base import BaseTab
from ruleta.vistas.fichas import ChipBar
from ruleta.vistas.mesa import MesaWidget


class VistaCorners(BaseTab):
    """Interfaz de la estrategia "12 Corners" (sin lógica de negocio).

    Réplica de la mesa de "3 Repeticiones": cuando un número sale, se
    señala el corner a jugar (resaltado en blanco) y se coloca la moneda
    correspondiente sobre sus números.
    """

    numero_ingresado = Signal(int)
    cero_toggle = Signal(bool)
    banca_ingresada = Signal(int)
    retiro_pedido = Signal()
    nueva_ronda_pedida = Signal()
    ficha_seleccionada = Signal(int)

    def __init__(self):
        super().__init__()
        self.activos = {}
        self.incluir_cero = True
        self.ultimo_corner = None
        self.chip = 500
        self.bets = {}
        self.apuestas_corner = {}
        self.resaltado = set()
        self.ultima_celda = None
        self.estrategia = {}

        self._construir()
        self.render({
            "fase": "pre", "saldo": 200, "saldo_fichas": 0, "mejor": 0,
            "beneficio": 0, "activos": {},
            "incluir_cero": True, "juego_tiros": 0, "tiros": 0,
            "banca": 200, "ficha_nivel": 1, "apuesta_total": 0,
            "ultimo_corner": None, "chip": 500,
        })
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

        self.chk_cero = QCheckBox("Incluir 0-1-2-3 (cero)")
        self.chk_cero.setChecked(self.incluir_cero)
        self.chk_cero.setStyleSheet("color:%s;" % TEXTO)
        self._reg_fuente(self.chk_cero, "sub")
        self.chk_cero.toggled.connect(self.cero_toggle)
        fila.addWidget(self.chk_cero)

        fila.addStretch(1)
        self.lbl_tiros = self._etiqueta("Tiros: 0", TEXTO, "sub")
        self.lbl_saldo = self._etiqueta("Saldo: $0", ORO, "peq")
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
        self.luz_amar = self._luz("#ffc933", "Esperando primer número")
        self.luz_verde = self._luz("#2ecc40", "Jugando")
        lh.addWidget(self.luz_amar, 0, Qt.AlignHCenter)
        lh.addWidget(self.luz_verde, 0, Qt.AlignHCenter)
        bloque("FASE", luces, 0)

        self.lbl_nivel = self._etiqueta("—", TEXTO, "peq")
        bloque("NIVEL", self.lbl_nivel, 0)
        self.lbl_ficha = self._etiqueta("—", TEXTO, "peq")
        bloque("FICHAS/CORNER", self.lbl_ficha, 0)
        self.lbl_apuesta = self._etiqueta("$0", TEXTO, "peq")
        bloque("APUESTA", self.lbl_apuesta, 0)
        self.lbl_mejor = self._etiqueta("$0", "#4caf50", "peq")
        bloque("MEJOR", self.lbl_mejor, 0)
        self.lbl_benef = self._etiqueta("+$0", "#4caf50", "peq")
        bloque("BENEFICIO (TODA LA PARTIDA)", self.lbl_benef, 0)

        self.entry_banca = QLineEdit()
        self.entry_banca.setFixedWidth(64)
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
        return cinta

    def _paneles(self, layout):
        zona = QHBoxLayout()
        zona.setSpacing(6)
        self._marco_hist, self.txt_historial = self._caja_texto("HISTORIAL")
        self._marco_cn, self.txt_corners = self._caja_texto("CORNERS ACTIVOS")
        self._marco_log, self.txt_log = self._caja_texto("RESULTADOS")
        zona.addWidget(self._marco_hist, 1)
        zona.addWidget(self._marco_cn, 1)
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
        b2 = self._btn("RETIRAR (cierra ciclo en verde)",
                       self.retiro_pedido.emit, "#7a4d1a", "white", "btn")
        b1.setMinimumHeight(38)
        b2.setMinimumHeight(38)
        row.addWidget(b1, 1)
        row.addWidget(b2, 1)
        layout.addLayout(row, 0)

    # ---------- entrada de datos ----------

    def _emitir_numero(self):
        texto = self.entry_num.text().strip()
        if not texto:
            return
        try:
            n = int(texto)
        except ValueError:
            QMessageBox.warning(self, "Error", "Ingresa un número válido.")
            return
        if n < 0 or n > 36:
            QMessageBox.warning(self, "Error",
                                "El número debe estar entre 0 y 36.")
            return
        self.entry_num.clear()
        self.numero_ingresado.emit(n)

    def _emitir_banca(self):
        texto = self.entry_banca.text().strip()
        try:
            valor = int(texto)
        except ValueError:
            QMessageBox.warning(self, "Error", "Banca inválida.")
            return
        self.banca_ingresada.emit(valor)

    # ---------- acciones de la vista ----------

    def limpiar_paneles(self):
        self.txt_historial.clear()
        self.txt_log.clear()
        self._actualizar_corners({}, False)

    def _actualizar_corners(self, activos, incluir_cero):
        self.txt_corners.clear()
        if activos:
            for cid, f in activos.items():
                suf = ""
                if cid == "C0":
                    suf = ("  (incluido)" if incluir_cero
                           else "  (cero excluido)")
                self._insertar_pane(self.txt_corners,
                                    "%s  ->  %d ficha(s)%s"
                                    % (_nom_corner(cid), f, suf), TEXTO)
        else:
            self._insertar_pane(self.txt_corners,
                                "Ninguno todavía. El corner a jugar se "
                                "marca en blanco en la mesa.", TEXTO)

    def render(self, e):
        self.activos = e["activos"]
        self.incluir_cero = e["incluir_cero"]
        self.ultimo_corner = e["ultimo_corner"]
        self.chip = e["chip"]

        if e["fase"] == "pre":
            self._set_luz(self.luz_amar, True)
            self._set_luz(self.luz_verde, False)
        else:
            self._set_luz(self.luz_amar, False)
            self._set_luz(self.luz_verde, True)

        k = len(e["activos"])
        if k == 0:
            self.lbl_nivel.setText("—")
            self.lbl_ficha.setText("—")
            self.lbl_apuesta.setText("$0")
        else:
            self.lbl_nivel.setText(str(k))
            self.lbl_ficha.setText("%d" % e["ficha_nivel"])
            self.lbl_apuesta.setText("$%d" % e["apuesta_total"])

        self.lbl_tiros.setText("Tiros: %d" % e["tiros"])
        saldo = e["saldo"]
        self.lbl_saldo.setText("Saldo: $%d" % saldo)
        self.lbl_saldo.setStyleSheet("color:%s;" %
                                     (ORO if saldo > 0 else
                                      ("#ff5252" if saldo < 0 else TEXTO)))
        self.lbl_saldo.setToolTip(
            "Tu dinero actual: baja según lo que apuestas en cada "
            "tirada (puesta × moneda) y sube cuando aciertas un corner. "
            "Se reinicia al establecer una nueva banca.")

        ben = e["beneficio"]
        if ben >= 0:
            self.lbl_benef.setText("+$%d" % ben)
            self.lbl_benef.setStyleSheet("color:#4caf50;")
        else:
            self.lbl_benef.setText("-$%d" % (-ben))
            self.lbl_benef.setStyleSheet("color:#ff5252;")
        self.lbl_benef.setToolTip(
            "Ganancia o pérdida de toda la partida (dinero actual - "
            "banca). Baja al perder y sube al ganar.")

        self.lbl_mejor.setText("$%d" % (e["mejor"] * e["chip"]))
        self.lbl_mejor.setToolTip(
            "Mejor saldo de fichas alcanzado, en dinero (× moneda).")
        self._actualizar_corners(e["activos"], e["incluir_cero"])

        nivel = e["ficha_nivel"]
        self.apuestas_corner = {
            cid: nivel * self.chip for cid in e["activos"]}
        self.bets = {}

        resaltado = set()
        if e["ultimo_corner"] is not None and not (
                e["ultimo_corner"] == "C0" and not e["incluir_cero"]):
            resaltado = {str(n) for n in CORNERES[e["ultimo_corner"]]}
        self.resaltado = resaltado
        self.ultima_celda = None

        self.mesa.update()
        self.chips.update()