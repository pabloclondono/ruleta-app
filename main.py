import sys

from PySide6.QtWidgets import QApplication

from ruleta.controladores.principal import ControladorPrincipal


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    ventana = ControladorPrincipal()
    ventana.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()