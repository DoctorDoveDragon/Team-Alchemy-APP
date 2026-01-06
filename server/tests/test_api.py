import pytest
from httpx import AsyncClient, ASGITransport
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session


# Test database setup
@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
async def client_fixture(session: Session):
    """Create test client with test database"""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint"""
    response = await client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "team-alchemy-app"


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test user registration"""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123"
    }
    response = await client.post("/api/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "id" in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_user(client: AsyncClient):
    """Test registering duplicate user fails"""
    user_data = {
        "email": "test2@example.com",
        "username": "testuser2",
        "password": "testpass123"
    }
    # First registration should succeed
    response1 = await client.post("/api/auth/register", json=user_data)
    assert response1.status_code == 200
    
    # Second registration should fail
    response2 = await client.post("/api/auth/register", json=user_data)
    assert response2.status_code == 400


@pytest.mark.asyncio
async def test_login_user(client: AsyncClient):
    """Test user login"""
    # First register a user
    user_data = {
        "email": "test3@example.com",
        "username": "testuser3",
        "password": "testpass123"
    }
    await client.post("/api/auth/register", json=user_data)
    
    # Then login
    login_data = {
        "username": "testuser3",
        "password": "testpass123"
    }
    response = await client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test login with invalid credentials fails"""
    login_data = {
        "username": "nonexistent",
        "password": "wrongpass"
    }
    response = await client.post("/api/auth/login", json=login_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_document_authenticated(client: AsyncClient):
    """Test creating a document with authentication"""
    # Register and login
    user_data = {
        "email": "test4@example.com",
        "username": "testuser4",
        "password": "testpass123"
    }
    await client.post("/api/auth/register", json=user_data)
    
    login_response = await client.post("/api/auth/login", json={
        "username": "testuser4",
        "password": "testpass123"
    })
    token = login_response.json()["access_token"]
    
    # Create document
    doc_data = {
        "title": "Test Document",
        "content": "This is test content",
        "citation_style": "APA"
    }
    response = await client.post(
        "/api/documents/",
        json=doc_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == doc_data["title"]
    assert data["content"] == doc_data["content"]
    assert data["citation_style"] == doc_data["citation_style"]
    assert "id" in data


@pytest.mark.asyncio
async def test_create_document_unauthenticated(client: AsyncClient):
    """Test creating a document without authentication fails"""
    doc_data = {
        "title": "Test Document",
        "content": "This is test content",
        "citation_style": "APA"
    }
    response = await client.post("/api/documents/", json=doc_data)
    assert response.status_code == 401
