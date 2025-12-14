from PySide6.QtCore import QTranslator, QLocale, QCoreApplication
import logging

class LocalizationManager:
    def __init__(self, app):
        self.app = app
        self.translator = QTranslator()

    def load_language(self, locale_name: str = None):
        """
        Load a language. If locale_name is None, use system locale.
        """
        if locale_name is None:
            locale = QLocale.system()
        else:
            locale = QLocale(locale_name)

        # Path to translations. Assuming they are in 'src/i18n' or 'assets/translations'
        # In a real build, these would be compiled .qm files.
        if self.translator.load(locale, "app", "_", "src/i18n"):
            self.app.installTranslator(self.translator)
            logging.info(f"Loaded translation for {locale.name()}")
        else:
            logging.warning(f"Could not load translation for {locale.name()}")
