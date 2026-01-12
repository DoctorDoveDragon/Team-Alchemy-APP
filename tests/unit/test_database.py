"""
Integration tests for database repository with different database backends.
"""

import pytest
import os
import tempfile
from pathlib import Path


def test_init_db_with_sqlite():
    """Test database initialization with SQLite."""
    # Use a temporary database file
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp_db_path = tmp.name
    
    try:
        # Set DATABASE_URL to use temp file
        os.environ["DATABASE_URL"] = f"sqlite:///{tmp_db_path}"
        
        # Re-import to pick up new DATABASE_URL
        import importlib
        import team_alchemy.data.repository as repo_module
        importlib.reload(repo_module)
        
        # Initialize database
        repo_module.init_db()
        
        # Verify database file was created
        assert Path(tmp_db_path).exists()
        
        # Verify we can get a session
        db_gen = repo_module.get_db()
        db = next(db_gen)
        assert db is not None
        
        # Close session
        try:
            next(db_gen)
        except StopIteration:
            pass
            
    finally:
        # Cleanup
        if Path(tmp_db_path).exists():
            Path(tmp_db_path).unlink()


def test_get_db_session_lifecycle():
    """Test database session lifecycle (create, use, close)."""
    from team_alchemy.data import repository
    
    # Get a session
    db_gen = repository.get_db()
    db = next(db_gen)
    
    # Verify session is usable
    assert db is not None
    assert hasattr(db, 'query')
    assert hasattr(db, 'commit')
    assert hasattr(db, 'close')
    
    # Close session
    try:
        next(db_gen)
    except StopIteration:
        pass


def test_database_url_configuration():
    """Test that DATABASE_URL is properly configured."""
    from team_alchemy.data import repository
    
    # DATABASE_URL should be set from environment or default to SQLite
    assert repository.DATABASE_URL is not None
    assert isinstance(repository.DATABASE_URL, str)
    assert any(db in repository.DATABASE_URL for db in ['sqlite', 'postgresql', 'postgres', 'mysql'])


def test_engine_creation():
    """Test that database engine is created."""
    from team_alchemy.data import repository
    
    # Engine should exist
    assert repository.engine is not None
    
    # Engine should have expected attributes
    assert hasattr(repository.engine, 'connect')
    assert hasattr(repository.engine, 'dispose')


def test_session_factory_creation():
    """Test that session factory is created."""
    from team_alchemy.data import repository
    
    # SessionLocal should exist and be callable
    assert repository.SessionLocal is not None
    assert callable(repository.SessionLocal)
    
    # Should be able to create a session
    session = repository.SessionLocal()
    assert session is not None
    session.close()

