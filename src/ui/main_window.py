from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QListWidget, QListWidgetItem,
    QStackedWidget, QFrame, QCheckBox, QLineEdit, QComboBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QAction
from src.backend.wireguard import WireGuardService
from src.backend.profiles import ProfileManager
from src.backend.settings import SettingsManager
from src.backend.backup import NetworkBackupManager
from src.utils.paths import get_assets_dir

class MainWindow(QMainWindow):
    connect_signal = Signal(str)
    disconnect_signal = Signal(str)

    def __init__(self, wg_service: WireGuardService, profile_manager: ProfileManager, settings_manager: SettingsManager, backup_manager: NetworkBackupManager):
        super().__init__()
        self.wg_service = wg_service
        self.profile_manager = profile_manager
        self.settings_manager = settings_manager
        self.backup_manager = backup_manager

        self.setWindowTitle("WireGuard GUI")
        self.resize(900, 600)

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main Layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet("background-color: #2D2D2D; color: white;")
        sidebar_layout = QVBoxLayout(self.sidebar)

        # Profile List
        self.profile_list = QListWidget()
        self.profile_list.setStyleSheet("""
            QListWidget { border: none; background: transparent; }
            QListWidget::item { padding: 10px; }
            QListWidget::item:selected { background-color: #3D3D3D; }
        """)
        self.profile_list.itemClicked.connect(self.on_profile_selected)
        sidebar_layout.addWidget(QLabel("PROFILES"))
        sidebar_layout.addWidget(self.profile_list)

        # Add Profile Button
        add_btn = QPushButton("+ Add Tunnel")
        add_btn.setStyleSheet("border: 1px solid #555; padding: 5px; border-radius: 4px;")
        sidebar_layout.addWidget(add_btn)

        # Settings Button (in Sidebar)
        settings_btn = QPushButton("⚙ Settings")
        settings_btn.setStyleSheet("border: 1px solid #555; padding: 5px; border-radius: 4px; margin-top: 10px;")
        settings_btn.clicked.connect(self.show_settings)
        sidebar_layout.addWidget(settings_btn)

        main_layout.addWidget(self.sidebar)

        # Content Area
        self.content_area = QStackedWidget()
        self.content_area.setStyleSheet("background-color: #1E1E1E; color: white;")
        main_layout.addWidget(self.content_area)

        # Default View (No profile selected)
        self.no_profile_view = QLabel("Select a tunnel to view details")
        self.no_profile_view.setAlignment(Qt.AlignCenter)
        self.content_area.addWidget(self.no_profile_view)

        # Profile Detail View
        self.detail_view = ProfileDetailView()
        self.detail_view.connect_btn.clicked.connect(self.on_connect_clicked)
        self.detail_view.disconnect_btn.clicked.connect(self.on_disconnect_clicked)
        self.content_area.addWidget(self.detail_view)

        # Settings View
        self.settings_view = SettingsView(self.settings_manager, self.backup_manager)
        self.content_area.addWidget(self.settings_view)

        self.refresh_profiles()

    def refresh_profiles(self):
        self.profile_list.clear()
        profiles = self.profile_manager.list_profiles()
        for p in profiles:
            item = QListWidgetItem(p)
            self.profile_list.addItem(item)

    def on_profile_selected(self, item):
        profile_name = item.text()
        self.detail_view.set_profile(profile_name)

        # Update status in UI
        status = self.wg_service.get_status(profile_name)
        self.detail_view.set_status(status.get("status", "disconnected"))

        self.content_area.setCurrentWidget(self.detail_view)

    def show_settings(self):
        self.content_area.setCurrentWidget(self.settings_view)

    def on_connect_clicked(self):
        profile = self.detail_view.current_profile
        if profile:
            self.connect_signal.emit(profile)
            self.detail_view.set_status("connecting")

    def on_disconnect_clicked(self):
        profile = self.detail_view.current_profile
        if profile:
            self.disconnect_signal.emit(profile)
            self.detail_view.set_status("disconnecting")

