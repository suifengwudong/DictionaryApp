from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from api import search_word
from player import AudioPlayer, AudioDownloader
from PyQt6.QtCore import QUrl, QThreadPool
import webbrowser

class DictionaryApp(MainWindow):
    def __init__(self):
        super().__init__()
        self.audio_player = AudioPlayer()
        self.local_audio_paths = {}  # To store local audio paths by word
        self.thread_pool = QThreadPool()
        print(f"Multithreading with maximum {self.thread_pool.maxThreadCount()} threads.")
        self.connect_signals()

    def connect_signals(self):
        self.search_button.clicked.connect(self.perform_search)
        self.word_input.returnPressed.connect(self.perform_search)
        self.result_display.anchorClicked.connect(self.handle_link)

    def perform_search(self):
        word = self.word_input.text().strip()
        self.result_display.setText(f"Searching for '{word}'...")
        QApplication.processEvents()

        data, error = search_word(word)
        if error:
            self.result_display.setText(error)
            return
        
        self.display_results(data)

    def display_results(self, data):
        if not data or 'title' in data:
            self.result_display.setText(data.get('message', "No results found."))
            return

        self.local_audio_paths.clear() # Clear previous search results
        html_content = ""
        for entry in data:
            word = entry.get('word', 'N/A')
            phonetic = entry.get('phonetic', '')
            html_content += f"<h1>{word}</h1>"
            if phonetic:
                html_content += f"<h3><i>{phonetic}</i></h3>"

            # Find and start downloading the first audio URL in the background
            for p in entry.get('phonetics', []):
                if p.get('audio'):
                    audio_url = p['audio']
                    if audio_url:
                        # Create a worker and pass it to the thread pool
                        downloader = AudioDownloader(word, audio_url)
                        # Connect the result signal to a slot
                        downloader.signals.result.connect(self.on_download_complete)
                        self.thread_pool.start(downloader)
                        
                        # Add a placeholder link. The actual path will be filled in later.
                        html_content += f"<p>Pronunciation: <a href='play_audio:{word}'>Click to Play</a> ({p.get('text', '')})</p>"
                        break
            
            html_content += "<hr>"

            for meaning in entry.get('meanings', []):
                pos = meaning.get('partOfSpeech', 'N/A')
                html_content += f"<h2>{pos}</h2>"
                html_content += "<ul>"
                for i, definition in enumerate(meaning.get('definitions', [])):
                    html_content += f"<li><b>{i+1}.</b> {definition.get('definition', '')}</li>"
                    if 'example' in definition and definition['example']:
                        html_content += f"<ul><i>e.g. {definition['example']}</i></ul>"
                html_content += "</ul>"

            source_urls = entry.get('sourceUrls', [])
            if source_urls:
                html_content += "<h3>Sources:</h3><ul>"
                for url in source_urls:
                    html_content += f"<li><a href='{url}'>{url}</a></li>"
                html_content += "</ul>"

        self.result_display.setHtml(html_content)

    def on_download_complete(self, word_key, local_path):
        """
        This slot is called when an audio download is finished.
        """
        if local_path:
            print(f"Download complete for '{word_key}', path: {local_path}")
            self.local_audio_paths[word_key] = local_path
        else:
            print(f"Download failed for '{word_key}'.")

    def handle_link(self, url):
        # 获取URL的字符串表示
        url_string = url.toString()
        print(f"Link clicked: {url_string}") # 增加这行打印，用于调试

        # 最终修正：不再使用 scheme()，直接判断字符串前缀
        if url_string.startswith('play_audio:'):
            # 从 "play_audio:word" 中提取 "word"
            word_key = url_string.split(':', 1)[1]
            
            local_path_to_play = self.local_audio_paths.get(word_key)
            if local_path_to_play:
                self.audio_player.play_audio(local_path_to_play)
            else:
                print(f"Audio for '{word_key}' is not cached or still downloading.")
        else:
            # 只有当它不是我们的自定义链接时，才作为外部链接打开
            webbrowser.open(url_string)
