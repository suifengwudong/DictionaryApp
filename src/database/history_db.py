import sqlite3
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

class HistoryDB(QObject):
    """
    Manages the search history in an SQLite database.
    """
    history_updated = pyqtSignal(list)

    def __init__(self, db_name="history.db"):
        super().__init__()
        self.db_name = db_name
        self.conn = None
        self.create_connection()
        self.create_table()

    def create_connection(self):
        """Create a database connection to the SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_name)
        except sqlite3.Error as e:
            print(e)

    def create_table(self):
        """Create the history table if it doesn't exist."""
        try:
            c = self.conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            print(e)

    @pyqtSlot(str)
    def add_search_entry(self, word):
        """Add a new search entry to the history table."""
        if not word:
            return
        try:
            c = self.conn.cursor()
            c.execute("INSERT INTO history (word) VALUES (?)", (word,))
            self.conn.commit()
            self.get_history() # Emit signal with updated history
        except sqlite3.Error as e:
            print(f"Database error: {e}")

    @pyqtSlot()
    def get_history(self):
        """Retrieve search history from the database."""
        try:
            c = self.conn.cursor()
            c.execute("SELECT word FROM history ORDER BY timestamp DESC LIMIT 20")
            history = [row[0] for row in c.fetchall()]
            self.history_updated.emit(history)
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            self.history_updated.emit([])

    def __del__(self):
        if self.conn:
            self.conn.close()
