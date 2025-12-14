import shutil
import subprocess
import platform
import logging
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)

class WireGuardService:
    def __init__(self):
        self.wg_path = shutil.which("wg")
        self.wg_quick_path = shutil.which("wg-quick")
        self.os_type = platform.system()

    def is_installed(self) -> bool:
        """Check if WireGuard tools are installed."""
        return self.wg_path is not None and self.wg_quick_path is not None

    def get_status(self, interface: str) -> Dict[str, str]:
        """
        Get the status of a specific interface.
        Returns a dict with 'status', 'handshake', 'transfer', etc.
        """
        if not self.is_installed():
            return {"status": "error", "message": "WireGuard not installed"}

        # This is a simplification. Real implementation parses `wg show` output.
        # For now, we check if the interface exists in the output of `wg show interfaces`
        try:
            # Check if interface is up
            result = subprocess.run(
                [self.wg_path, "show", "interfaces"],
                capture_output=True, text=True, check=False
            )
            if result.returncode != 0:
                 return {"status": "disconnected"}

            if interface in result.stdout.split():
                 # Get details
                 details = subprocess.run(
                     [self.wg_path, "show", interface, "latest-handshakes"],
                     capture_output=True, text=True
                 )
                 # Parse details... for now return basic connected
                 return {"status": "connected"}
            else:
                 return {"status": "disconnected"}

        except Exception as e:
            logger.error(f"Error getting status for {interface}: {e}")
            return {"status": "error", "message": str(e)}

    def connect(self, config_path: str) -> bool:
        """Connect using wg-quick."""
        if not self.is_installed():
            return False

        try:
            cmd = [self.wg_quick_path, "up", config_path]
            logger.info(f"Running: {' '.join(cmd)}")
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to connect: {e.stderr}")
            return False

    def disconnect(self, config_path: str) -> bool:
        """Disconnect using wg-quick."""
        if not self.is_installed():
            return False

        try:
            cmd = [self.wg_quick_path, "down", config_path]
            logger.info(f"Running: {' '.join(cmd)}")
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to disconnect: {e.stderr}")
            return False
