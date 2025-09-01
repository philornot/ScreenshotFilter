import logging
import os
import shutil
import threading
import time
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox
from tkinter import ttk

from PIL import Image


# Konfiguracja logowania
def setup_logging():
    """Konfiguruje system logowania"""
    log_filename = f"screenshot_filter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()  # Także do konsoli
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info("=== CLIP Screenshot Filter Started ===")
    logger.info(f"Log file: {log_filename}")
    return logger


class CLIPScreenshotFilter:
    def __init__(self, root):
        self.root = root
        self.root.title("CLIP Screenshot Filter (ML)")
        self.root.geometry("600x400")
        self.root.resizable(False, False)

        self.folder_path = tk.StringVar()
        self.logger = setup_logging()
        self.clip_model = None
        self.clip_processor = None

        self.create_widgets()
        self.load_clip_model()

    def create_widgets(self):
        # Główna ramka
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Tytuł
        title_label = ttk.Label(main_frame, text="CLIP Screenshot Filter (ML)",
                                font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        subtitle_label = ttk.Label(main_frame, text="Wykorzystuje AI do inteligentnej klasyfikacji obrazów",
                                   font=("Arial", 10), foreground="gray")
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))

        # Status modelu
        self.model_status = ttk.Label(main_frame, text="Ładowanie modelu CLIP...",
                                      font=("Arial", 10, "italic"), foreground="orange")
        self.model_status.grid(row=2, column=0, columnspan=2, pady=(0, 15))

        # Wybór folderu
        folder_label = ttk.Label(main_frame, text="Folder ze screenshotami:")
        folder_label.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))

        folder_frame = ttk.Frame(main_frame)
        folder_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        self.folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_path,
                                      width=60, state="readonly")
        self.folder_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))

        browse_button = ttk.Button(folder_frame, text="Przeglądaj",
                                   command=self.browse_folder)
        browse_button.grid(row=0, column=1)

        folder_frame.columnconfigure(0, weight=1)

        # Opcje konfiguracji
        config_frame = ttk.LabelFrame(main_frame, text="Konfiguracja", padding="10")
        config_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        # Próg pewności
        ttk.Label(config_frame, text="Próg pewności (0.0-1.0):").grid(row=0, column=0, sticky=tk.W)
        self.confidence_var = tk.DoubleVar(value=0.6)
        confidence_scale = ttk.Scale(config_frame, from_=0.0, to=1.0,
                                     variable=self.confidence_var, orient="horizontal", length=200)
        confidence_scale.grid(row=0, column=1, padx=(10, 0))

        self.confidence_label = ttk.Label(config_frame, text="0.60")
        self.confidence_label.grid(row=0, column=2, padx=(5, 0))

        confidence_scale.configure(command=self.update_confidence_label)

        # Checkbox dla szczegółowych logów
        self.verbose_logs = tk.BooleanVar(value=True)
        verbose_check = ttk.Checkbutton(config_frame, text="Szczegółowe logi",
                                        variable=self.verbose_logs)
        verbose_check.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))

        # Opis działania
        description_label = ttk.Label(main_frame,
                                      text="CLIP AI przeanalizuje obrazy i sklasyfikuje je jako:\n"
                                           "'clean_images' - normalne zdjęcia, obrazki, memy\n"
                                           "'code_screenshots' - screenshoty kodu, IDE, terminali\n"
                                           "Wyższa pewność = bardziej rygorystyczna klasyfikacja",
                                      justify=tk.CENTER, foreground="darkblue")
        description_label.grid(row=6, column=0, columnspan=2, pady=(0, 15))

        # Przycisk uruchomienia
        self.filter_button = ttk.Button(main_frame, text="Uruchom klasyfikację AI",
                                        command=self.start_filtering, state="disabled")
        self.filter_button.grid(row=7, column=0, columnspan=2, pady=(0, 15))

        # Pasek postępu
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # Status
        self.status_label = ttk.Label(main_frame, text="Ładowanie modelu...",
                                      foreground="blue")
        self.status_label.grid(row=9, column=0, columnspan=2)

        main_frame.columnconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def update_confidence_label(self, value):
        """Aktualizuje label z wartością progu pewności"""
        self.confidence_label.config(text=f"{float(value):.2f}")

    def load_clip_model(self):
        """Ładuje model CLIP w osobnym wątku"""

        def load_model():
            try:
                self.logger.info("Rozpoczęcie ładowania modelu CLIP...")

                # Import bibliotek (może zająć chwilę przy pierwszym uruchomieniu)
                import torch
                from transformers import CLIPProcessor, CLIPModel

                self.logger.info("Biblioteki załadowane, ładowanie modelu...")

                # Ładuj model (przy pierwszym uruchomieniu pobiera ~1.7GB)
                model_name = "openai/clip-vit-base-patch32"
                self.clip_model = CLIPModel.from_pretrained(model_name)
                self.clip_processor = CLIPProcessor.from_pretrained(model_name)

                self.logger.info("Model CLIP załadowany pomyślnie!")

                # Aktualizuj GUI w głównym wątku
                self.root.after(0, self._on_model_loaded)

            except ImportError as e:
                error_msg = "Brakujące biblioteki! Zainstaluj: pip install torch transformers"
                self.logger.error(f"ImportError: {e}")
                self.root.after(0, lambda: self._on_model_error(error_msg))
            except Exception as e:
                error_msg = f"Błąd ładowania modelu: {str(e)}"
                self.logger.error(f"Model loading error: {e}")
                self.root.after(0, lambda: self._on_model_error(error_msg))

        # Uruchom w osobnym wątku
        thread = threading.Thread(target=load_model)
        thread.daemon = True
        thread.start()

    def _on_model_loaded(self):
        """Callback gdy model został załadowany"""
        self.model_status.config(text="✅ Model CLIP gotowy do pracy!", foreground="green")
        self.status_label.config(text="Wybierz folder aby rozpocząć", foreground="blue")
        self.filter_button.config(state="normal" if self.folder_path.get() else "disabled")

    def _on_model_error(self, error_msg):
        """Callback gdy wystąpił błąd przy ładowaniu modelu"""
        self.model_status.config(text="❌ Błąd ładowania modelu", foreground="red")
        self.status_label.config(text=error_msg, foreground="red")
        messagebox.showerror("Błąd modelu",
                             f"{error_msg}\n\nZainstaluj wymagane biblioteki:\npip install torch transformers")

    def browse_folder(self):
        folder = filedialog.askdirectory(title="Wybierz folder ze screenshotami")
        if folder:
            self.folder_path.set(folder)
            self.logger.info(f"Wybrano folder: {folder}")
            if self.clip_model is not None:
                self.filter_button.config(state="normal")
                self.status_label.config(text="Gotowy do klasyfikacji", foreground="green")

    def start_filtering(self):
        if not self.folder_path.get():
            messagebox.showerror("Błąd", "Najpierw wybierz folder!")
            return

        if self.clip_model is None:
            messagebox.showerror("Błąd", "Model CLIP nie został załadowany!")
            return

        # Uruchom filtrowanie w osobnym wątku
        self.filter_button.config(state="disabled")
        self.progress.configure(mode='determinate')
        self.status_label.config(text="Analizowanie obrazów przez AI...", foreground="orange")

        thread = threading.Thread(target=self.filter_images)
        thread.daemon = True
        thread.start()

    def classify_image_with_clip(self, image_path):
        """Klasyfikuje obraz używając modelu CLIP"""
        try:
            import torch

            # Wczytaj obraz
            image = Image.open(image_path).convert('RGB')

            # Teksty opisujące klasy
            texts = [
                "a screenshot of code in an IDE or text editor",
                "a screenshot of programming code",
                "a terminal or command line interface",
                "a normal photo or colorful image",
                "a regular picture or photograph",
                "a meme or colorful graphic"
            ]

            # Przetwórz przez CLIP
            inputs = self.clip_processor(text=texts, images=image, return_tensors="pt", padding=True)

            with torch.no_grad():
                outputs = self.clip_model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)

            # Prawdopodobieństwa dla każdej klasy
            code_prob = max(probs[0][0].item(), probs[0][1].item(), probs[0][2].item())  # IDE, kod, terminal
            normal_prob = max(probs[0][3].item(), probs[0][4].item(), probs[0][5].item())  # normalne zdjęcia

            confidence = max(code_prob, normal_prob)
            is_code = code_prob > normal_prob

            if self.verbose_logs.get():
                self.logger.info(f"{os.path.basename(image_path)}: "
                                 f"kod={code_prob:.3f}, normalne={normal_prob:.3f}, "
                                 f"klasyfikacja={'KOD' if is_code else 'NORMALNE'}, "
                                 f"pewność={confidence:.3f}")

            return is_code, confidence, {'code_prob': code_prob, 'normal_prob': normal_prob}

        except Exception as e:
            self.logger.error(f"Błąd klasyfikacji {image_path}: {e}")
            return False, 0.0, {}

    def filter_images(self):
        try:
            start_time = time.time()
            input_folder = self.folder_path.get()
            clean_folder = os.path.join(os.path.dirname(input_folder), "clean_images")
            code_folder = os.path.join(os.path.dirname(input_folder), "code_screenshots")
            uncertain_folder = os.path.join(os.path.dirname(input_folder), "uncertain_images")

            self.logger.info(f"Rozpoczęcie klasyfikacji w folderze: {input_folder}")
            self.logger.info(f"Próg pewności: {self.confidence_var.get()}")

            # Utwórz foldery wyjściowe
            for folder in [clean_folder, code_folder, uncertain_folder]:
                if not os.path.exists(folder):
                    os.makedirs(folder)
                    self.logger.info(f"Utworzono folder: {folder}")

            # Obsługiwane formaty obrazów
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}

            # Znajdź wszystkie pliki obrazów
            image_files = []
            for file in os.listdir(input_folder):
                if os.path.splitext(file.lower())[1] in image_extensions:
                    image_files.append(file)

            if not image_files:
                error_msg = "Nie znaleziono obrazów w wybranym folderze!"
                self.logger.warning(error_msg)
                self.root.after(0, lambda: self.show_result(error_msg))
                return

            self.logger.info(f"Znaleziono {len(image_files)} obrazów do klasyfikacji")

            # Statystyki
            clean_images = 0
            code_images = 0
            uncertain_images = 0
            total_images = len(image_files)
            confidence_threshold = self.confidence_var.get()

            # Przetwórz każdy obraz
            for i, filename in enumerate(image_files):
                try:
                    file_path = os.path.join(input_folder, filename)

                    # Aktualizuj progress bar i status
                    progress_value = (i + 1) / total_images * 100
                    self.root.after(0, lambda p=progress_value, i=i, total=total_images:
                    self.update_progress(p, f"Przetwarzanie: {i + 1}/{total}"))

                    # Klasyfikuj przez CLIP
                    is_code, confidence, details = self.classify_image_with_clip(file_path)

                    # Zdecyduj o klasyfikacji na podstawie pewności
                    if confidence >= confidence_threshold:
                        if is_code:
                            dest_folder = code_folder
                            code_images += 1
                            category = "KOD"
                        else:
                            dest_folder = clean_folder
                            clean_images += 1
                            category = "CZYSTE"
                    else:
                        dest_folder = uncertain_folder
                        uncertain_images += 1
                        category = "NIEPEWNE"

                    # Skopiuj plik
                    dest_path = os.path.join(dest_folder, filename)
                    shutil.copy2(file_path, dest_path)

                    if not self.verbose_logs.get():  # Krótkie logi jeśli verbose wyłączone
                        if i % 50 == 0 or i == total_images - 1:  # Co 50 plików lub ostatni
                            self.logger.info(f"Przetworzono {i + 1}/{total_images} obrazów...")

                except Exception as e:
                    self.logger.error(f"Błąd przetwarzania {filename}: {e}")
                    continue

            # Podsumowanie
            elapsed_time = time.time() - start_time
            self.logger.info("=== PODSUMOWANIE KLASYFIKACJI ===")
            self.logger.info(f"Czas przetwarzania: {elapsed_time:.2f} sekund")
            self.logger.info(f"Prędkość: {total_images / elapsed_time:.1f} obrazów/sekundę")
            self.logger.info(f"Całkowite obrazy: {total_images}")
            self.logger.info(f"Czyste obrazy: {clean_images}")
            self.logger.info(f"Screenshoty kodu: {code_images}")
            self.logger.info(f"Niepewne: {uncertain_images}")

            self.root.after(0, lambda: self.show_result(
                f"✅ Klasyfikacja AI zakończona!\n\n"
                f"📊 STATYSTYKI:\n"
                f"• Przetworzono: {total_images} obrazów\n"
                f"• Czyste obrazy: {clean_images}\n"
                f"• Screenshoty kodu: {code_images}\n"
                f"• Niepewne (niska pewność): {uncertain_images}\n"
                f"• Czas: {elapsed_time:.1f}s ({total_images / elapsed_time:.1f} img/s)\n\n"
                f"📁 FOLDERY:\n"
                f"• Czyste: {clean_folder}\n"
                f"• Kod: {code_folder}\n"
                f"• Niepewne: {uncertain_folder}\n\n"
                f"💡 TIP: Sprawdź folder 'uncertain_images'\n"
                f"jeśli chcesz ręcznie sklasyfikować obrazy\n"
                f"o niskiej pewności AI."))

        except Exception as e:
            error_msg = f"Wystąpił błąd podczas klasyfikacji: {str(e)}"
            self.logger.error(error_msg)
            self.root.after(0, lambda: self.show_result(error_msg))

    def update_progress(self, value, status_text):
        """Aktualizuje pasek postępu i status"""
        self.progress['value'] = value
        self.status_label.config(text=status_text)

    def show_result(self, message):
        self.progress['value'] = 0
        self.filter_button.config(state="normal")
        self.status_label.config(text="Gotowy do kolejnej klasyfikacji", foreground="blue")
        messagebox.showinfo("Wyniki klasyfikacji AI", message)


def main():
    """Główna funkcja programu"""
    try:
        root = tk.Tk()
        app = CLIPScreenshotFilter(root)
        root.mainloop()
    except Exception as e:
        logging.error(f"Krytyczny błąd aplikacji: {e}")
        messagebox.showerror("Błąd krytyczny", f"Wystąpił nieoczekiwany błąd:\n{e}")


if __name__ == "__main__":
    main()
