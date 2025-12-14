from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Signal
from src.utils.icons import IconGenerator
import sys

class SystemTray(QSystemTrayIcon):
    show_window_signal = Signal()
    quit_signal = Signal()
    connect_signal = Signal(str)
    disconnect_signal = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setToolTip("WireGuard GUI")

        # Initial Icon (Disconnected)
        self.setIcon(IconGenerator.get_status_icon("disconnected"))

        # Create context menu
        self.menu = QMenu()

        self.status_action = self.menu.addAction("Status: Disconnected")
        self.status_action.setEnabled(False)
        self.menu.addSeparator()

        self.show_action = self.menu.addAction("Show Window")
        self.show_action.triggered.connect(self.show_window_signal.emit)

        self.menu.addSeparator()
        self.quit_action = self.menu.addAction("Quit")
        self.quit_action.triggered.connect(self.quit_signal.emit)

        self.setContextMenu(self.menu)

    def update_status(self, connected: bool, profile_name: str = ""):
        if connected:
            self.setToolTip(f"WireGuard GUI: Connected to {profile_name}")
            self.status_action.setText(f"Connected: {profile_name}")
            self.setIcon(IconGenerator.get_status_icon("connected"))
        else:
            self.setToolTip("WireGuard GUI: Disconnected")
            self.status_action.setText("Disconnected")
            self.setIcon(IconGenerator.get_status_icon("disconnected"))
