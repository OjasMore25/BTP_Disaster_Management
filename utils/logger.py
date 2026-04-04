"""
Logging utility for the disaster response system
"""
import logging
from pathlib import Path
from datetime import datetime
from config.settings import LOG_LEVEL, LOG_FILE


class Logger:
    """Custom logger for the application"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance
    
    def _initialize_logger(self):
        """Initialize logger"""
        self.logger = logging.getLogger('disaster_rag')
        self.logger.setLevel(getattr(logging, LOG_LEVEL))
        
        # Create logs directory if not exists
        log_path = Path(LOG_FILE)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # File handler
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(getattr(logging, LOG_LEVEL))
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, LOG_LEVEL))
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Set encoding to UTF-8 for both handlers
        try:
            file_handler.setStream(open(log_path, 'w', encoding='utf-8'))
        except:
            pass
    
    def info(self, message: str):
        """Log info message"""
        # Replace special Unicode characters that Windows console can't handle
        message = str(message).replace('\u2713', '[OK]').replace('\u2717', '[FAIL]')
        self.logger.info(message)
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self.logger.error(message, **kwargs)
    
    def critical(self, message: str):
        """Log critical message"""
        self.logger.critical(message)


def get_logger() -> Logger:
    """Get logger instance"""
    return Logger()
