class I18nManager:
    def __init__(self, language='pl'):
        self.current_language = language
        self.translations = {
            'pl': {
                # Window
                'window_title': 'CLIP Screenshot Filter (ML)',
                'subtitle': 'Wykorzystuje AI do inteligentnej klasyfikacji obrazów',

                # Model status
                'loading_model': 'Ładowanie modelu CLIP...',
                'model_ready': '✅ Model CLIP gotowy do pracy!',
                'model_error': '❌ Błąd ładowania modelu',

                # Status messages
                'select_folders': 'Wybierz foldery aby rozpocząć',
                'ready_to_classify': 'Gotowy do klasyfikacji',
                'analyzing_images': 'Analizowanie obrazów przez AI...',
                'ready_for_next': 'Gotowy do kolejnej klasyfikacji',

                # UI Labels
                'input_folder_label': 'Folder wejściowy (screenshoty):',
                'output_folder_label': 'Folder wyjściowy (gdzie zapisać wyniki):',
                'browse': 'Przeglądaj',
                'configuration': 'Konfiguracja',
                'confidence_threshold': 'Próg pewności (0.0-1.0):',
                'verbose_logs': 'Szczegółowe logi',
                'toggle_theme': '🌓 Przełącz motyw',
                'toggle_language': '🌐 EN',
                'start_classification': '🚀 Uruchom klasyfikację AI',

                # Dialog titles
                'select_input_folder': 'Wybierz folder ze screenshotami',
                'select_output_folder': 'Wybierz folder wyjściowy',
                'classification_results': 'Wyniki klasyfikacji AI',
                'error': 'Błąd',

                # Error messages
                'select_input_first': 'Najpierw wybierz folder wejściowy!',
                'select_output_first': 'Najpierw wybierz folder wyjściowy!',
                'model_not_loaded': 'Model CLIP nie został załadowany!',
                'install_libraries': 'Zainstaluj wymagane biblioteki:\npip install torch transformers',

                # Description
                'description': ("CLIP AI przeanalizuje obrazy i sklasyfikuje je jako:\n"
                                "'clean_images' - normalne zdjęcia, obrazki, memy\n"
                                "'code_screenshots' - screenshoty kodu, IDE, terminali\n"
                                "'uncertain_images' - obrazy z niską pewnością klasyfikacji\n\n"
                                "Wyższa pewność = bardziej rygorystyczna klasyfikacja")
            },
            'en': {
                # Window
                'window_title': 'CLIP Screenshot Filter (ML)',
                'subtitle': 'Uses AI for intelligent image classification',

                # Model status
                'loading_model': 'Loading CLIP model...',
                'model_ready': '✅ CLIP Model ready to work!',
                'model_error': '❌ Model loading error',

                # Status messages
                'select_folders': 'Select folders to begin',
                'ready_to_classify': 'Ready to classify',
                'analyzing_images': 'Analyzing images with AI...',
                'ready_for_next': 'Ready for next classification',

                # UI Labels
                'input_folder_label': 'Input folder (screenshots):',
                'output_folder_label': 'Output folder (where to save results):',
                'browse': 'Browse',
                'configuration': 'Configuration',
                'confidence_threshold': 'Confidence threshold (0.0-1.0):',
                'verbose_logs': 'Verbose logs',
                'toggle_theme': '🌓 Toggle theme',
                'toggle_language': '🌐 PL',
                'start_classification': '🚀 Start AI classification',

                # Dialog titles
                'select_input_folder': 'Select screenshots folder',
                'select_output_folder': 'Select output folder',
                'classification_results': 'AI Classification Results',
                'error': 'Error',

                # Error messages
                'select_input_first': 'First select input folder!',
                'select_output_first': 'First select output folder!',
                'model_not_loaded': 'CLIP model not loaded!',
                'install_libraries': 'Install required libraries:\npip install torch transformers',

                # Description
                'description': ("CLIP AI will analyze images and classify them as:\n"
                                "'clean_images' - normal photos, pictures, memes\n"
                                "'code_screenshots' - code screenshots, IDE, terminals\n"
                                "'uncertain_images' - images with low classification confidence\n\n"
                                "Higher confidence = more strict classification")
            }
        }

    def get(self, key):
        """Pobiera przetłumaczony tekst"""
        return self.translations.get(self.current_language, {}).get(
            key, self.translations['pl'].get(key, key))

    def set_language(self, language):
        """Ustawia język"""
        if language in self.translations:
            self.current_language = language
