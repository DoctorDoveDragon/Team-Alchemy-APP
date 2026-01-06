#!/usr/bin/env python
"""
Load sample data into the database.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from team_alchemy.data.repository import SessionLocal
from team_alchemy.data.models import User, UserProfile, Team
from config.logging_config import setup_logging


def load_sample_assessments():
    """Load sample assessment data."""
    sample_file = Path(__file__).parent.parent / "examples" / "data" / "sample_assessments.json"
    
    if not sample_file.exists():
        return []
        
    with open(sample_file) as f:
        return json.load(f)


def main():
    """Load sample data."""
    logger = setup_logging()
    
    logger.info("Loading sample data into Team Alchemy database...")
    
    db = SessionLocal()
    
    try:
        # Create sample users
        users = [
            User(email="alice@example.com", name="Alice Johnson"),
            User(email="bob@example.com", name="Bob Smith"),
            User(email="carol@example.com", name="Carol Williams"),
        ]
        
        for user in users:
            db.add(user)
        
        db.commit()
        logger.info(f"✓ Created {len(users)} sample users")
        
        # Create sample profiles
        sample_assessments = load_sample_assessments()
        
        for i, assessment in enumerate(sample_assessments):
            if i < len(users):
                profile = UserProfile(
                    user_id=users[i].id,
                    archetype=assessment.get("archetype"),
                    trait_scores=assessment.get("trait_scores"),
                    jungian_type=assessment.get("jungian_type")
                )
                db.add(profile)
        
        db.commit()
        logger.info(f"✓ Created {len(sample_assessments)} sample profiles")
        
        # Create sample team
        team = Team(
            name="Alpha Team",
            description="Sample team for demonstration"
        )
        team.members.extend(users)
        db.add(team)
        db.commit()
        
        logger.info("✓ Created sample team")
        logger.info("✓ Sample data loaded successfully!")
        
        return 0
        
    except Exception as e:
        logger.error(f"✗ Error loading sample data: {e}")
        db.rollback()
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
