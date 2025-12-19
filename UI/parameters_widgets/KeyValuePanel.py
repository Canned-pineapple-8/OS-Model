from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QSizePolicy
from PyQt6.QtCore import Qt

MONO_FONT = "Cascadia Mono"


class KeyValuePanel(QWidget):
    """
    Панель "ключ: значение" в виде карточек.
    """
    def __init__(self, pairs: list[tuple[str,str]] | None = None, parent=None):
        super().__init__(parent)
        self._grid = QGridLayout()
        self._grid.setSpacing(6)
        self._grid.setContentsMargins(6, 6, 6, 6)
        self.setLayout(self._grid)
        self._rows = 0
        if pairs:
            for k, v in pairs:
                self.set(k, v)

    def set(self, key: str, value: str):
        for r in range(self._rows):
            key_lbl = self._grid.itemAtPosition(r, 0).widget()
            if key_lbl and key_lbl.text() == f"{key}:":
                val_lbl = self._grid.itemAtPosition(r, 1).widget()
                if val_lbl:
                    val_lbl.setText(str(value))
                    return
        key_lbl = QLabel(f"{key}:")
        key_lbl.setProperty("role", "key")
        key_lbl.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        key_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        val_lbl = QLabel(str(value))
        val_lbl.setProperty("role", "value")
        val_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self._grid.addWidget(key_lbl, self._rows, 0)
        self._grid.addWidget(val_lbl, self._rows, 1)
        self._rows += 1

    def bulk_set(self, mapping: dict):
        for k, v in mapping.items():
            self.set(k, v)

    def clear(self):
        while self._grid.count():
            item = self._grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self._rows = 0
