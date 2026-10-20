from PyQt6.QtCore import QThread, pyqtSignal
from core.processor import process_image


class Worker(QThread):
    progress = pyqtSignal(int, int)         # (fatte, totali)
    finished_batch = pyqtSignal(int, list)  # (elaborate, errori)

    def __init__(self, paths, output_dir, settings):
        super().__init__()
        self.paths = paths
        self.output_dir = output_dir
        self.settings = settings

    def run(self):
        done = 0
        errors = []
        total = len(self.paths)

        for i, path in enumerate(self.paths, start=1):
            try:
                process_image(path, self.output_dir, self.settings)
                done += 1
            except Exception as e:
                errors.append(f"{path}: {e}")
            self.progress.emit(i, total)

        self.finished_batch.emit(done, errors)