from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import (
    QFrame, QLabel, QMessageBox, QPlainTextEdit, QPushButton, QVBoxLayout,
    QWidget,
)

from ruleta.constantes import FONDO, ORO, PANEL, TEXTO, _claro


class BaseTab(QWidget):
    """Helpers comunes de las vistas (fuentes, etiquetas, botones...)."""

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: %s;" % FONDO)
        self._s = 1.0
        self._wfont = []
        self._crear_fuentes()

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
        s = min(w / 1000.0, h / 720.0)
        s = max(0.55, min(1.8, s))
        if abs(s - self._s) < 0.03:
            return
        self._s = s
        self._aplicar_fuentes()
        if hasattr(self, "mesa"):
            self.mesa.update()
        if hasattr(self, "chips"):
            self.chips.update()

    # ---------- helpers de widgets ----------

    def _etiqueta(self, texto, color, key):
        lbl = QLabel(texto)
        lbl.setStyleSheet("color:%s;" % color)
        self._reg_fuente(lbl, key)
        return lbl

    def _luz(self, encendida_color, texto):
        lbl = QLabel()
        lbl.setFixedSize(15, 15)
        lbl._enc = encendida_color
        lbl.setToolTip(texto)
        self._set_luz(lbl, False)
        return lbl

    def _set_luz(self, luz, encendida):
        luz.setStyleSheet(
            "QLabel{background:%s;border-radius:7px;border:1px solid #2c2c2c;}"
            % (luz._enc if encendida else "#2e2e2e"))

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

    def _preguntar(self, titulo, mensaje):
        r = QMessageBox.question(self, titulo, mensaje,
                                 QMessageBox.StandardButton.Yes |
                                 QMessageBox.StandardButton.No)
        return r == QMessageBox.StandardButton.Yes

    # ---------- paneles dinámicos ----------

    def _insertar_pane(self, pane, texto, color):
        cur = pane.textCursor()
        cur.movePosition(QTextCursor.End)
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        cur.insertText(texto + "\n", fmt)
        pane.setTextCursor(cur)

    def _agregar_historial(self, n, tag):
        color = {"rojo": "#ff6b6b", "negro": "#ffffff",
                 "verde": "#4caf50"}[tag]
        cur = self.txt_historial.textCursor()
        cur.movePosition(QTextCursor.Start)
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        cur.insertText("%3d\n" % n, fmt)
        self.txt_historial.setTextCursor(cur)

    def _log(self, msj):
        self._insertar_pane(self.txt_log, msj, TEXTO)