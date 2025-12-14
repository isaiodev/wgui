import sys
import logging
import os
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QIcon
from src.ui.main_window import MainWindow
from src.ui.tray import SystemTray
from src.backend.wireguard import WireGuardService
from src.backend.profiles import ProfileManager
from src.backend.settings import SettingsManager
from src.backend.backup import NetworkBackupManager
from src.utils.i18n import LocalizationManager
from src.utils.paths import get_assets_dir

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WireGuardApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False) # Keep running for tray

        # I18n
        self.loc_manager = LocalizationManager(self.app)
        self.loc_manager.load_language() # Load system language

        # Managers
        self.wg_service = WireGuardService()
        self.profile_manager = ProfileManager()
        self.settings_manager = SettingsManager()
        self.backup_manager = NetworkBackupManager()

        self.main_window = MainWindow(
            self.wg_service,
            self.profile_manager,
            self.settings_manager,
            self.backup_manager
        )
        self.tray = SystemTray()

        # Connect signals
        self.main_window.connect_signal.connect(self.connect_tunnel)
        self.main_window.disconnect_signal.connect(self.disconnect_tunnel)

        self.tray.show_window_signal.connect(self.show_window)
        self.tray.quit_signal.connect(self.quit_app)
        self.tray.activated.connect(self.on_tray_activated)

        self.tray.show()

        # Check Privileges
        if not self.check_privileges():
             logger.warning("Not running as root. Functionality will be limited.")
             # We might show a message box here, but let's do it after main window init or rely on logger for now

        # Check if WG is installed
        if not self.wg_service.is_installed():
             logger.warning("WireGuard tools (wg, wg-quick) not found!")

    def check_privileges(self) -> bool:
        if sys.platform != "win32":
            return os.geteuid() == 0
        return True # Windows check is more complex, assuming True or handled by UAC manifest later

    def run(self):
        # Apply settings (e.g. start minimized?)
        if not self.settings_manager.get("start_on_boot", False):
            # If not autostart, maybe show window?
            pass

        # On Wayland, sometimes show() is needed explicitly
        if os.environ.get("XDG_SESSION_TYPE") == "wayland":
            logger.info("Wayland detected.")

        return self.app.exec()

    def show_window(self):
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()

    def on_tray_activated(self, reason):
        if reason == SystemTray.Trigger:
            if self.main_window.isVisible():
                self.main_window.hide()
            else:
                self.show_window()

    def connect_tunnel(self, profile_name):
        path = self.profile_manager.get_profile_path(profile_name)
        success = self.wg_service.connect(str(path))
        if success:
            self.tray.update_status(True, profile_name)
            self.main_window.detail_view.set_status("connected")
        else:
            self.main_window.detail_view.set_status("error")
            self.tray.update_status(False) # Keep disconnected/error icon

    def disconnect_tunnel(self, profile_name):
        path = self.profile_manager.get_profile_path(profile_name)
        success = self.wg_service.disconnect(str(path))
        if success:
            self.tray.update_status(False)
            self.main_window.detail_view.set_status("disconnected")
        else:
            self.main_window.detail_view.set_status("error")

    def quit_app(self):
        self.app.quit()

if __name__ == "__main__":
    client = WireGuardApp()
    sys.exit(client.run())
