from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton
from PyQt6.QtCore import pyqtSignal

class SearchWidget(QWidget):
    """
    A widget with a line edit for input and a search button.
    Emits a signal when the search button is clicked.
    """
    searchRequested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter a word...")
        self.search_input.returnPressed.connect(self.on_search)
        
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.on_search)
        
        self.layout.addWidget(self.search_input)
        self.layout.addWidget(self.search_button)

    def on_search(self):
        word = self.search_input.text().strip()
        if word:
            self.searchRequested.emit(word)
