import os
import shutil
import platform
from pathlib import Path
from typing import List, Optional
from src.utils.paths import get_profiles_dir

class ProfileManager:
    def __init__(self):
        self.profiles_dir = get_profiles_dir()

    def list_profiles(self) -> List[str]:
        """List all available profile names (without .conf extension)."""
        return [f.stem for f in self.profiles_dir.glob("*.conf")]

    def get_profile_path(self, name: str) -> Path:
        """Get the full path to a profile config file."""
        return self.profiles_dir / f"{name}.conf"

    def import_profile(self, source_path: str) -> bool:
        """Import a profile from a file path."""
        src = Path(source_path)
        if not src.exists() or src.suffix != ".conf":
            return False

        dest = self.profiles_dir / src.name
        try:
            shutil.copy(src, dest)
            self._secure_file(dest)
            return True
        except Exception:
            return False

    def create_profile(self, name: str, content: str) -> bool:
        """Create a new profile with the given content."""
        dest = self.profiles_dir / f"{name}.conf"
        try:
            with open(dest, "w") as f:
                f.write(content)
            self._secure_file(dest)
            return True
        except Exception:
            return False

    def delete_profile(self, name: str) -> bool:
        """Delete a profile."""
        path = self.get_profile_path(name)
        try:
            if path.exists():
                path.unlink()
            return True
        except Exception:
            return False

    def _secure_file(self, path: Path):
        """Apply security permissions to the file."""
        if platform.system() != "Windows":
            os.chmod(path, 0o600)
        else:
            # Windows permission handling could be added here
            pass