class ProfileDetailView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        self.name_label = QLabel("Profile Name")
        self.name_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(self.name_label)

        self.status_label = QLabel("Status: Disconnected")
        layout.addWidget(self.status_label)

        self.stats_label = QLabel("Data: 0 B received, 0 B sent")
        layout.addWidget(self.stats_label)

        layout.addStretch()

        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; color: white; border: none;
                padding: 10px 20px; border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336; color: white; border: none;
                padding: 10px 20px; border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #da190b; }
        """)

        self.disconnect_btn.hide()

        layout.addWidget(self.connect_btn)
        layout.addWidget(self.disconnect_btn)

        self.current_profile = None

    def set_profile(self, name):
        self.current_profile = name
        self.name_label.setText(name)

    def set_status(self, status):
        self.status_label.setText(f"Status: {status.title()}")
        if status == "connected":
            self.connect_btn.hide()
            self.disconnect_btn.show()
            self.status_label.setStyleSheet("color: #4CAF50;")
        else:
            self.connect_btn.show()
            self.disconnect_btn.hide()
            if status == "disconnected":
                self.status_label.setStyleSheet("color: #9E9E9E;")
            elif status == "error":
                self.status_label.setStyleSheet("color: #f44336;")

class SettingsView(QWidget):
    def __init__(self, settings_manager: SettingsManager, backup_manager: NetworkBackupManager):
        super().__init__()
        self.settings_manager = settings_manager
        self.backup_manager = backup_manager

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        layout.addWidget(QLabel("Settings"))

        # Start on Boot
        self.boot_check = QCheckBox("Start on Boot")
        self.boot_check.setChecked(self.settings_manager.get("start_on_boot", False))
        self.boot_check.stateChanged.connect(lambda s: self.settings_manager.set("start_on_boot", bool(s)))
        layout.addWidget(self.boot_check)

        # Kill Switch
        self.kill_check = QCheckBox("Kill Switch (Block traffic if VPN drops)")
        self.kill_check.setChecked(self.settings_manager.get("kill_switch", False))
        self.kill_check.stateChanged.connect(lambda s: self.settings_manager.set("kill_switch", bool(s)))
        layout.addWidget(self.kill_check)

        layout.addSpacing(20)

        # Network Backup Section
        layout.addWidget(QLabel("Network Backup & Restore"))

        self.backup_btn = QPushButton("Create Network Backup")
        self.backup_btn.clicked.connect(self.create_backup)
        self.backup_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 8px; border-radius: 4px;")
        layout.addWidget(self.backup_btn)

        self.restore_btn = QPushButton("Restore Last Backup")
        self.restore_btn.clicked.connect(self.restore_backup)
        self.restore_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 8px; border-radius: 4px;")
        layout.addWidget(self.restore_btn)

    def create_backup(self):
        backup_path = self.backup_manager.create_backup()
        if backup_path:
            QMessageBox.information(self, "Backup", f"Backup created at:\n{backup_path}")
        else:
            QMessageBox.critical(self, "Backup Error", "Failed to create backup. Check logs/permissions.")

    def restore_backup(self):
        backups = self.backup_manager.list_backups()
        if not backups:
             QMessageBox.information(self, "Restore", "No backups found.")
             return

        # Just restore the latest for now (Simplicity)
        latest = backups[0]
        ret = QMessageBox.warning(self, "Restore", f"Restore backup from {latest.name}?\nThis will overwrite current network settings.", QMessageBox.Yes | QMessageBox.No)

        if ret == QMessageBox.Yes:
            if self.backup_manager.restore_backup(latest):
                 QMessageBox.information(self, "Restore", "Restore successful. Please restart networking or reboot.")
            else:
                 QMessageBox.critical(self, "Restore Error", "Failed to restore backup.")
