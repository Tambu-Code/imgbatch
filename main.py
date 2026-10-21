import sys
from pathlib import Path

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from gui.main_window import MainWindow
from gui.style import apply_theme


def resource_path(relative):
    """Percorso di un file incluso, sia da codice sia dentro l'.exe."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / relative


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(resource_path("assets/icon.ico"))))
    apply_theme(app, "scuro")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())