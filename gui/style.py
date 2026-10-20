import tempfile
from pathlib import Path
from string import Template

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor, QPainter, QPalette, QPen, QPixmap, QPolygonF

THEMES = {
    "chiaro": {
        "bg": "#F6F7FB",
        "surface": "#FFFFFF",
        "border": "#E3E6EF",
        "text": "#2D3142",
        "muted": "#9AA0B5",
        "accent": "#6C8EF5",
        "accent_hover": "#5A7BE0",
        "accent_pressed": "#4A69C8",
        "disabled_bg": "#C9CEDD",
        "disabled_text": "#F6F7FB",
        "selected": "#E4EAFE",
        "track": "#E3E6EF",
        "spin_btn": "#EEF1F9",
        "spin_btn_hover": "#DFE5F6",
        "arrow": "#6B7391",
    },
    "scuro": {
        "bg": "#1E1F2B",
        "surface": "#2A2C3B",
        "border": "#3A3D52",
        "text": "#E6E8F0",
        "muted": "#7C8099",
        "accent": "#4F67D6",
        "accent_hover": "#6079E8",
        "accent_pressed": "#3F54B5",
        "disabled_bg": "#3A3D52",
        "disabled_text": "#7C8099",
        "selected": "#34395A",
        "track": "#3A3D52",
        "spin_btn": "#363A52",
        "spin_btn_hover": "#454A68",
        "arrow": "#C5CAE0",
    },
}

QSS_TEMPLATE = """
QWidget {
    color: $text;
    font-family: "Segoe UI";
    font-size: 10pt;
}

QMainWindow {
    background: $bg;
}

QLabel {
    background: transparent;
}

QListWidget {
    background: $surface;
    border: 1px solid $border;
    border-radius: 12px;
    padding: 6px;
}
QListWidget::item {
    padding: 6px;
    border-radius: 6px;
}
QListWidget::item:selected {
    background: $selected;
    color: $text;
}

QPushButton {
    background: $accent;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 8px 16px;
}
QPushButton:hover {
    background: $accent_hover;
}
QPushButton:pressed {
    background: $accent_pressed;
}
QPushButton:disabled {
    background: $disabled_bg;
    color: $disabled_text;
}

QLineEdit, QSpinBox, QComboBox {
    background: $surface;
    border: 1px solid $border;
    border-radius: 8px;
    padding: 5px 8px;
}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 1px solid $accent;
}

QSpinBox {
    padding-right: 28px;
}
QSpinBox::up-button {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    background: $spin_btn;
    border: none;
    border-radius: 6px;
}
QSpinBox::down-button {
    subcontrol-origin: padding;
    subcontrol-position: bottom right;
    width: 20px;
    background: $spin_btn;
    border: none;
    border-radius: 6px;
}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background: $spin_btn_hover;
}
QSpinBox::up-button:pressed, QSpinBox::down-button:pressed {
    background: $accent;
}
QSpinBox::up-arrow {
    image: url("$up_icon");
    width: 10px;
    height: 10px;
}
QSpinBox::down-arrow {
    image: url("$down_icon");
    width: 10px;
    height: 10px;
}

QComboBox {
    padding-right: 28px;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox::down-arrow {
    image: url("$down_icon");
    width: 10px;
    height: 10px;
}
QComboBox QAbstractItemView {
    background: $surface;
    border: 1px solid $border;
    selection-background-color: $selected;
    selection-color: $text;
}

QProgressBar {
    background: $track;
    border: none;
    border-radius: 8px;
    height: 16px;
    text-align: center;
}
QProgressBar::chunk {
    background: $accent;
    border-radius: 8px;
}
"""


def _draw_arrow(path, color, up):
    size = 12
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(QColor(color))
    pen.setWidthF(1.8)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)

    if up:
        points = [QPointF(2.5, 7.5), QPointF(6, 4), QPointF(9.5, 7.5)]
    else:
        points = [QPointF(2.5, 4.5), QPointF(6, 8), QPointF(9.5, 4.5)]
    painter.drawPolyline(QPolygonF(points))
    painter.end()

    pixmap.save(str(path))


def build_icons(name, color):
    folder = Path(tempfile.gettempdir()) / "imgbatch_icons"
    folder.mkdir(exist_ok=True)
    up = folder / f"up_{name}.png"
    down = folder / f"down_{name}.png"
    _draw_arrow(up, color, up=True)
    _draw_arrow(down, color, up=False)
    return up.as_posix(), down.as_posix()


def build_palette(c):
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(c["bg"]))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(c["text"]))
    palette.setColor(QPalette.ColorRole.Base, QColor(c["surface"]))
    palette.setColor(QPalette.ColorRole.Text, QColor(c["text"]))
    palette.setColor(QPalette.ColorRole.Button, QColor(c["surface"]))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(c["text"]))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(c["accent"]))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("white"))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(c["muted"]))
    return palette


def apply_theme(app, name):
    colors = dict(THEMES[name])
    colors["up_icon"], colors["down_icon"] = build_icons(name, colors["arrow"])

    app.setStyle("Fusion")
    app.setPalette(build_palette(colors))
    app.setStyleSheet(Template(QSS_TEMPLATE).substitute(colors))