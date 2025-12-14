from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QCoreApplication
from pathlib import Path
from src.backend.profiles import ProfileManager

class AddProfileDialog(QDialog):
    def __init__(self, profile_manager: ProfileManager, parent=None):
        super().__init__(parent)
        self.profile_manager = profile_manager
        self.setWindowTitle(self.tr("Add WireGuard Tunnel"))
        self.resize(500, 400)
        self.setStyleSheet("background-color: #2D2D2D; color: white;")

        layout = QVBoxLayout(self)

        # Name
        layout.addWidget(QLabel(self.tr("Tunnel Name:")))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(self.tr("e.g. wg0"))
        self.name_edit.setStyleSheet("padding: 5px; border: 1px solid #555;")
        layout.addWidget(self.name_edit)

        # Import Button
        import_btn = QPushButton(self.tr("Import from File..."))
        import_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 5px; border-radius: 4px;")
        import_btn.clicked.connect(self.import_from_file)
        layout.addWidget(import_btn)

        # Config Content
        layout.addWidget(QLabel(self.tr("Configuration:")))
        self.config_edit = QTextEdit()
        self.config_edit.setPlaceholderText("[Interface]\nPrivateKey = ...\nAddress = ...\n\n[Peer]\nPublicKey = ...\nEndpoint = ...")
        self.config_edit.setStyleSheet("border: 1px solid #555; font-family: monospace;")
        layout.addWidget(self.config_edit)

        # Buttons
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton(self.tr("Cancel"))
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("background-color: #757575; color: white; padding: 8px; border-radius: 4px;")

        save_btn = QPushButton(self.tr("Save Tunnel"))
        save_btn.clicked.connect(self.save_profile)
        save_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px; border-radius: 4px;")

        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def import_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, self.tr("Import WireGuard Config"), "", self.tr("Conf Files (*.conf);;All Files (*)"))
        if file_path:
            try:
                with open(file_path, "r") as f:
                    content = f.read()
                    self.config_edit.setText(content)

                # Auto-fill name if empty
                if not self.name_edit.text():
                    self.name_edit.setText(Path(file_path).stem)
            except Exception as e:
                QMessageBox.critical(self, self.tr("Error"), self.tr("Failed to read file: {0}").format(e))

    def save_profile(self):
        name = self.name_edit.text().strip()
        content = self.config_edit.toPlainText().strip()

        if not name:
            QMessageBox.warning(self, self.tr("Validation"), self.tr("Please enter a tunnel name."))
            return

        if not content:
            QMessageBox.warning(self, self.tr("Validation"), self.tr("Configuration content cannot be empty."))
            return

        # Check if exists
        if (self.profile_manager.get_profile_path(name)).exists():
             ret = QMessageBox.warning(self, self.tr("Overwrite?"), self.tr("Profile '{0}' already exists. Overwrite?").format(name), QMessageBox.Yes | QMessageBox.No)
             if ret == QMessageBox.No:
                 return

        if self.profile_manager.create_profile(name, content):
            self.accept()
        else:
            QMessageBox.critical(self, self.tr("Error"), self.tr("Failed to save profile. Check permissions."))
