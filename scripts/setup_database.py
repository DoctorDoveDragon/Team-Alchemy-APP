#!/usr/bin/env python
"""
Database setup script for Team Alchemy.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from team_alchemy.data.repository import init_db, engine
from team_alchemy.data.models import Base
from config.settings import settings
from config.logging_config import setup_logging


def main():
    """Setup the database."""
    logger = setup_logging()
    
    logger.info("Setting up Team Alchemy database...")
    logger.info(f"Database URL: {settings.database_url}")
    
    try:
        # Create all tables
        init_db()
        
        logger.info("✓ Database tables created successfully!")
        logger.info(f"✓ Tables: {', '.join(Base.metadata.tables.keys())}")
        
        return 0
    except Exception as e:
        logger.error(f"✗ Error setting up database: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
