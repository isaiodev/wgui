import unittest
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path
from src.backend.wireguard import WireGuardService
from src.backend.profiles import ProfileManager

class TestWireGuardService(unittest.TestCase):
    @patch("src.backend.wireguard.shutil.which")
    def test_is_installed(self, mock_which):
        # Test when installed
        mock_which.side_effect = lambda x: "/usr/bin/" + x
        service = WireGuardService()
        self.assertTrue(service.is_installed())

        # Test when not installed
        mock_which.side_effect = None # Reset side_effect
        mock_which.return_value = None
        service = WireGuardService()
        self.assertFalse(service.is_installed())

    @patch("src.backend.wireguard.subprocess.run")
    @patch("src.backend.wireguard.shutil.which")
    def test_connect(self, mock_which, mock_run):
        mock_which.return_value = "/usr/bin/wg-quick"
        service = WireGuardService()

        # Mock successful connection
        mock_run.return_value.returncode = 0
        self.assertTrue(service.connect("/path/to/config.conf"))
        mock_run.assert_called()

class TestProfileManager(unittest.TestCase):
    @patch("src.backend.profiles.get_profiles_dir")
    def test_list_profiles(self, mock_get_dir):
        mock_dir = MagicMock()
        mock_p1 = MagicMock()
        mock_p1.stem = "profile1"
        mock_p2 = MagicMock()
        mock_p2.stem = "profile2"

        mock_dir.glob.return_value = [mock_p1, mock_p2]
        mock_get_dir.return_value = mock_dir

        manager = ProfileManager()
        profiles = manager.list_profiles()
        self.assertEqual(profiles, ["profile1", "profile2"])

if __name__ == '__main__':
    unittest.main()
