import unittest
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path
from src.backend.settings import SettingsManager
from src.backend.backup import NetworkBackupManager

class TestSettingsManager(unittest.TestCase):
    def setUp(self):
        self.mock_dir = Path("/tmp/mock_config")
        self.patcher = patch("src.backend.settings.get_config_dir", return_value=self.mock_dir)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_default_settings(self):
        with patch("builtins.open", side_effect=FileNotFoundError):
            manager = SettingsManager()
            self.assertEqual(manager.get("language"), "en_US")
            self.assertFalse(manager.get("start_on_boot"))

    def test_save_load(self):
        manager = SettingsManager()
        # Mock json dump/load
        with patch("builtins.open", mock_open()) as mocked_file:
             manager.set("language", "pt_BR")
             # Verify write
             mocked_file.assert_called()

class TestNetworkBackupManager(unittest.TestCase):
    @patch("src.backend.backup.shutil")
    @patch("src.backend.backup.subprocess.run")
    def test_create_backup(self, mock_run, mock_shutil):
        # Mock paths
        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.mkdir"):
                manager = NetworkBackupManager("/tmp/backups")
                backup_path = manager.create_backup()

                # Should attempt to copy NetworkManager
                # We check if shutil.copytree or copy2 was called
                self.assertTrue(mock_shutil.copytree.called or mock_shutil.copy2.called)
                self.assertIsNotNone(backup_path)

if __name__ == '__main__':
    unittest.main()
