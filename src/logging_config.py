import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logging(level=logging.INFO, log_file=None, verbose=False, quiet=False):
    """Konfiguriert das Logging-System"""
    
    # Log-Level bestimmen
    if quiet:
        level = logging.WARNING
    elif verbose:
        level = logging.DEBUG
    
    # Logger erstellen
    logger = logging.getLogger('evaluation_harness')
    logger.setLevel(level)
    
    # Existierende Handler entfernen
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Formatter erstellen
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File Handler (optional)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Datei immer DEBUG
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Transformers Logging reduzieren
    logging.getLogger('transformers').setLevel(logging.WARNING)
    logging.getLogger('torch').setLevel(logging.WARNING)
    
    return logger


def get_logger(name=None):
    """Gibt einen Logger zurück"""
    if name:
        return logging.getLogger(f'evaluation_harness.{name}')
    return logging.getLogger('evaluation_harness')
