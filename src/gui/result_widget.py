import functools
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea, QFrame, QHBoxLayout, QStyle
from PyQt6.QtCore import pyqtSlot
from ..audio.audio_player import AudioPlayer

class ResultWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self._layout.addWidget(self.scroll_area)
        
        self.audio_player = AudioPlayer()
        self.clear_results() # Initialize with an empty widget

    def clear_results(self):
        # Replace the old content widget with a new one
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)

    def set_loading(self, is_loading):
        self.clear_results()
        if is_loading:
            self.scroll_layout.addWidget(QLabel("Searching..."))

    @pyqtSlot(dict)
    def display_results(self, data):
        self.clear_results()
        
        word = data.get('word', 'N/A')
        phonetic = data.get('phonetic', '')
        
        self.scroll_layout.addWidget(QLabel(f"<h2>{word}</h2>"))
        
        # Phonetic and Play Button Layout
        phonetic_layout = QHBoxLayout()
        
        if phonetic:
            phonetic_layout.addWidget(QLabel(f"<i>{phonetic}</i>"))

        # Create a button for each available audio source
        phonetics = data.get('phonetics', [])
        for p in phonetics:
            audio_url = p.get('audio')
            if audio_url:
                play_button = QPushButton()
                play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume))
                play_button.setFixedSize(30, 30)
                play_button.setStyleSheet("border-radius: 15px;") # Make it circular
                # Use functools.partial to pass the specific url to the slot
                play_button.clicked.connect(functools.partial(self.audio_player.play_audio_from_url, audio_url))
                phonetic_layout.addWidget(play_button)

        phonetic_layout.addStretch() # Push widgets to the left
        self.scroll_layout.addLayout(phonetic_layout)

        for meaning in data.get('meanings', []):
            line = QFrame()
            line.setFrameShape(QFrame.Shape.HLine)
            line.setFrameShadow(QFrame.Shadow.Sunken)
            self.scroll_layout.addWidget(line)
            
            self.scroll_layout.addWidget(QLabel(f"<b>{meaning.get('partOfSpeech', '')}</b>"))
            for i, definition in enumerate(meaning.get('definitions', [])):
                def_text = definition.get('definition', '')
                definition_label = QLabel(f"{i+1}. {def_text}")
                definition_label.setWordWrap(True) # Enable word wrapping
                self.scroll_layout.addWidget(definition_label)
