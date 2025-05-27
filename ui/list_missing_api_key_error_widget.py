from PyQt5 import uic, QtWidgets, QtGui
import os


class ListMissingApiKeyErrorWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.plugin_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(
            self.plugin_dir, "list_missing_api_key_error_widget.ui")
        uic.loadUi(ui_path, self)
