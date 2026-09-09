import sys

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QTextCharFormat, QTextCursor, QTextOption
from PySide6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel, QLineEdit, QMessageBox,
    QPlainTextEdit, QPushButton, QVBoxLayout, QWidget,
)

ROJO = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
NEGRO = set(range(1, 37)) - ROJO
RANGO = [str(n) for n in range(37)]

FILAS = [
    [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36],
    [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35],
    [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34],
]

VALORES_FICHAS = [50, 500, 2500, 5000, 25000, 50000]
COLOR_FICHA = {50: "#d7dce8", 500: "#c81e1e", 2500: "#1d7c1d",
               5000: "#121212", 25000: "#6a2c91", 50000: "#1b4f8a"}
TEXTO_FICHA = {50: "#1a1a1a", 500: "#ffffff", 2500: "#ffffff",
               5000: "#ffffff", 25000: "#ffffff", 50000: "#ffffff"}

FONDO   = "#141414"
PANEL   = "#1e1e1e"
TEXTO   = "#e8e8e8"
SUB     = "#8f8f8f"
ORO     = "#d9a621"
VERDE   = "#166b16"
ROJO_BG = "#c81e1e"
NEGRO_BG = "#111111"
AZUL    = "#1b4f8a"
GRIS    = "#3a3a3a"

BASE_W, BASE_H = 1000, 720


def _claro(color, factor):
    c = QColor(color)
    c = c.lighter(factor)
    return c.name()


