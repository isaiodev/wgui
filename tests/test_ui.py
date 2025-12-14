import unittest
from unittest.mock import MagicMock, patch
from PySide6.QtWidgets import QApplication
from src.ui.dialogs import AddProfileDialog
from src.backend.profiles import ProfileManager

app = QApplication([])

class TestAddProfileDialog(unittest.TestCase):
    def test_save_validation(self):
        manager = MagicMock(spec=ProfileManager)
        dialog = AddProfileDialog(manager)

        # Test empty save
        with patch("PySide6.QtWidgets.QMessageBox.warning") as mock_warn:
            dialog.save_profile()
            mock_warn.assert_called()

        # Test valid save
        dialog.name_edit.setText("test_tunnel")
        dialog.config_edit.setText("some_config")
        manager.get_profile_path.return_value.exists.return_value = False
        manager.create_profile.return_value = True

        with patch.object(dialog, 'accept') as mock_accept:
             dialog.save_profile()
             mock_accept.assert_called()
             manager.create_profile.assert_called_with("test_tunnel", "some_config")

if __name__ == '__main__':
    unittest.main()
