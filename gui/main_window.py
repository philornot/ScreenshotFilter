import tkinter as tk
from tkinter import messagebox, filedialog

import sv_ttk
from utils.i18n import I18nManager
from utils.settings_manager import SettingsManager

from core.clip_classifier import CLIPClassifier
from core.image_processor import ImageProcessor
from .ui_components import UIComponents


class CLIPScreenshotFilterGUI:
    def __init__(self, root, logger):
        self.root = root
        self.logger = logger

        # Managers
        self.settings = SettingsManager()
        self.i18n = I18nManager(self.settings.get('language', 'pl'))

        # Konfiguracja okna
        self.root.title(self.i18n.get('window_title'))
        self.root.geometry("700x500")
        self.root.minsize(600, 630)

        # Zmienne
        self.folder_path = tk.StringVar(value=self.settings.get('last_input_folder', ''))
        self.output_path = tk.StringVar(value=self.settings.get('last_output_folder', ''))
        self.confidence_var = tk.DoubleVar(value=self.settings.get('confidence_threshold', 0.6))
        self.verbose_logs = tk.BooleanVar(value=self.settings.get('verbose_logs', True))
        self.is_dark_theme = tk.BooleanVar(value=self.settings.get('dark_theme', True))

        # Komponenty
        self.ui = UIComponents(self.root, self)
        self.classifier = CLIPClassifier(logger)
        self.processor = ImageProcessor(logger)

        # Zastosuj domyślny motyw
        self.apply_theme()

        # Utwórz interfejs użytkownika
        self.ui.create_widgets()

        # Załaduj model CLIP
        self.classifier.load_model(self._on_model_loaded, self._on_model_error)

        # Bind zamykania okna
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def apply_theme(self):
        """Aplikuje wybrany motyw"""
        try:
            if self.is_dark_theme.get():
                sv_ttk.set_theme("dark")
                self.logger.info("Zastosowano ciemny motyw")
            else:
                sv_ttk.set_theme("light")
                self.logger.info("Zastosowano jasny motyw")
        except Exception as e:
            self.logger.warning(
                f"Nie można zastosować motywu sv_ttk: {e}. Sprawdź czy biblioteka jest zainstalowana: pip install sv-ttk")

    def toggle_theme(self):
        """Przełącza między ciemnym a jasnym motywem"""
        self.is_dark_theme.set(not self.is_dark_theme.get())
        self.settings.set('dark_theme', self.is_dark_theme.get())
        self.apply_theme()

    def toggle_language(self):
        """Przełącza język między polskim a angielskim"""
        current_lang = self.i18n.current_language
        new_lang = 'en' if current_lang == 'pl' else 'pl'
        self.i18n.set_language(new_lang)
        self.settings.set('language', new_lang)

        # Odśwież interfejs
        self.root.title(self.i18n.get('window_title'))
        self.ui.refresh_ui()

    def _on_model_loaded(self):
        """Callback gdy model został załadowany"""
        self.ui.update_model_status(self.i18n.get('model_ready'), "green")
        self.ui.update_status(self.i18n.get('select_folders'), "blue")
        self._update_filter_button_state()

    def _on_model_error(self, error_msg):
        """Callback gdy wystąpił błąd przy ładowaniu modelu"""
        self.ui.update_model_status(self.i18n.get('model_error'), "red")
        self.ui.update_status(error_msg, "red")
        messagebox.showerror(self.i18n.get('model_error'),
                             f"{error_msg}\n\n{self.i18n.get('install_libraries')}")

    def browse_input_folder(self):
        """Wybiera folder wejściowy ze screenshotami"""
        folder = filedialog.askdirectory(
            title=self.i18n.get('select_input_folder'),
            initialdir=self.settings.get('last_input_folder', '')
        )
        if folder:
            self.folder_path.set(folder)
            self.settings.set('last_input_folder', folder)
            self.logger.info(f"Wybrano folder wejściowy: {folder}")

            # Automatycznie ustaw folder wyjściowy jako katalog nadrzędny folderu wejściowego
            if not self.output_path.get():
                import os
                parent_dir = os.path.dirname(folder)
                self.output_path.set(parent_dir)
                self.settings.set('last_output_folder', parent_dir)
                self.logger.info(f"Automatycznie ustawiono folder wyjściowy: {parent_dir}")

            self._update_filter_button_state()

    def browse_output_folder(self):
        """Wybiera folder wyjściowy dla sklasyfikowanych obrazów"""
        folder = filedialog.askdirectory(
            title=self.i18n.get('select_output_folder'),
            initialdir=self.settings.get('last_output_folder', '')
        )
        if folder:
            self.output_path.set(folder)
            self.settings.set('last_output_folder', folder)
            self.logger.info(f"Wybrano folder wyjściowy: {folder}")
            self._update_filter_button_state()

    def _update_filter_button_state(self):
        """Aktualizuje stan przycisku filtrowania"""
        can_filter = (self.classifier.is_loaded() and
                      self.folder_path.get() and
                      self.output_path.get())

        if can_filter:
            self.ui.enable_filter_button()
            self.ui.update_status(self.i18n.get('ready_to_classify'), "green")
        else:
            self.ui.disable_filter_button()

    def start_filtering(self):
        """Rozpoczyna proces filtrowania obrazów"""
        if not self.folder_path.get():
            messagebox.showerror(self.i18n.get('error'), self.i18n.get('select_input_first'))
            return

        if not self.output_path.get():
            messagebox.showerror(self.i18n.get('error'), self.i18n.get('select_output_first'))
            return

        if not self.classifier.is_loaded():
            messagebox.showerror(self.i18n.get('error'), self.i18n.get('model_not_loaded'))
            return

        # Przygotuj konfigurację
        config = {
            'input_folder': self.folder_path.get(),
            'output_folder': self.output_path.get(),
            'confidence_threshold': self.confidence_var.get(),
            'verbose_logs': self.verbose_logs.get()
        }

        # Zapisz ustawienia
        self.settings.set('confidence_threshold', self.confidence_var.get())
        self.settings.set('verbose_logs', self.verbose_logs.get())

        # Rozpocznij przetwarzanie
        self.ui.start_processing()
        self.processor.process_images(
            config,
            self.classifier,
            self.ui.update_progress,
            self._on_processing_complete
        )

    def _on_processing_complete(self, result):
        """Callback po zakończeniu przetwarzania"""
        self.ui.finish_processing()
        messagebox.showinfo(self.i18n.get('classification_results'), result)

    def update_confidence_label(self, value):
        """Aktualizuje label z wartością progu pewności"""
        self.ui.update_confidence_display(float(value))

    def on_closing(self):
        """Obsługuje zamknięcie aplikacji"""
        self.settings.save()
        self.root.destroy()
