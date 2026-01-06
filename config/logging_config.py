"""
Logging configuration for Team Alchemy.
"""

import logging
import logging.config
import sys
from typing import Dict, Any


def get_logging_config(log_level: str = "INFO", log_format: str = "json") -> Dict[str, Any]:
    """
    Get logging configuration dictionary.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Format style ("json" or "text")
        
    Returns:
        Logging configuration dictionary
    """
    
    if log_format == "json":
        formatter_config = {
            "format": '{"time": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "message": "%(message)s"}',
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    else:
        formatter_config = {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": formatter_config,
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "default",
                "stream": sys.stdout,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "default",
                "filename": "team_alchemy.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
        },
        "loggers": {
            "team_alchemy": {
                "level": log_level,
                "handlers": ["console", "file"],
                "propagate": False,
            },
        },
        "root": {
            "level": log_level,
            "handlers": ["console"],
        },
    }


def setup_logging(log_level: str = "INFO", log_format: str = "json"):
    """
    Setup logging configuration.
    
    Args:
        log_level: Logging level
        log_format: Format style
    """
    config = get_logging_config(log_level, log_format)
    logging.config.dictConfig(config)
    
    logger = logging.getLogger("team_alchemy")
    logger.info(f"Logging initialized at {log_level} level")
    
    return logger
