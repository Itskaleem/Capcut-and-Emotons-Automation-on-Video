"""
Logger Utility
Provides consistent logging across the application
"""

import logging
import sys
from datetime import datetime
from src.config import Config

class Logger:
    """Application logger"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.logger = logging.getLogger('VideoProcessor')
        self.logger.setLevel(logging.DEBUG if Config.VERBOSE_LOGGING else logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG if Config.VERBOSE_LOGGING else logging.INFO)
        
        # Format
        formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
        self._initialized = True
    
    def info(self, message: str, emoji: str = "ℹ️"):
        """Log info message"""
        self.logger.info(f"{emoji} {message}")
    
    def success(self, message: str):
        """Log success message"""
        self.logger.info(f"✅ {message}")
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(f"⚠️ {message}")
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(f"❌ {message}")
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(f"🔍 {message}")
    
    def step(self, step_number: int, message: str):
        """Log step message"""
        self.logger.info(f"{'='*60}")
        self.logger.info(f"Step {step_number}: {message}")
        self.logger.info(f"{'='*60}")
    
    def section(self, message: str):
        """Log section header"""
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"  {message}")
        self.logger.info(f"{'='*60}\n")

# Singleton instance
logger = Logger()
