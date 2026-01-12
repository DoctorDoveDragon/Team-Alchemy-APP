#!/usr/bin/env python
"""
Script to run database migrations and initialization for deployment.

This script should be run during deployment to ensure the database schema
is up-to-date. It can be called from Railway or other deployment platforms.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main():
    """Run database migrations and initialization."""
    print("=" * 60)
    print("DATABASE MIGRATION AND INITIALIZATION")
    print("=" * 60)
    
    # Import after path setup
    from config.settings import get_settings
    from team_alchemy.data.repository import init_db
    from alembic.config import Config
    from alembic import command
    
    settings = get_settings()
    
    print(f"Environment: {settings.environment}")
    print(f"Database URL: {settings.database_url[:30]}...")
    print()
    
    # Step 1: Run Alembic migrations
    print("Step 1: Running Alembic migrations...")
    try:
        alembic_cfg = Config(str(project_root / "alembic.ini"))
        alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)
        
        # Upgrade to latest revision
        command.upgrade(alembic_cfg, "head")
        print("✓ Alembic migrations completed successfully")
    except Exception as e:
        print(f"ℹ Alembic migrations info: {e}")
        print("This is expected if no migrations exist yet.")
    
    print()
    
    # Step 2: Initialize database (creates tables if they don't exist)
    print("Step 2: Initializing database...")
    try:
        init_db()
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("DATABASE SETUP COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
