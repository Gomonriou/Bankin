import logging
from logging.handlers import RotatingFileHandler
import os

os.makedirs("logs", exist_ok=True)
log_file = "logs/app.log"
logger = logging.getLogger("app")

if not logger.hasHandlers():  # évite les doublons
    logger.setLevel(logging.DEBUG) 

    # Handler fichier (rotation)
    file_handler = RotatingFileHandler(log_file, maxBytes=5_000_000, backupCount=5)
    file_handler.setLevel(logging.INFO)

    # Handler console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Format commun
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Ajouter handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
