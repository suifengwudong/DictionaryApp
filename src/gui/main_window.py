import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QMessageBox
from PyQt6.QtCore import pyqtSlot
from .search_widget import SearchWidget
from .result_widget import ResultWidget
from ..api.dictionary_api import DictionaryAPI
from ..database.history_db import HistoryDB

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Own Dictionary")
        self.setGeometry(100, 100, 600, 450)
        self.setStyleSheet("""
            QWidget {
                background-color: #2e2e2e;
                color: #eeeeee;
                font-size: 14px;
            }
            QMainWindow {
                background-color: #252525;
            }
            QLineEdit {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton {
                background-color: #555555;
                border: 1px solid #666666;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
            QScrollArea {
                border: none;
            }
            QLabel {
                background-color: transparent;
            }
        """)

        # --- Central Widget and Layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # --- Create Widgets ---
        self.search_widget = SearchWidget()
        self.result_widget = ResultWidget()

        # --- Add Widgets to Layout ---
        layout.addWidget(self.search_widget)
        layout.addWidget(self.result_widget)

        # --- Backend Components ---
        self.api = DictionaryAPI()
        self.db = HistoryDB()

        # --- Connections ---
        self.search_widget.searchRequested.connect(self.handle_search)
        self.api.searchCompleted.connect(self.handle_search_success)
        self.api.searchFailed.connect(self.handle_search_failure)
        self.api.searchCompleted.connect(self.add_word_to_history)

    @pyqtSlot(str)
    def handle_search(self, word):
        self.result_widget.clear_results()
        self.result_widget.set_loading(True)
        self.api.search_word(word)

    @pyqtSlot(dict)
    def handle_search_success(self, data):
        self.result_widget.set_loading(False)
        self.result_widget.display_results(data)

    @pyqtSlot(str)
    def handle_search_failure(self, error_message):
        self.result_widget.set_loading(False)
        QMessageBox.warning(self, "Search Error", error_message)

    @pyqtSlot(dict)
    def add_word_to_history(self, data):
        """Extracts the word from the data and adds it to the history DB."""
        word = data.get('word')
        if word:
            self.db.add_search_entry(word)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())
