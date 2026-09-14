from PySide6.QtCore import Qt, QPointF, QRectF, Signal
from PySide6.QtGui import QColor, QPainter, QPen, QTextOption
from PySide6.QtWidgets import QWidget

from ruleta.constantes import (AZUL, COLOR_FICHA, CORNERES, FILAS, FONDO,
                               GRIS, NEGRO_BG, ROJO_BG, ROJO, TEXTO, ORO,
                               VERDE, TEXTO_FICHA)


class MesaWidget(QWidget):
    """Tablero europeo (réplica para las estrategias).

    Solo pinta: lee los datos directamente de la vista propietaria
    (``owner``) en cada repintado.
    """

    apuesta = Signal(str, bool)

    def __init__(self, owner):
        super().__init__()
        self.owner = owner
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

        for i, (texto, loc) in enumerate([("1-12", "dozen1"),
                                          ("13-24", "dozen2"),
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

            if loc == "0" or loc.lstrip("-").isdigit():
                p.setFont(self.owner._fuentes["num"])
                p.setPen(QColor("#f2f2f2"))
                r_num = QRectF(rect.left(), rect.top() + 2, rect.width(),
                               rect.height() * 0.56)
                p.drawText(r_num, texto, opt)
                fm = p.fontMetrics()
                hr = fm.height()
                if loc in self.owner.bets:
                    p.setFont(self.owner._fuentes["mon"])
                    fm2 = p.fontMetrics()
                    r_m = QRectF(rect.left(), rect.bottom() - 2 * hr - 2,
                                 rect.width(), hr)
                    p.setPen(QColor(ORO))
                    p.drawText(r_m, "$%d" % self.owner.bets[loc], opt)
                    hr2 = fm2.height()
                    if int(loc) in self.owner.estrategia:
                        p.setFont(self.owner._fuentes["est"])
                        fm3 = p.fontMetrics()
                        r_e = QRectF(rect.left(), rect.bottom() - hr2 - 2,
                                     rect.width(), hr2)
                        p.setPen(QColor("#ffd700"))
                        p.drawText(r_e, "R%d" % self.owner.estrategia[int(loc)],
                                   opt)
                else:
                    if int(loc) in self.owner.estrategia:
                        p.setFont(self.owner._fuentes["est"])
                        fm3 = p.fontMetrics()
                        hr3 = fm3.height()
                        r_e = QRectF(rect.left(), rect.bottom() - hr3 - 2,
                                     rect.width(), hr3)
                        p.setPen(QColor("#ffd700"))
                        p.drawText(r_e, "R%d" % self.owner.estrategia[int(loc)],
                                   opt)
            else:
                p.setFont(self.owner._fuentes["num"])
                p.setPen(QColor("#f2f2f2"))
                p.drawText(rect, texto, opt)

            if self.owner.ultima_celda == loc:
                p.setPen(QPen(QColor(ORO), 3))
                p.drawRect(rect.adjusted(1, 1, -1, -1))

            if loc in getattr(self.owner, "resaltado", ()):
                p.setPen(QPen(QColor("#ffffff"), 3))
                p.drawRect(rect.adjusted(2, 2, -2, -2))

        w, h = self.width(), self.height()
        m = max(3, int(round(w * 0.006)))
        ax, ay = m, m
        cw = (w - 2 * m) / 14.0
        rh = (h - 2 * m) / 5.0
        self._dibujar_fichas_corner(p, ax, ay, cw, rh)

    def _punto_corner(self, cid, ax, ay, cw, rh):
        """Intersección de la rejilla donde se sitúa un corner."""
        if cid == "C0":
            return QPointF(ax + 1 * cw, ay + 2 * rh)
        cols = []
        fils = []
        for n in CORNERES[cid]:
            for r, fila in enumerate(FILAS):
                if n in fila:
                    fils.append(r)
                    cols.append(1 + fila.index(n))
        return QPointF(ax + max(cols) * cw, ay + max(fils) * rh)

    def _dibujar_fichas_corner(self, p, ax, ay, cw, rh):
        p.setRenderHint(QPainter.Antialiasing, True)
        moneda = getattr(self.owner, "chip", 500) or 500
        opt = QTextOption(Qt.AlignCenter)
        r = min(cw, rh) * 0.34
        for cid, monto in getattr(self.owner, "apuestas_corner", {}).items():
            c = self._punto_corner(cid, ax, ay, cw, rh)
            rect = QRectF(c.x() - r, c.y() - r, 2 * r, 2 * r)
            p.setPen(QPen(QColor(ORO), 3 if cid == self.owner.ultimo_corner
                          else 2))
            p.setBrush(QColor(COLOR_FICHA.get(moneda, "#333333")))
            p.drawEllipse(rect)
            if cid == self.owner.ultimo_corner:
                p.setPen(QPen(QColor("#ffffff"), 2))
                p.drawEllipse(rect.adjusted(-3, -3, 3, 3))
            p.setFont(self.owner._fuentes["chip"])
            p.setPen(QColor(TEXTO_FICHA.get(moneda, "#ffffff")))
            p.drawText(rect, "$%d" % monto, opt)

    def mousePressEvent(self, e):
        pos = e.position()
        for rect, loc in self._cajas:
            if rect.contains(pos):
                self.apuesta.emit(loc, e.button() == Qt.MouseButton.RightButton)
                return