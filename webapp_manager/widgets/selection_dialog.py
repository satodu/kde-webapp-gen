from typing import List, Optional, Tuple
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPushButton, QDialogButtonBox, QWidget
)
from webapp_manager.i18n import tr


class WebappSelectionDialog(QDialog):
    """Checkable list used to pick which webapps to export or import."""

    def __init__(
        self,
        title: str,
        message: str,
        entries: List[Tuple[str, str]],
        extra_widget: Optional[QWidget] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(520, 480)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        lbl = QLabel(message)
        lbl.setWordWrap(True)
        layout.addWidget(lbl)

        self.list_widget = QListWidget()
        for label, tooltip in entries:
            item = QListWidgetItem(label)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)
            if tooltip:
                item.setToolTip(tooltip)
            self.list_widget.addItem(item)
        self.list_widget.itemChanged.connect(self.update_ok_state)
        layout.addWidget(self.list_widget)

        toggle_row = QHBoxLayout()
        btn_all = QPushButton(tr("selection.check_all"))
        btn_all.clicked.connect(lambda: self.set_all(Qt.CheckState.Checked))
        btn_none = QPushButton(tr("selection.uncheck_all"))
        btn_none.clicked.connect(lambda: self.set_all(Qt.CheckState.Unchecked))
        toggle_row.addWidget(btn_all)
        toggle_row.addWidget(btn_none)
        toggle_row.addStretch()
        layout.addLayout(toggle_row)

        if extra_widget:
            layout.addWidget(extra_widget)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

        self.update_ok_state()

    def set_all(self, state: Qt.CheckState) -> None:
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setCheckState(state)

    def update_ok_state(self) -> None:
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(bool(self.checked_indexes()))

    def checked_indexes(self) -> List[int]:
        return [
            i for i in range(self.list_widget.count())
            if self.list_widget.item(i).checkState() == Qt.CheckState.Checked
        ]
