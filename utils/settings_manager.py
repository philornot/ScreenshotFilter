import json
import os


class SettingsManager:
    def __init__(self, settings_file='settings.json'):
        self.settings_file = settings_file
        self.settings = self._load_settings()

    def _load_settings(self):
        """Ładuje ustawienia z pliku"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, Exception):
                return {}
        return {}

    def get(self, key, default=None):
        """Pobiera wartość ustawienia"""
        return self.settings.get(key, default)

    def set(self, key, value):
        """Ustawia wartość ustawienia"""
        self.settings[key] = value

    def save(self):
        """Zapisuje ustawienia do pliku"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Błąd zapisywania ustawień: {e}")
