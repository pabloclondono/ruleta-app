import sys

from PySide6.QtWidgets import QApplication, QTabWidget, QVBoxLayout, QWidget

from ruleta.constantes import BASE_W, BASE_H, FONDO, ORO, SUB
from ruleta.controladores.controlador_3reps import ControladorTresReps
from ruleta.controladores.controlador_corners import ControladorCorners


class ControladorPrincipal(QWidget):
    """Ventana contenedora con las pestañas de las estrategias."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ruleta — Seguimiento de estrategias")
        self.setMinimumSize(660, 540)

        self.tab_3reps = ControladorTresReps()
        self.tab_corners = ControladorCorners()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(
            "QTabWidget::pane{border:1px solid #2c2c2c;background:%s;}"
            "QTabBar::tab{background:#1a1a1a;color:%s;padding:8px 18px;"
            "border:1px solid #2c2c2c;border-bottom:none;}"
            "QTabBar::tab:selected{background:#2c2c2c;color:%s;}"
            "QTabBar::tab:hover{background:#242424;}"
            % (FONDO, SUB, ORO))
        self.tabs.addTab(self.tab_3reps.vista, "3 Repeticiones")
        self.tabs.addTab(self.tab_corners.vista, "12 Corners")
        layout.addWidget(self.tabs)

        self.resize(BASE_W, BASE_H)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    ventana = ControladorPrincipal()
    ventana.show()
    sys.exit(app.exec())