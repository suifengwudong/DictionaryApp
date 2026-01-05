import os
import requests
from PyQt6.QtCore import QObject, QUrl, pyqtSlot
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

class AudioPlayer(QObject):
    """
    Handles downloading and playing audio from a URL.
    Caches the audio file locally.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._player = QMediaPlayer()
        self._audio_output = QAudioOutput()
        self._player.setAudioOutput(self._audio_output)
        self.cache_dir = "audio_cache"
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    @pyqtSlot(str)
    def play_audio_from_url(self, url):
        """
        Downloads and plays an audio file from a URL.
        """
        if not url:
            print("No audio URL provided.")
            return

        try:
            file_name = url.split("/")[-1]
            local_path = os.path.join(self.cache_dir, file_name)

            if not os.path.exists(local_path):
                print(f"Downloading audio from {url}...")
                response = requests.get(url, stream=True)
                response.raise_for_status()
                with open(local_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"Audio cached at {local_path}")

            self._player.setSource(QUrl.fromLocalFile(os.path.abspath(local_path)))
            self._player.play()

        except requests.exceptions.RequestException as e:
            print(f"Error downloading audio: {e}")
        except Exception as e:
            print(f"Error playing audio: {e}")
