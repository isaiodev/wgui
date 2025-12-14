from PySide6.QtGui import QPixmap, QPainter, QColor, QIcon, QPen
from PySide6.QtCore import Qt

class IconGenerator:
    @staticmethod
    def create_tray_icon(color: str, symbol_type: str = "none") -> QIcon:
        """
        Generates a dynamic tray icon.
        :param color: Background color (e.g. green, red).
        :param symbol_type: 'none', 'wifi', 'no_internet'
        """
        size = 64
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw base circle
        painter.setBrush(QColor(color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, size, size)

        painter.setPen(QColor("white"))

        if symbol_type == "no_internet":
             # Draw a slashed circle or similar "No Internet" sign
             pen = QPen(QColor("white"))
             pen.setWidth(4)
             painter.setPen(pen)
             # Draw '!'
             font = painter.font()
             font.setPixelSize(int(size * 0.5))
             font.setBold(True)
             painter.setFont(font)
             painter.drawText(pixmap.rect(), Qt.AlignCenter, "!")

             # Draw slash
             # painter.drawLine(size * 0.3, size * 0.3, size * 0.7, size * 0.7)

        elif symbol_type == "connected":
             # Draw a checkmark or 'W'
             font = painter.font()
             font.setPixelSize(int(size * 0.5))
             font.setBold(True)
             painter.setFont(font)
             painter.drawText(pixmap.rect(), Qt.AlignCenter, "W")

        painter.end()

        return QIcon(pixmap)

    @staticmethod
    def get_status_icon(status: str) -> QIcon:
        if status == "connected":
            return IconGenerator.create_tray_icon("#4CAF50", "connected") # Green
        elif status == "disconnected":
            # Red with No Internet sign
            return IconGenerator.create_tray_icon("#F44336", "no_internet") # Red
        elif status == "error":
            return IconGenerator.create_tray_icon("#F44336", "no_internet") # Red
        else:
            return IconGenerator.create_tray_icon("#9E9E9E") # Default Gray
