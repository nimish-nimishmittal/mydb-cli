import json
import os
from datetime import datetime
from tabulate import tabulate
from typing import List, Optional, Dict, Any

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
    
    def clear_history(self, before_date: Optional[datetime] = None) -> bool:
        """
        Clear history entries.
        
        Args:
            before_date (datetime, optional): If provided, only clear entries before this date
        
        Returns:
            bool: True if operation was successful, False otherwise
        """
        try:
            if before_date:
                history = self._read_history()
                filtered_history = [
                    entry for entry in history 
                    if datetime.fromisoformat(entry['timestamp']) >= before_date
                ]
                self._write_history(filtered_history)
            else:
                self._write_history([])
            
            # Add entry about clearing history
            self.add_entry(
                command='clear_history',
                details=f"History cleared {'before ' + before_date.strftime('%Y-%m-%d') if before_date else 'completely'}",
                status='success'
            )
            return True
            
        except Exception as e:
            self.add_entry(
                command='clear_history',
                details='Failed to clear history',
                status='failed',
                error=str(e)
            )
            return False

    def backup_history(self, backup_path: Optional[str] = None) -> bool:
        """
        Create a backup of the history file.
        
        Args:
            backup_path (str, optional): Custom path for backup file
                                       If not provided, uses timestamp-based name
        
        Returns:
            bool: True if backup was successful, False otherwise
        """
        try:
            if not backup_path:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = f'.mydb/history_backup_{timestamp}.json'

            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            history = self._read_history()
            
            with open(backup_path, 'w') as f:
                json.dump(history, f, indent=2)

            self.add_entry(
                command='backup_history',
                details=f'History backed up to {backup_path}',
                status='success'
            )
            return True

        except Exception as e:
            self.add_entry(
                command='backup_history',
                details='Failed to backup history',
                status='failed',
                error=str(e)
            )
            return False
