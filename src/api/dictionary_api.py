import requests
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

class DictionaryAPI(QObject):
    """
    Handles interaction with the dictionary API.
    Emits signals with the result of the API call.
    """
    searchCompleted = pyqtSignal(dict)
    searchFailed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.api_url = "https://api.dictionaryapi.dev/api/v2/entries/en/"

    @pyqtSlot(str)
    def search_word(self, word):
        """
        Searches for a word using the dictionary API.
        """
        if not word:
            self.searchFailed.emit("Please enter a word.")
            return

        try:
            response = requests.get(self.api_url + word)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                self.searchCompleted.emit(data[0])
            else:
                self.searchFailed.emit(f"No definition found for '{word}'.")

        except requests.exceptions.RequestException as e:
            self.searchFailed.emit(f"Network error: {e}")
        except Exception as e:
            self.searchFailed.emit(f"An error occurred: {e}")
