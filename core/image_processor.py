import os
import shutil
import threading
import time


class ImageProcessor:
    def __init__(self, logger):
        self.logger = logger
        self.i18n = None  # Will be set from main app

        # Obsługiwane formaty obrazów
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}

    def process_images(self, config, classifier, progress_callback, complete_callback):
        """Przetwarza obrazy w osobnym wątku"""
        thread = threading.Thread(
            target=self._process_images_thread,
            args=(config, classifier, progress_callback, complete_callback)
        )
        thread.daemon = True
        thread.start()

    def _process_images_thread(self, config, classifier, progress_callback, complete_callback):
        """Główna logika przetwarzania obrazów"""
        try:
            start_time = time.time()
            input_folder = config['input_folder']
            output_folder = config['output_folder']
            confidence_threshold = config['confidence_threshold']
            verbose_logs = config['verbose_logs']

            self.logger.info(f"Rozpoczęcie klasyfikacji w folderze: {input_folder}")
            self.logger.info(f"Folder wyjściowy: {output_folder}")
            self.logger.info(f"Próg pewności: {confidence_threshold}")

            # Utwórz foldery wyjściowe
            clean_folder = os.path.join(output_folder, "clean_images")
            code_folder = os.path.join(output_folder, "code_screenshots")
            uncertain_folder = os.path.join(output_folder, "uncertain_images")

            for folder in [clean_folder, code_folder, uncertain_folder]:
                if not os.path.exists(folder):
                    os.makedirs(folder)
                    self.logger.info(f"Utworzono folder: {folder}")

            # Znajdź wszystkie pliki obrazów
            image_files = self._find_image_files(input_folder)

            if not image_files:
                error_msg = "Nie znaleziono obrazów w wybranym folderze!"
                self.logger.warning(error_msg)
                complete_callback(error_msg)
                return

            self.logger.info(f"Znaleziono {len(image_files)} obrazów do klasyfikacji")

            # Przetwórz obrazy
            stats = self._classify_and_move_images(
                image_files, input_folder, clean_folder, code_folder, uncertain_folder,
                classifier, confidence_threshold, verbose_logs, progress_callback
            )

            # Przygotuj podsumowanie
            elapsed_time = time.time() - start_time
            result_message = self._create_summary_message(stats, elapsed_time,
                                                          clean_folder, code_folder, uncertain_folder)

            self._log_summary(stats, elapsed_time)
            complete_callback(result_message)

        except Exception as e:
            error_msg = f"Wystąpił błąd podczas klasyfikacji: {str(e)}"
            self.logger.error(error_msg)
            complete_callback(error_msg)

    def _find_image_files(self, folder):
        """Znajduje wszystkie pliki obrazów w folderze"""
        image_files = []
        try:
            for file in os.listdir(folder):
                if os.path.splitext(file.lower())[1] in self.image_extensions:
                    image_files.append(file)
        except Exception as e:
            self.logger.error(f"Błąd podczas przeszukiwania folderu {folder}: {e}")

        return image_files

    def _classify_and_move_images(self, image_files, input_folder, clean_folder,
                                  code_folder, uncertain_folder, classifier,
                                  confidence_threshold, verbose_logs, progress_callback):
        """Klasyfikuje i przenosi obrazy do odpowiednich folderów"""
        stats = {
            'clean_images': 0,
            'code_images': 0,
            'uncertain_images': 0,
            'total_images': len(image_files),
            'errors': 0
        }

        for i, filename in enumerate(image_files):
            try:
                file_path = os.path.join(input_folder, filename)

                # Aktualizuj progress bar
                progress_value = (i + 1) / stats['total_images'] * 100
                progress_callback(progress_value, f"Przetwarzanie: {i + 1}/{stats['total_images']}")

                # Klasyfikuj przez CLIP
                is_code, confidence, details = classifier.classify_image(file_path, verbose_logs)

                # Zdecyduj o klasyfikacji na podstawie pewności
                if confidence >= confidence_threshold:
                    if is_code:
                        dest_folder = code_folder
                        stats['code_images'] += 1
                        category = "KOD"
                    else:
                        dest_folder = clean_folder
                        stats['clean_images'] += 1
                        category = "CZYSTE"
                else:
                    dest_folder = uncertain_folder
                    stats['uncertain_images'] += 1
                    category = "NIEPEWNE"

                # Skopiuj plik
                dest_path = os.path.join(dest_folder, filename)
                shutil.copy2(file_path, dest_path)

                if not verbose_logs:  # Krótkie logi jeśli verbose wyłączone
                    if i % 50 == 0 or i == stats['total_images'] - 1:  # Co 50 plików lub ostatni
                        self.logger.info(f"Przetworzono {i + 1}/{stats['total_images']} obrazów...")

            except Exception as e:
                self.logger.error(f"Błąd przetwarzania {filename}: {e}")
                stats['errors'] += 1
                continue

        return stats

    def _create_summary_message(self, stats, elapsed_time, clean_folder, code_folder, uncertain_folder):
        """Tworzy wiadomość podsumowującą"""
        speed = stats['total_images'] / elapsed_time if elapsed_time > 0 else 0

        message = (
            f"✅ Klasyfikacja AI zakończona!\n\n"
            f"📊 STATYSTYKI:\n"
            f"• Przetworzono: {stats['total_images']} obrazów\n"
            f"• Czyste obrazy: {stats['clean_images']}\n"
            f"• Screenshoty kodu: {stats['code_images']}\n"
            f"• Niepewne (niska pewność): {stats['uncertain_images']}\n"
        )

        if stats['errors'] > 0:
            message += f"• Błędy: {stats['errors']}\n"

        message += (
            f"• Czas: {elapsed_time:.1f}s ({speed:.1f} img/s)\n\n"
            f"📁 FOLDERY:\n"
            f"• Czyste: {clean_folder}\n"
            f"• Kod: {code_folder}\n"
            f"• Niepewne: {uncertain_folder}\n\n"
            f"💡 TIP: Sprawdź folder 'uncertain_images'\n"
            f"jeśli chcesz ręcznie sklasyfikować obrazy\n"
            f"o niskiej pewności AI."
        )

        return message

    def _log_summary(self, stats, elapsed_time):
        """Loguje podsumowanie przetwarzania"""
        self.logger.info("=== PODSUMOWANIE KLASYFIKACJI ===")
        self.logger.info(f"Czas przetwarzania: {elapsed_time:.2f} sekund")
        self.logger.info(f"Prędkość: {stats['total_images'] / elapsed_time:.1f} obrazów/sekundę")
        self.logger.info(f"Całkowite obrazy: {stats['total_images']}")
        self.logger.info(f"Czyste obrazy: {stats['clean_images']}")
        self.logger.info(f"Screenshoty kodu: {stats['code_images']}")
        self.logger.info(f"Niepewne: {stats['uncertain_images']}")
        if stats['errors'] > 0:
            self.logger.info(f"Błędy: {stats['errors']}")
