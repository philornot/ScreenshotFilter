import tkinter as tk
from tkinter import ttk


class UIComponents:
    def __init__(self, root, main_app):
        self.root = root
        self.main_app = main_app

        # Referencje do widgetów
        self.model_status = None
        self.status_label = None
        self.filter_button = None
        self.progress = None
        self.confidence_label = None
        self.theme_button = None
        self.language_button = None

        # Labels do odświeżania
        self.input_label = None
        self.output_label = None
        self.config_frame = None
        self.description_label = None
        self.confidence_text_label = None
        self.verbose_check = None
        self.title_label = None
        self.subtitle_label = None

    def create_widgets(self):
        """Tworzy wszystkie widgety interfejsu"""
        # Główna ramka z możliwością przewijania
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Konfiguruj responsywność
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        current_row = 0

        # Header z przełącznikami
        current_row = self._create_header(main_frame, current_row)

        # Status modelu
        current_row = self._create_model_status(main_frame, current_row)

        # Sekcja wyboru folderów
        current_row = self._create_folder_selection(main_frame, current_row)

        # Sekcja konfiguracji
        current_row = self._create_configuration(main_frame, current_row)

        # Opis działania
        current_row = self._create_description(main_frame, current_row)

        # Kontrole przetwarzania
        current_row = self._create_processing_controls(main_frame, current_row)

    def _create_header(self, parent, row):
        """Tworzy header z tytułem i przełącznikami"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.grid_columnconfigure(1, weight=1)

        # Tytuł
        self.title_label = ttk.Label(header_frame, text=self.main_app.i18n.get('window_title'),
                                     font=("Arial", 16, "bold"))
        self.title_label.grid(row=0, column=0, sticky=tk.W)

        # Przełączniki
        controls_frame = ttk.Frame(header_frame)
        controls_frame.grid(row=0, column=2, sticky=tk.E)

        self.language_button = ttk.Button(controls_frame, text=self.main_app.i18n.get('toggle_language'),
                                          command=self.main_app.toggle_language, width=8)
        self.language_button.grid(row=0, column=0, padx=(0, 5))

        self.theme_button = ttk.Button(controls_frame, text=self.main_app.i18n.get('toggle_theme'),
                                       command=self.main_app.toggle_theme)
        self.theme_button.grid(row=0, column=1)

        # Podtytuł
        self.subtitle_label = ttk.Label(header_frame, text=self.main_app.i18n.get('subtitle'),
                                        font=("Arial", 10))
        self.subtitle_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))

        return row + 1

    def _create_model_status(self, parent, row):
        """Tworzy sekcję statusu modelu"""
        self.model_status = ttk.Label(parent, text=self.main_app.i18n.get('loading_model'),
                                      font=("Arial", 10, "italic"))
        self.model_status.grid(row=row, column=0, pady=(10, 20))
        return row + 1

    def _create_folder_selection(self, parent, row):
        """Tworzy sekcję wyboru folderów"""
        # Folder wejściowy
        self.input_label = ttk.Label(parent, text=self.main_app.i18n.get('input_folder_label'))
        self.input_label.grid(row=row, column=0, sticky=tk.W, pady=(0, 5))

        input_frame = ttk.Frame(parent)
        input_frame.grid(row=row + 1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.grid_columnconfigure(0, weight=1)

        self.input_entry = ttk.Entry(input_frame, textvariable=self.main_app.folder_path,
                                     width=60, state="readonly")
        self.input_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))

        self.input_browse_button = ttk.Button(input_frame, text=self.main_app.i18n.get('browse'),
                                              command=self.main_app.browse_input_folder)
        self.input_browse_button.grid(row=0, column=1)

        # Folder wyjściowy
        self.output_label = ttk.Label(parent, text=self.main_app.i18n.get('output_folder_label'))
        self.output_label.grid(row=row + 2, column=0, sticky=tk.W, pady=(10, 5))

        output_frame = ttk.Frame(parent)
        output_frame.grid(row=row + 3, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        output_frame.grid_columnconfigure(0, weight=1)

        self.output_entry = ttk.Entry(output_frame, textvariable=self.main_app.output_path,
                                      width=60, state="readonly")
        self.output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))

        self.output_browse_button = ttk.Button(output_frame, text=self.main_app.i18n.get('browse'),
                                               command=self.main_app.browse_output_folder)
        self.output_browse_button.grid(row=0, column=1)

        return row + 4

    def _create_configuration(self, parent, row):
        """Tworzy sekcję konfiguracji"""
        self.config_frame = ttk.LabelFrame(parent, text=self.main_app.i18n.get('configuration'), padding="15")
        self.config_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        self.config_frame.grid_columnconfigure(1, weight=1)

        # Próg pewności
        self.confidence_text_label = ttk.Label(self.config_frame, text=self.main_app.i18n.get('confidence_threshold'))
        self.confidence_text_label.grid(row=0, column=0, sticky=tk.W, pady=5)

        confidence_frame = ttk.Frame(self.config_frame)
        confidence_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        confidence_frame.grid_columnconfigure(0, weight=1)

        confidence_scale = ttk.Scale(confidence_frame, from_=0.0, to=1.0,
                                     variable=self.main_app.confidence_var, orient="horizontal")
        confidence_scale.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        confidence_scale.configure(command=self.main_app.update_confidence_label)

        self.confidence_label = ttk.Label(confidence_frame, text="0.60", width=6)
        self.confidence_label.grid(row=0, column=1)

        # Checkbox dla szczegółowych logów
        self.verbose_check = ttk.Checkbutton(self.config_frame, text=self.main_app.i18n.get('verbose_logs'),
                                             variable=self.main_app.verbose_logs)
        self.verbose_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))

        return row + 1

    def _create_description(self, parent, row):
        """Tworzy opis działania aplikacji"""
        self.description_label = ttk.Label(parent, text=self.main_app.i18n.get('description'),
                                           justify=tk.CENTER, font=("Arial", 9))
        self.description_label.grid(row=row, column=0, pady=(0, 20))

        return row + 1

    def _create_processing_controls(self, parent, row):
        """Tworzy kontrolki do przetwarzania"""
        # Przycisk uruchomienia
        self.filter_button = ttk.Button(parent, text=self.main_app.i18n.get('start_classification'),
                                        command=self.main_app.start_filtering, state="disabled")
        self.filter_button.grid(row=row, column=0, pady=(0, 15))

        # Pasek postępu
        self.progress = ttk.Progressbar(parent, mode='determinate')
        self.progress.grid(row=row + 1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # Status
        self.status_label = ttk.Label(parent, text=self.main_app.i18n.get('loading_model'), font=("Arial", 9))
        self.status_label.grid(row=row + 2, column=0, pady=(0, 10))

        return row + 3

    def refresh_ui(self):
        """Odświeża wszystkie teksty w interfejsie po zmianie języka"""
        # Header
        if self.title_label:
            self.title_label.config(text=self.main_app.i18n.get('window_title'))
        if self.subtitle_label:
            self.subtitle_label.config(text=self.main_app.i18n.get('subtitle'))
        if self.language_button:
            self.language_button.config(text=self.main_app.i18n.get('toggle_language'))
        if self.theme_button:
            self.theme_button.config(text=self.main_app.i18n.get('toggle_theme'))

        # Labels
        if self.input_label:
            self.input_label.config(text=self.main_app.i18n.get('input_folder_label'))
        if self.output_label:
            self.output_label.config(text=self.main_app.i18n.get('output_folder_label'))
        if self.input_browse_button:
            self.input_browse_button.config(text=self.main_app.i18n.get('browse'))
        if self.output_browse_button:
            self.output_browse_button.config(text=self.main_app.i18n.get('browse'))

        # Configuration
        if self.config_frame:
            self.config_frame.config(text=self.main_app.i18n.get('configuration'))
        if self.confidence_text_label:
            self.confidence_text_label.config(text=self.main_app.i18n.get('confidence_threshold'))
        if self.verbose_check:
            self.verbose_check.config(text=self.main_app.i18n.get('verbose_logs'))

        # Description
        if self.description_label:
            self.description_label.config(text=self.main_app.i18n.get('description'))

        # Processing controls
        if self.filter_button:
            self.filter_button.config(text=self.main_app.i18n.get('start_classification'))

        # Sprawdź czy model jest gotowy i zaktualizuj status
        if self.main_app.classifier.is_loaded():
            self.update_model_status(self.main_app.i18n.get('model_ready'), "green")
            self.update_status(self.main_app.i18n.get('select_folders'), "blue")

    # Metody do aktualizacji interfejsu
    def update_model_status(self, text, color="black"):
        """Aktualizuje status modelu"""
        if self.model_status:
            self.model_status.config(text=text, foreground=color)

    def update_status(self, text, color="black"):
        """Aktualizuje status główny"""
        if self.status_label:
            self.status_label.config(text=text, foreground=color)

    def update_progress(self, value, status_text):
        """Aktualizuje pasek postępu i status"""
        if self.progress:
            self.progress['value'] = value
        self.update_status(status_text, "orange")

    def update_confidence_display(self, value):
        """Aktualizuje wyświetlanie wartości pewności"""
        if self.confidence_label:
            self.confidence_label.config(text=f"{value:.2f}")

    def enable_filter_button(self):
        """Włącza przycisk filtrowania"""
        if self.filter_button:
            self.filter_button.config(state="normal")

    def disable_filter_button(self):
        """Wyłącza przycisk filtrowania"""
        if self.filter_button:
            self.filter_button.config(state="disabled")

    def start_processing(self):
        """Ustawia interfejs w tryb przetwarzania"""
        self.disable_filter_button()
        if self.progress:
            self.progress.configure(mode='determinate', value=0)
        self.update_status(self.main_app.i18n.get('analyzing_images'), "orange")

    def finish_processing(self):
        """Kończy tryb przetwarzania"""
        if self.progress:
            self.progress['value'] = 0
        self.enable_filter_button()
        self.update_status(self.main_app.i18n.get('ready_for_next'), "blue")
