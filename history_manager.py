import json
import os
from datetime import datetime
from tabulate import tabulate

class HistoryManager:
    def __init__(self, history_file='.mydb/history.json'):
        self.history_file = history_file
        self._ensure_history_file()

    def _ensure_history_file(self):
        """Ensure history file exists"""
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w') as f:
                json.dump([], f)

    def add_entry(self, command, details, status='success', error=None):
        """Add a new entry to history"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'command': command,
            'details': details,
            'status': status,
            'error': error
        }
        
        history = self._read_history()
        history.append(entry)
        self._write_history(history)

    def _read_history(self):
        """Read history from file"""
        with open(self.history_file, 'r') as f:
            return json.load(f)

    def _write_history(self, history):
        """Write history to file"""
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)

    def get_history(self, limit=None):
        """Get formatted history"""
        history = self._read_history()
        if limit:
            history = history[-limit:]
        
        formatted_entries = []
        for entry in history:
            timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            status_symbol = '✓' if entry['status'] == 'success' else '✗'
            formatted_entries.append([
                timestamp,
                status_symbol,
                entry['command'],
                entry['details'],
                entry['error'] if entry['error'] else ''
            ])
        
        return formatted_entries
