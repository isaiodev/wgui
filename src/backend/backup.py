import shutil
import subprocess
import datetime
import logging
import platform
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

class NetworkBackupManager:
    def __init__(self, backup_base_dir: str = "/root/network-backups"):
        self.backup_base = Path(backup_base_dir)

    def is_supported(self) -> bool:
        """Check if backup is supported on this platform."""
        return platform.system() == "Linux"

    def create_backup(self) -> Optional[Path]:
        """
        Creates a backup of network configurations.
        Returns the path to the backup directory if successful, None otherwise.
        """
        if not self.is_supported():
             logger.warning("Network backup is only supported on Linux.")
             return None

        if not self.backup_base.exists():
            try:
                self.backup_base.mkdir(parents=True, exist_ok=True)
            except PermissionError:
                logger.error("Permission denied creating backup base directory. Are you root?")
                return None

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        backup_dir = self.backup_base / f"network-backup-{timestamp}"

        try:
            backup_dir.mkdir()
        except OSError as e:
            logger.error(f"Failed to create backup dir {backup_dir}: {e}")
            return None

        logger.info(f"Creating backup in {backup_dir}")

        # Helper to copy
        def copy_safe(src, dst_dir):
            s = Path(src)
            if s.exists():
                try:
                    if s.is_dir():
                        shutil.copytree(s, dst_dir / s.name, symlinks=True)
                    else:
                        shutil.copy2(s, dst_dir / s.name)
                except Exception as e:
                    logger.warning(f"Failed to copy {s}: {e}")

        # Helper to run command and save output
        def run_save(cmd, out_file):
            try:
                with open(out_file, "w") as f:
                    subprocess.run(cmd, stdout=f, stderr=subprocess.DEVNULL, shell=False, check=False)
            except Exception as e:
                logger.warning(f"Failed to run {' '.join(cmd)}: {e}")

        # Files/Dirs to copy
        copy_safe("/etc/NetworkManager", backup_dir)
        copy_safe("/etc/systemd/network", backup_dir)

        # resolv.conf (copy-safe doesn't handle rename easily, so manual)
        try:
            if Path("/etc/resolv.conf").exists():
                 # Use copy (dereference symlinks per script `cp -L`)
                 shutil.copy("/etc/resolv.conf", backup_dir / "resolv.conf", follow_symlinks=True)
        except Exception as e:
            logger.warning(f"Failed to copy resolv.conf: {e}")

        # Command outputs
        run_save(["iptables-save"], backup_dir / "iptables.rules")
        run_save(["nft", "list", "ruleset"], backup_dir / "nftables.rules")
        run_save(["ip", "route", "show"], backup_dir / "ip-route.txt")
        run_save(["ip", "rule", "show"], backup_dir / "ip-rule.txt")
        run_save(["ip", "addr", "show"], backup_dir / "ip-addr.txt")
        run_save(["ip", "link", "show"], backup_dir / "ip-link.txt")
        run_save(["resolvectl", "status"], backup_dir / "resolvectl-status.txt")
        run_save(["lsmod"], backup_dir / "lsmod.txt")

        return backup_dir

    def list_backups(self) -> List[Path]:
        """Returns a list of available backup directories."""
        if not self.backup_base.exists():
            return []
        return sorted(list(self.backup_base.glob("network-backup-*")), reverse=True)

    def restore_backup(self, backup_dir: Path) -> bool:
        """
        Restores a backup from the given directory.
        Returns True if successful.
        """
        if not self.is_supported():
            return False

        if not backup_dir.exists():
            return False

        logger.info(f"Restoring backup from {backup_dir}")

        try:
            # Restore Directories
            nm_src = backup_dir / "NetworkManager"
            if nm_src.exists():
                # We typically want to overwrite. shutil.copytree with dirs_exist_ok=True (Py3.8+)
                shutil.copytree(nm_src, "/etc/NetworkManager", dirs_exist_ok=True)

            sysd_src = backup_dir / "network"
            if sysd_src.exists():
                shutil.copytree(sysd_src, "/etc/systemd/network", dirs_exist_ok=True)

            resolv_src = backup_dir / "resolv.conf"
            if resolv_src.exists():
                shutil.copy2(resolv_src, "/etc/resolv.conf")

            # Restore Rules
            iptables_src = backup_dir / "iptables.rules"
            if iptables_src.exists():
                with open(iptables_src, "r") as f:
                    subprocess.run(["iptables-restore"], stdin=f, check=False)

            nft_src = backup_dir / "nftables.rules"
            if nft_src.exists():
                 subprocess.run(["nft", "-f", str(nft_src)], check=False)

            return True

        except Exception as e:
            logger.error(f"Error during restore: {e}")
            return False
