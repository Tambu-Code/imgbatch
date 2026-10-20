from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QPushButton, QFileDialog,
    QLabel, QSpinBox, QCheckBox, QComboBox, QLineEdit,
    QProgressBar, QMessageBox, QInputDialog,
)
from core.processor import FORMATS
from core.profiles import load_profiles, save_profile, delete_profile
from core.settings import Settings
from core.watermark import POSITIONS
from gui.worker import Worker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ImgBatch")
        self.setMinimumSize(800, 500)

        self.output_dir = ""
        self.logo_path = ""
        self.worker = None

        central = QWidget()
        layout = QVBoxLayout()

        # Profili
        profile_row = QHBoxLayout()
        self.profile_combo = QComboBox()
        self.profile_load_button = QPushButton("Carica")
        self.profile_load_button.clicked.connect(self.load_selected_profile)
        self.profile_save_button = QPushButton("Salva come...")
        self.profile_save_button.clicked.connect(self.save_current_profile)
        self.profile_delete_button = QPushButton("Elimina")
        self.profile_delete_button.clicked.connect(self.delete_selected_profile)
        profile_row.addWidget(QLabel("Profilo:"))
        profile_row.addWidget(self.profile_combo, 1)
        profile_row.addWidget(self.profile_load_button)
        profile_row.addWidget(self.profile_save_button)
        profile_row.addWidget(self.profile_delete_button)

        # Lista file
        self.file_list = QListWidget()
        self.add_button = QPushButton("Aggiungi immagini")
        self.add_button.clicked.connect(self.add_files)

        # Cartella di output
        output_row = QHBoxLayout()
        self.output_button = QPushButton("Cartella di output")
        self.output_button.clicked.connect(self.choose_output_dir)
        self.output_label = QLabel("Nessuna cartella selezionata")
        output_row.addWidget(self.output_button)
        output_row.addWidget(self.output_label, 1)

        # Opzioni di ridimensionamento
        resize_row = QHBoxLayout()
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 10000)
        self.width_spin.setValue(1920)
        self.width_spin.setSuffix(" px")
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 10000)
        self.height_spin.setValue(1080)
        self.height_spin.setSuffix(" px")
        self.keep_ratio = QCheckBox("Mantieni proporzioni")
        self.keep_ratio.setChecked(True)
        resize_row.addWidget(QLabel("Larghezza:"))
        resize_row.addWidget(self.width_spin)
        resize_row.addWidget(QLabel("Altezza:"))
        resize_row.addWidget(self.height_spin)
        resize_row.addWidget(self.keep_ratio)
        resize_row.addStretch()

        # Formato e qualità
        format_row = QHBoxLayout()
        self.format_combo = QComboBox()
        self.format_combo.addItems(list(FORMATS.keys()))
        self.format_combo.currentTextChanged.connect(self.update_quality_state)
        self.quality_spin = QSpinBox()
        self.quality_spin.setRange(1, 100)
        self.quality_spin.setValue(85)
        format_row.addWidget(QLabel("Formato:"))
        format_row.addWidget(self.format_combo)
        format_row.addWidget(QLabel("Qualità:"))
        format_row.addWidget(self.quality_spin)
        format_row.addStretch()

        # Watermark: testo e posizione
        wm_text_row = QHBoxLayout()
        self.wm_text_edit = QLineEdit()
        self.wm_text_edit.setPlaceholderText("Testo del watermark (vuoto = nessun testo)")
        self.wm_position_combo = QComboBox()
        self.wm_position_combo.addItems(POSITIONS)
        wm_text_row.addWidget(QLabel("Watermark:"))
        wm_text_row.addWidget(self.wm_text_edit, 1)
        wm_text_row.addWidget(self.wm_position_combo)

        # Watermark: opacità e dimensione del testo
        wm_style_row = QHBoxLayout()
        self.wm_opacity_spin = QSpinBox()
        self.wm_opacity_spin.setRange(0, 100)
        self.wm_opacity_spin.setValue(50)
        self.wm_opacity_spin.setSuffix(" %")
        self.wm_size_spin = QSpinBox()
        self.wm_size_spin.setRange(1, 30)
        self.wm_size_spin.setValue(5)
        self.wm_size_spin.setSuffix(" %")
        wm_style_row.addWidget(QLabel("Opacità (testo e logo):"))
        wm_style_row.addWidget(self.wm_opacity_spin)
        wm_style_row.addWidget(QLabel("Dimensione testo:"))
        wm_style_row.addWidget(self.wm_size_spin)
        wm_style_row.addStretch()

        # Logo: scelta file
        logo_row = QHBoxLayout()
        self.logo_button = QPushButton("Scegli logo")
        self.logo_button.clicked.connect(self.choose_logo)
        self.logo_label = QLabel("Nessun logo selezionato")
        self.logo_clear_button = QPushButton("Rimuovi logo")
        self.logo_clear_button.clicked.connect(self.clear_logo)
        logo_row.addWidget(self.logo_button)
        logo_row.addWidget(self.logo_label, 1)
        logo_row.addWidget(self.logo_clear_button)

        # Logo: posizione e dimensione
        logo_style_row = QHBoxLayout()
        self.logo_position_combo = QComboBox()
        self.logo_position_combo.addItems(POSITIONS)
        self.logo_size_spin = QSpinBox()
        self.logo_size_spin.setRange(1, 50)
        self.logo_size_spin.setValue(15)
        self.logo_size_spin.setSuffix(" %")
        logo_style_row.addWidget(QLabel("Posizione logo:"))
        logo_style_row.addWidget(self.logo_position_combo)
        logo_style_row.addWidget(QLabel("Larghezza logo:"))
        logo_style_row.addWidget(self.logo_size_spin)
        logo_style_row.addStretch()

        # Elabora e avanzamento
        self.run_button = QPushButton("Elabora")
        self.run_button.clicked.connect(self.process_files)
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        layout.addLayout(profile_row)
        layout.addWidget(self.file_list)
        layout.addWidget(self.add_button)
        layout.addLayout(output_row)
        layout.addLayout(resize_row)
        layout.addLayout(format_row)
        layout.addLayout(wm_text_row)
        layout.addLayout(wm_style_row)
        layout.addLayout(logo_row)
        layout.addLayout(logo_style_row)
        layout.addWidget(self.run_button)
        layout.addWidget(self.progress_bar)
        central.setLayout(layout)
        self.setCentralWidget(central)

        self.refresh_profiles()

    # ---------- impostazioni <-> widget ----------

    def read_settings(self):
        return Settings(
            width=self.width_spin.value(),
            height=self.height_spin.value(),
            keep_ratio=self.keep_ratio.isChecked(),
            fmt_name=self.format_combo.currentText(),
            quality=self.quality_spin.value(),
            wm_text=self.wm_text_edit.text(),
            wm_position=self.wm_position_combo.currentText(),
            wm_opacity=self.wm_opacity_spin.value(),
            wm_size=self.wm_size_spin.value(),
            logo_path=self.logo_path,
            logo_position=self.logo_position_combo.currentText(),
            logo_size=self.logo_size_spin.value(),
        )

    def apply_settings(self, s):
        self.width_spin.setValue(s.width)
        self.height_spin.setValue(s.height)
        self.keep_ratio.setChecked(s.keep_ratio)
        self.format_combo.setCurrentText(s.fmt_name)
        self.quality_spin.setValue(s.quality)
        self.wm_text_edit.setText(s.wm_text)
        self.wm_position_combo.setCurrentText(s.wm_position)
        self.wm_opacity_spin.setValue(s.wm_opacity)
        self.wm_size_spin.setValue(s.wm_size)
        self.logo_position_combo.setCurrentText(s.logo_position)
        self.logo_size_spin.setValue(s.logo_size)

        self.logo_path = s.logo_path
        if s.logo_path:
            self.logo_label.setText(Path(s.logo_path).name)
        else:
            self.logo_label.setText("Nessun logo selezionato")

        self.update_quality_state(self.format_combo.currentText())

    # ---------- profili ----------

    def refresh_profiles(self, select=None):
        self.profile_combo.clear()
        self.profile_combo.addItems(sorted(load_profiles()))
        if select:
            self.profile_combo.setCurrentText(select)

    def load_selected_profile(self):
        name = self.profile_combo.currentText()
        profiles = load_profiles()
        if name in profiles:
            self.apply_settings(profiles[name])

    def save_current_profile(self):
        name, ok = QInputDialog.getText(self, "Salva profilo", "Nome del profilo:")
        name = name.strip()
        if not ok or not name:
            return
        save_profile(name, self.read_settings())
        self.refresh_profiles(select=name)

    def delete_selected_profile(self):
        name = self.profile_combo.currentText()
        if not name:
            return
        reply = QMessageBox.question(
            self, "ImgBatch", f"Eliminare il profilo «{name}»?"
        )
        if reply == QMessageBox.StandardButton.Yes:
            delete_profile(name)
            self.refresh_profiles()

    # ---------- file, cartelle, logo ----------

    def add_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Seleziona immagini",
            "",
            "Immagini (*.png *.jpg *.jpeg *.webp)",
        )
        existing = {
            self.file_list.item(i).text()
            for i in range(self.file_list.count())
        }
        new_paths = [p for p in paths if p not in existing]
        self.file_list.addItems(new_paths)

    def choose_output_dir(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Scegli la cartella di output"
        )
        if folder:
            self.output_dir = folder
            self.output_label.setText(folder)

    def choose_logo(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleziona il logo",
            "",
            "Immagini (*.png *.webp *.jpg *.jpeg)",
        )
        if path:
            self.logo_path = path
            self.logo_label.setText(Path(path).name)

    def clear_logo(self):
        self.logo_path = ""
        self.logo_label.setText("Nessun logo selezionato")

    def update_quality_state(self, name):
        self.quality_spin.setEnabled(name != "PNG")

    # ---------- elaborazione ----------

    def process_files(self):
        if self.file_list.count() == 0:
            QMessageBox.warning(self, "ImgBatch", "Aggiungi almeno un'immagine.")
            return
        if not self.output_dir:
            QMessageBox.warning(self, "ImgBatch", "Scegli la cartella di output.")
            return

        paths = [
            self.file_list.item(i).text()
            for i in range(self.file_list.count())
        ]

        self.progress_bar.setMaximum(len(paths))
        self.progress_bar.setValue(0)
        self.run_button.setEnabled(False)

        self.worker = Worker(paths, self.output_dir, self.read_settings())
        self.worker.progress.connect(self.on_progress)
        self.worker.finished_batch.connect(self.on_finished)
        self.worker.start()

    def on_progress(self, done, total):
        self.progress_bar.setValue(done)

    def on_finished(self, done, errors):
        self.run_button.setEnabled(True)

        message = f"Elaborate {done} immagini."
        if errors:
            message += "\n\nErrori:\n" + "\n".join(errors)
        QMessageBox.information(self, "ImgBatch", message)