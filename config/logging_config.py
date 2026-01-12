"""
Logging configuration for Team Alchemy.
"""

import logging
import logging.config
import sys
import os
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
    
    # Determine if we're in production based on environment
    environment = os.getenv("ENVIRONMENT", "development").lower()
    is_production = environment == "production"
    
    # In production, reduce verbosity for third-party loggers
    third_party_level = "WARNING" if is_production else log_level
    
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
    
    config = {
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
        },
        "loggers": {
            "team_alchemy": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False,
            },
            # Reduce verbosity for third-party libraries in production
            "uvicorn": {
                "level": third_party_level,
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "WARNING" if is_production else "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.error": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False,
            },
            "fastapi": {
                "level": third_party_level,
                "handlers": ["console"],
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "level": "WARNING" if is_production else log_level,
                "handlers": ["console"],
                "propagate": False,
            },
        },
        "root": {
            "level": log_level,
            "handlers": ["console"],
        },
    }
    
    # Only add file handler in non-production environments to avoid disk usage issues
    if not is_production:
        config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": log_level,
            "formatter": "default",
            "filename": "team_alchemy.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        }
        config["loggers"]["team_alchemy"]["handlers"].append("file")
    
    return config


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
