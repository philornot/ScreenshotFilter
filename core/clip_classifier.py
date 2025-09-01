import os
import threading

from PIL import Image


class CLIPClassifier:
    def __init__(self, logger):
        self.logger = logger
        self.clip_model = None
        self.clip_processor = None
        self._model_loaded = False

    def is_loaded(self):
        """Sprawdza czy model jest załadowany"""
        return self._model_loaded

    def load_model(self, success_callback, error_callback):
        """Ładuje model CLIP w osobnym wątku"""

        def load_model_thread():
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

                self._model_loaded = True
                self.logger.info("Model CLIP załadowany pomyślnie!")

                # Wywołaj callback sukcesu w głównym wątku
                if success_callback:
                    success_callback()

            except ImportError as e:
                error_msg = "Brakujące biblioteki! Zainstaluj: pip install torch transformers"
                self.logger.error(f"ImportError: {e}")
                if error_callback:
                    error_callback(error_msg)

            except Exception as e:
                error_msg = f"Błąd ładowania modelu: {str(e)}"
                self.logger.error(f"Model loading error: {e}")
                if error_callback:
                    error_callback(error_msg)

        # Uruchom w osobnym wątku
        thread = threading.Thread(target=load_model_thread)
        thread.daemon = True
        thread.start()

    def classify_image(self, image_path, verbose=True):
        """Klasyfikuje obraz używając modelu CLIP"""
        if not self._model_loaded:
            raise RuntimeError("Model CLIP nie został załadowany")

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

            if verbose:
                self.logger.info(f"{os.path.basename(image_path)}: "
                                 f"kod={code_prob:.3f}, normalne={normal_prob:.3f}, "
                                 f"klasyfikacja={'KOD' if is_code else 'NORMALNE'}, "
                                 f"pewność={confidence:.3f}")

            return is_code, confidence, {'code_prob': code_prob, 'normal_prob': normal_prob}

        except Exception as e:
            self.logger.error(f"Błąd klasyfikacji {image_path}: {e}")
            return False, 0.0, {}