class MesaWidget(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self._cajas = []
        self._dibujos = []
        self._loc_rect = {}
        self.setMinimumSize(380, 260)

    def _layout(self):
        self._cajas = []
        self._dibujos = []
        self._loc_rect = {}
        w, h = self.width(), self.height()
        m = max(3, int(round(w * 0.006)))
        ax, ay = m, m
        cw = (w - 2 * m) / 14.0
        rh = (h - 2 * m) / 5.0

        def add(x, y, xs, ys, loc, texto, color):
            rect = QRectF(ax + x * cw, ay + y * rh, xs * cw, ys * rh)
            self._cajas.append((rect, loc))
            self._loc_rect[loc] = rect
            self._dibujos.append((rect, loc, texto, QColor(color)))

        add(0, 0, 1, 3, "0", "0", VERDE)
        for r, fila in enumerate(FILAS):
            for j, num in enumerate(fila):
                bg = ROJO_BG if num in ROJO else NEGRO_BG
                add(1 + j, r, 1, 1, str(num), str(num), bg)
            add(13, r, 1, 1, "col%d" % (r + 1), "2:1", AZUL)

        for i, (texto, loc) in enumerate([("1-12", "dozen1"), ("13-24", "dozen2"),
                                          ("25-36", "dozen3")]):
            add(1 + i * 4, 3, 4, 1, loc, texto, AZUL)

        for i, (texto, loc, col) in enumerate([
                ("1-18", "1-18", GRIS), ("PAR", "par", GRIS),
                ("ROJO", "rojo", ROJO_BG), ("NEGRO", "negro", NEGRO_BG),
                ("IMPAR", "impar", GRIS), ("19-36", "19-36", GRIS)]):
            add(1 + i * 2, 4, 2, 1, loc, texto, col)

    def paintEvent(self, e):
        self._layout()
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.fillRect(self.rect(), QColor(FONDO))

        opt = QTextOption(Qt.AlignCenter)
        for rect, loc, texto, bg in self._dibujos:
            p.fillRect(rect, bg)
            p.setPen(QPen(QColor("#2b2b2b"), 1))
            p.drawRect(rect)

            p.setFont(self.app._fuentes["num"])
            p.setPen(QColor("#f2f2f2"))
            if loc == "0" or loc.lstrip("-").isdigit():
                r_num = QRectF(rect.left(), rect.top() + 2, rect.width(),
                               rect.height() * 0.56)
                p.drawText(r_num, texto, opt)
                fm = p.fontMetrics()
                hr = fm.height()
                if loc in self.app.bets:
                    p.setFont(self.app._fuentes["mon"])
                    fm2 = p.fontMetrics()
                    r_m = QRectF(rect.left(), rect.bottom() - 2 * hr - 2,
                                 rect.width(), hr)
                    p.setPen(QColor(ORO))
                    p.drawText(r_m, "$%d" % self.app.bets[loc], opt)
                    hr2 = fm2.height()
                    if int(loc) in self.app.estrategia:
                        p.setFont(self.app._fuentes["est"])
                        fm3 = p.fontMetrics()
                        r_e = QRectF(rect.left(), rect.bottom() - hr2 - 2,
                                     rect.width(), hr2)
                        p.setPen(QColor("#ffd700"))
                        p.drawText(r_e, "R%d" % self.app.estrategia[int(loc)], opt)
                else:
                    if int(loc) in self.app.estrategia:
                        p.setFont(self.app._fuentes["est"])
                        fm3 = p.fontMetrics()
                        hr3 = fm3.height()
                        r_e = QRectF(rect.left(), rect.bottom() - hr3 - 2,
                                     rect.width(), hr3)
                        p.setPen(QColor("#ffd700"))
                        p.drawText(r_e, "R%d" % self.app.estrategia[int(loc)], opt)
            else:
                p.drawText(rect, texto, opt)

            if self.app.ultima_celda == loc:
                p.setPen(QPen(QColor(ORO), 3))
                p.drawRect(rect.adjusted(1, 1, -1, -1))

    def mousePressEvent(self, e):
        pos = e.position()
        for rect, loc in self._cajas:
            if rect.contains(pos):
                if e.button() == Qt.MouseButton.RightButton:
                    self.app._quitar_apuesta(loc)
                else:
                    self.app._agregar_apuesta(loc)
                return


class ChipBar(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setFixedHeight(48)
        self.setMinimumWidth(200)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.fillRect(self.rect(), QColor(FONDO))

        n = len(VALORES_FICHAS)
        gap = 10
        r = min(19, (self.width() - gap * (n + 1)) / (2.0 * n))
        r = max(10, r)
        step = (self.width() - gap) / float(n)
        cy = self.height() / 2.0
        opt = QTextOption(Qt.AlignCenter)

        for i, valor in enumerate(VALORES_FICHAS):
            cx = gap / 2.0 + i * step + step / 2.0
            sel = (self.app.chip == valor)
            p.setPen(QPen(QColor(ORO if sel else "#5a5a5a"), 3 if sel else 2))
            p.setBrush(QColor(COLOR_FICHA[valor]))
            p.drawEllipse(QRectF(cx - r, cy - r, 2 * r, 2 * r))
            p.setFont(self.app._fuentes["chip"])
            p.setPen(QColor(TEXTO_FICHA[valor]))
            p.drawText(QRectF(cx - r, cy - r, 2 * r, 2 * r), "$%d" % valor, opt)

    def mousePressEvent(self, e):
        pos = e.position()
        n = len(VALORES_FICHAS)
        gap = 10
        r = min(19, (self.width() - gap * (n + 1)) / (2.0 * n))
        r = max(10, r)
        step = (self.width() - gap) / float(n)
        cx0 = gap / 2.0 + step / 2.0
        for i, valor in enumerate(VALORES_FICHAS):
            cx = cx0 + i * step
            if (pos.x() - cx) ** 2 + (pos.y() - self.height() / 2.0) ** 2 <= r * r:
                self.app._set_chip(valor)
                return


class RuletaApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Seguimiento de Ruleta · Estrategia 3 Repeticiones")
        self.resize(1000, 760)
        self.setMinimumSize(820, 620)
        self.setStyleSheet("background-color: %s;" % FONDO)

        self.bets = {}
        self.historial = []
        self.celdas = {}
        self.ultima_celda = None

        self._estado_estrategia()
        self._s = 1.0
        self._wfont = []
        self._crear_fuentes()
        self._construir()
        self._cinta()
        self.entry_num.setFocus()

    # ---------- estado ----------

    def _estado_estrategia(self):
        self.banca = 200
        self.saldo = 200
        self.beneficio = 0
        self.unidad = 1
        self.perdida = 0
        self.juego_tiros = 0
        self.fase = "obs"
        self.juego_count = {}
        self.estrategia = {}
        self.chip = 500

    # ---------- fuentes / escala ----------

    def _crear_fuentes(self):
        self._font_defs = {
            "tit": (14, True), "sub": (10, False), "num": (11, True),
            "mon": (9, True), "chip": (8, True), "hist": (13, True),
            "txt": (10, False), "btn": (13, True), "peq": (10, True),
            "est": (8, True),
        }
        self._fuentes = {}
        self._aplicar_fuentes()

    def _aplicar_fuentes(self):
        for key, (base, bold) in self._font_defs.items():
            f = QFont()
            f.setFamily("DejaVu Sans")
            f.setPointSize(max(6, int(round(base * self._s))))
            f.setBold(bold)
            self._fuentes[key] = f
        for w, key in self._wfont:
            w.setFont(self._fuentes[key])

    def _reg_fuente(self, w, key):
        self._wfont.append((w, key))
        w.setFont(self._fuentes[key])

    def resizeEvent(self, e):
        super().resizeEvent(e)
        w, h = e.size().width(), e.size().height()
        s = min(w / BASE_W, h / BASE_H)
        s = max(0.55, min(1.8, s))
        if abs(s - self._s) < 0.03:
            return
        self._s = s
        self._aplicar_fuentes()
        self.mesa.update()
        self.chips.update()

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
        self.entry_num.returnPressed.connect(self._registrar)
        fila.addWidget(self.entry_num)

        fila.addWidget(self._btn("Registrar", self._registrar, ORO, "#1a1a1a", "peq"))
        fila.addWidget(self._btn("Limpiar apuestas manuales", self._limpiar_apuestas,
                                 GRIS, TEXTO, "sub"))

        fila.addStretch(1)
        self.lbl_tiros = self._etiqueta("Tiros: 0", TEXTO, "sub")
        self.lbl_total = self._etiqueta("Total: $0", ORO, "peq")
        fila.addWidget(self.lbl_tiros)
        fila.addWidget(self.lbl_total)
        layout.addLayout(fila, 0)

    def _etiqueta(self, texto, color, key):
        lbl = QLabel(texto)
        lbl.setStyleSheet("color:%s;" % color)
        self._reg_fuente(lbl, key)
        return lbl

    def _btn(self, texto, comando, bg, fg, key, hover=None, bold=True):
        b = QPushButton(texto)
        if hover is None:
            hover = _claro(bg, 135)
        b.setCursor(Qt.PointingHandCursor)
        b.setStyleSheet(
            "QPushButton{background:%s;color:%s;border:none;padding:5px 12px;"
            "font-weight:%s;}" % (bg, fg, "bold" if bold else "normal")
            + "QPushButton:hover{background:%s;}" % hover)
        self._reg_fuente(b, key)
        b.setFocusPolicy(Qt.NoFocus)
        b.clicked.connect(comando)
        return b

    def _cinta_estrategia(self):
        cinta = QFrame()
        cinta.setStyleSheet(
            "QFrame{background:#101010;border:1px solid #2c2c2c;}")
        h = QHBoxLayout(cinta)
        h.setContentsMargins(10, 4, 10, 4)
        h.setSpacing(8)

        def bloque(titulo, valor_label):
            box = QHBoxLayout()
            box.setSpacing(4)
            box.addWidget(self._etiqueta(titulo, SUB, "sub"))
            box.addWidget(valor_label)
            return box

        self.lbl_fase = self._etiqueta("OBSERVANDO", ORO, "peq")
        h.addLayout(bloque("FASE", self.lbl_fase))
        self.lbl_apostados = self._etiqueta("—", TEXTO, "peq")
        h.addLayout(bloque("APOSTADOS", self.lbl_apostados))
        self.lbl_perdida = self._etiqueta("-0 ficha(s)", TEXTO, "peq")
        h.addLayout(bloque("PÉRDIDA", self.lbl_perdida))
        h.addWidget(self._btn("Reiniciar conteo", self._reiniciar_conteo,
                              "#7a4d1a", "white", "sub"))
        self.lbl_unidad = self._etiqueta("1 ficha(s)", TEXTO, "peq")
        h.addLayout(bloque("UNIDAD", self.lbl_unidad))

        self.entry_banca = QLineEdit()
        self.entry_banca.setFixedWidth(70)
        self.entry_banca.setAlignment(Qt.AlignCenter)
        self.entry_banca.setStyleSheet(
            "QLineEdit{background:#1a1a1a;color:white;border:1px solid #2c2c2c;"
            "padding:2px 4px;}")
        self._reg_fuente(self.entry_banca, "sub")
        self.entry_banca.setText(str(self.banca))
        h.addWidget(self._etiqueta("BANCA", SUB, "sub"))
        h.addWidget(self.entry_banca)
        h.addWidget(self._btn("OK", self._apl_banca, GRIS, TEXTO, "sub"))

        self.lbl_saldo = self._etiqueta("$200", ORO, "peq")
        h.addLayout(bloque("SALDO", self.lbl_saldo))
        self.lbl_benef = self._etiqueta("+$0", "#4caf50", "peq")
        h.addLayout(bloque("BENEFICIO", self.lbl_benef))
        h.addStretch(1)
        return cinta

    def _caja_texto(self, titulo):
        marco = QFrame()
        marco.setStyleSheet("QFrame{background:%s;border:1px solid #2c2c2c;}"
                            % PANEL)
        v = QVBoxLayout(marco)
        v.setContentsMargins(8, 6, 8, 6)
        v.setSpacing(2)
        v.addWidget(self._etiqueta(titulo, ORO, "peq"))
        txt = QPlainTextEdit()
        txt.setReadOnly(True)
        txt.setStyleSheet("QPlainTextEdit{background:#101010;color:%s;"
                          "border:none;}" % TEXTO)
        self._reg_fuente(txt, "txt")
        v.addWidget(txt, 1)
        return marco, txt

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
        b1 = self._btn("NUEVA RONDA", self._nueva_ronda, "#9c1010", "white",
                       "btn")
        b2 = self._btn("NUEVA RONDA CON ÚLTIMAS RONDAS", self._nueva_ronda_rapida,
                       "#7a4d1a", "white", "btn")
        b1.setMinimumHeight(38)
        b2.setMinimumHeight(38)
        row.addWidget(b1, 1)
        row.addWidget(b2, 1)
        layout.addLayout(row, 0)

    # ---------- apuestas manuales ----------

    def _agregar_apuesta(self, loc):
        monto = self.chip
        if monto <= 0:
            return
        self.bets[loc] = self.bets.get(loc, 0) + monto
        self._monito(loc)

    def _quitar_apuesta(self, loc):
        monto = self.chip
        if loc in self.bets:
            self.bets[loc] = max(0, self.bets[loc] - monto)
            if self.bets[loc] == 0:
                del self.bets[loc]
            self._monito(loc)

    def _monito(self, loc):
        if loc in self.bets:
            monto = self.bets[loc]
        else:
            monto = 0
        self.lbl_total.setText("Total: $%d" % sum(self.bets.values()))
        if self.mesa:
            self.mesa.update()

    def _limpiar_apuestas(self):
        self.bets = {}
        self.lbl_total.setText("Total: $0")
        self.mesa.update()

    # ---------- estrategia 3 repeticiones ----------

    def _apl_banca(self):
        texto = self.entry_banca.text().strip()
        try:
            self.saldo = int(texto)
        except ValueError:
            QMessageBox.warning(self, "Error", "Banca inválida.")
            return
        self._cinta()
        self._log("Banca establecida en $%d" % self.saldo)

    def _marcar(self, n):
        self.mesa.update()

    def _desmarcar(self):
        self.mesa.update()

    def _radicar_al_marcar(self):
        self.mesa.update()

    def _reiniciar_conteo(self):
        self.perdida = 0
        self._cinta()
        self._log("Conteo de pérdidas reiniciado. Puedes seguir jugando la jugada.")

    def _fin_juego(self):
        self._desmarcar()
        self.estrategia = {}
        self.juego_count = {}
        self.perdida = 0
        self.unidad = 1
        self.juego_tiros = 0
        self.fase = "obs"
        self._actualizar_repetidos()
        self._cinta()
        self._log("NUEVA JUGADA: observa y apunta los números (sin apostar).")

    def _registrar(self):
        texto = self.entry_num.text().strip()
        if not texto:
            return
        try:
            n = int(texto)
        except ValueError:
            QMessageBox.warning(self, "Error", "Ingresa un número válido.")
            return
        if n < 0 or n > 36:
            QMessageBox.warning(self, "Error", "El número debe estar entre 0 y 36.")
            return

        self.entry_num.clear()
        self.historial.append(n)
        self.lbl_tiros.setText("Tiros: %d" % len(self.historial))
        self.juego_tiros += 1

        color = "rojo" if n in ROJO else ("negro" if n in NEGRO else "verde")
        self._agregar_historial(n, color)
        self._resaltar(str(n))
        self._procesar_jugada(n)
        self._actualizar_repetidos()
        self._cinta()
        self.entry_num.setFocus()

    def _procesar_jugada(self, n):
        c = self.juego_count.get(n, 0) + 1
        self.juego_count[n] = c
        activos = list(self.estrategia)

        if c >= 3 and n in activos:
            N = len(activos)
            ganancia = (36 - N) * self.unidad - self.perdida
            self.beneficio += ganancia
            self._log("¡¡3ª repetición del %d!! Ganas +$%d "
                      "(pleno %d ficha(s), %d números, pérdida previa "
                      "%d ficha(s)). Beneficio total: $%d." %
                      (n, ganancia, self.unidad, N, self.perdida, self.beneficio))
            self._fin_juego()
            return

        if self.fase == "jug" and activos:
            self.perdida += len(activos) * self.unidad

        if c == 2:
            self.estrategia[n] = self.unidad
            self.fase = "jug"
            self._marcar(n)
            self._log("¡%d se repite! Añades %d a las apuestas (ficha %d). "
                      "Va %d número(s) apostados." %
                      (n, n, self.unidad, len(self.estrategia)))

        self._ajustar_nivel()

    def _limite_perdida(self):
        N = len(self.estrategia)
        if N <= 0:
            return None
        return self.unidad * (36 - N) - 12

    def _ajustar_nivel(self):
        cambio = False
        while self.estrategia:
            limite = self._limite_perdida()
            if limite is None or self.perdida <= limite:
                break
            self.unidad += 1
            self.estrategia = {k: self.unidad for k in self.estrategia}
            self._radicar_al_marcar()
            cambio = True
            self._log("Pérdida %d ficha(s): la próxima apuesta superaría "
                      "el límite (-%d). Sumas 1 ficha -> %d ficha(s) "
                      "por número." % (self.perdida, limite, self.unidad))
        if cambio:
            self._cinta()

    # ---------- botones y limpieza ----------

    def _limpiar(self):
        self._desmarcar()
        self.bets = {}
        self.historial = []
        self.estrategia = {}
        self.juego_count = {}
        self.perdida = 0
        self.unidad = 1
        self.juego_tiros = 0
        self.fase = "obs"
        self.lbl_total.setText("Total: $0")
        self.ultima_celda = None
        self.txt_historial.clear()
        self.txt_log.clear()
        self.mesa.update()

    def _preguntar(self, titulo, mensaje):
        r = QMessageBox.question(self, titulo, mensaje,
                                 QMessageBox.StandardButton.Yes |
                                 QMessageBox.StandardButton.No)
        return r == QMessageBox.StandardButton.Yes

    def _nueva_ronda(self):
        if not self._preguntar("Nueva ronda",
                               "¿Reiniciar toda la sesión (apuestas, historial, "
                               "jugada y beneficios)?"):
            return
        self.beneficio = 0
        self._limpiar()
        self.lbl_tiros.setText("Tiros: 0")
        self.lbl_total.setText("Total: $0")
        self.txt_repetidos.clear()
        self._insertar_pane(self.txt_repetidos, "Ninguno todavía", TEXTO)
        self._cinta()
        self._log("Nueva sesión. Observa y apunta los números.")

    def _nueva_ronda_rapida(self):
        cola = list(self.historial[-15:])
        if not cola:
            self._nueva_ronda()
            return
        if not self._preguntar(
                "Nueva ronda con últimas rondas",
                "¿Empezar nueva ronda conservando los últimos %d números "
                "y sus repeticiones?" % len(cola)):
            return
        self.beneficio = 0
        self._limpiar()
        self.historial = cola
        self.lbl_tiros.setText("Tiros: %d" % len(self.historial))
        self.lbl_total.setText("Total: $0")
        for n in cola:
            tag = "rojo" if n in ROJO else ("negro" if n in NEGRO else "verde")
            self._agregar_historial(n, tag)
        for n in cola:
            self.juego_count[n] = self.juego_count.get(n, 0) + 1
        heredados = []
        for n, c in self.juego_count.items():
            if c >= 2:
                self.estrategia[n] = self.unidad
                self._marcar(n)
                heredados.append(str(n))
        self.fase = "jug" if self.estrategia else "obs"
        self._actualizar_repetidos()
        self._cinta()
        self._log("Nueva ronda rápida: conservados %d números. "
                  "Repetidos heredados: %s." %
                  (len(cola), ", ".join(heredados) or "ninguno"))

    # ---------- paneles dinámicos ----------

    def _actualizar_repetidos(self):
        repetidos = [(n, c) for n, c in self.juego_count.items() if c >= 2]
        repetidos.sort(key=lambda x: (-x[1], x[0]))
        self.txt_repetidos.clear()
        if repetidos:
            for n, c in repetidos:
                sufijo = "  <- ¡3ª!" if n in self.estrategia and c >= 3 else ""
                self._insertar_pane(self.txt_repetidos,
                                    "%3d  ->  %d veces%s" % (n, c, sufijo), TEXTO)
        else:
            self._insertar_pane(self.txt_repetidos, "Ninguno todavía", TEXTO)

    def _cinta(self):
        if self.fase == "obs":
            texto = "OBSERVANDO (giro %d)" % self.juego_tiros
            if self.juego_tiros >= 9 and self.juego_tiros <= 20:
                texto = "OBSERVANDO · zona amarilla (giro %d)" % self.juego_tiros
            color = ORO if self.juego_tiros < 9 else "#ff5252"
            self.lbl_fase.setText(texto)
            self.lbl_fase.setStyleSheet("color:%s;" % color)
        else:
            self.lbl_fase.setText("JUGANDO")
            self.lbl_fase.setStyleSheet("color:#4caf50;")

        self.lbl_apostados.setText(", ".join(str(k) for k in self.estrategia) or "—")
        limite = self._limite_perdida()
        if limite is None:
            self.lbl_perdida.setText("-%d ficha(s)" % self.perdida)
            self.lbl_perdida.setStyleSheet("color:%s;" % TEXTO)
        else:
            self.lbl_perdida.setText("-%d / límite -%d" % (self.perdida, limite))
            if self.perdida >= limite * 0.75:
                self.lbl_perdida.setStyleSheet("color:#ff5252;")
            else:
                self.lbl_perdida.setStyleSheet("color:%s;" % TEXTO)
        self.lbl_unidad.setText("%d ficha(s)" % self.unidad)
        self.lbl_saldo.setText("$%d" % (self.saldo + self.beneficio))
        self.lbl_benef.setText("+$%d" % self.beneficio)

    def _insertar_pane(self, pane, texto, color):
        cur = pane.textCursor()
        cur.movePosition(QTextCursor.End)
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        cur.insertText(texto + "\n", fmt)
        pane.setTextCursor(cur)

    def _agregar_historial(self, n, tag):
        color = {"rojo": "#ff6b6b", "negro": "#ffffff", "verde": "#4caf50"}[tag]
        cur = self.txt_historial.textCursor()
        cur.movePosition(QTextCursor.Start)
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        cur.insertText("%3d\n" % n, fmt)
        self.txt_historial.setTextCursor(cur)

    def _log(self, msj):
        self._insertar_pane(self.txt_log, msj, TEXTO)

    def _resaltar(self, loc):
        self.ultima_celda = loc
        self.mesa.update()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Ruleta 3 Repeticiones")
    app.setStyle("Fusion")
    w = RuletaApp()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()