import logging
import os
from datetime import datetime


def setup_logging():
    """Konfiguruje system logowania"""
    # Utwórz folder logs jeśli nie istnieje
    if not os.path.exists("logs"):
        os.makedirs("logs")

    log_filename = os.path.join("logs", f"screenshot_filter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()  # Także do konsoli
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Log file: {log_filename}")
    return logger
