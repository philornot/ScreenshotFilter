import logging
import tkinter as tk

from gui.main_window import CLIPScreenshotFilterGUI
from utils.logger import setup_logging


def main():
    """Główna funkcja programu"""
    try:
        # Konfiguruj logowanie
        logger = setup_logging()
        logger.info("=== CLIP Screenshot Filter Started ===")

        # Utwórz główne okno
        root = tk.Tk()
        app = CLIPScreenshotFilterGUI(root, logger)

        # Uruchom aplikację
        root.mainloop()

    except Exception as e:
        logging.error(f"Krytyczny błąd aplikacji: {e}")
        tk.messagebox.showerror("Błąd krytyczny", f"Wystąpił nieoczekiwany błąd:\n{e}")


if __name__ == "__main__":
    main()
