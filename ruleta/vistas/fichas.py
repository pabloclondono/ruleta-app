from PySide6.QtCore import Qt, QRectF, Signal
from PySide6.QtGui import QColor, QPainter, QPen, QTextOption
from PySide6.QtWidgets import QWidget

from ruleta.constantes import (COLOR_FICHA, FONDO, ORO, TEXTO_FICHA,
                               VALORES_FICHAS)


class ChipBar(QWidget):
    """Barra de fichas para apostar manualmente (estrategia 3 Repeticiones)."""

    ficha = Signal(int)

    def __init__(self, owner):
        super().__init__()
        self.owner = owner
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
            sel = (self.owner.chip == valor)
            p.setPen(QPen(QColor(ORO if sel else "#5a5a5a"), 3 if sel else 2))
            p.setBrush(QColor(COLOR_FICHA[valor]))
            p.drawEllipse(QRectF(cx - r, cy - r, 2 * r, 2 * r))
            p.setFont(self.owner._fuentes["chip"])
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
                self.ficha.emit(valor)
                return