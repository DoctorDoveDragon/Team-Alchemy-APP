"""
Integration tests for assessment API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from team_alchemy.data.models import Base
from team_alchemy.core.assessment.models import (
    AssessmentORM,
    QuestionORM,
    ResponseORM,
    QuestionType,
)
from team_alchemy.data.repository import get_db


# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_assessment.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """Create test client with database override."""
    from main import app

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def sample_assessment(db_session):
    """Create a sample assessment for testing."""
    assessment = AssessmentORM(
        title="Personality Assessment",
        description="A test personality assessment",
        version="1.0.0",
        status="draft",
    )
    db_session.add(assessment)
    db_session.commit()
    db_session.refresh(assessment)
    return assessment


@pytest.fixture
def sample_questions(db_session):
    """Create sample questions for testing."""
    questions = [
        QuestionORM(
            text="How do you prefer to work?",
            question_type=QuestionType.MULTIPLE_CHOICE.value,
            options=["Alone", "In a team", "Both"],
            category="behavioral",
            weight=1.0,
        ),
        QuestionORM(
            text="Rate your communication skills (0-100)",
            question_type=QuestionType.SCALE.value,
            options=None,
            category="interpersonal",
            weight=1.0,
        ),
        QuestionORM(
            text="How analytical are you?",
            question_type=QuestionType.SCALE.value,
            options=None,
            category="cognitive",
            weight=1.0,
        ),
        QuestionORM(
            text="Describe your work style",
            question_type=QuestionType.TEXT.value,
            options=None,
            category="behavioral",
            weight=0.8,
        ),
        QuestionORM(
            text="How do you handle stress?",
            question_type=QuestionType.MULTIPLE_CHOICE.value,
            options=["Take a break", "Work through it", "Seek help"],
            category="emotional",
            weight=1.0,
        ),
    ]
    for question in questions:
        db_session.add(question)
    db_session.commit()
    for question in questions:
        db_session.refresh(question)
    return questions


@pytest.fixture
def sample_responses(db_session, sample_assessment, sample_questions):
    """Create sample responses for testing."""
    responses = [
        ResponseORM(
            assessment_id=sample_assessment.id,
            question_id=sample_questions[0].id,
            answer="In a team",
            confidence=0.9,
        ),
        ResponseORM(
            assessment_id=sample_assessment.id,
            question_id=sample_questions[1].id,
            answer=75,
            confidence=0.8,
        ),
    ]
    for response in responses:
        db_session.add(response)
    db_session.commit()
    for response in responses:
        db_session.refresh(response)
    return responses


class TestCreateAssessment:
    """Tests for POST /assessments/ endpoint."""

    def test_create_assessment_success(self, client):
        """Test creating a new assessment successfully."""
        assessment_data = {
            "title": "Team Dynamics Assessment",
            "description": "Assesses team collaboration skills",
            "version": "1.0.0",
            "questions": [
                {
                    "text": "Do you prefer working in teams?",
                    "question_type": "multiple_choice",
                    "options": ["Yes", "No", "Sometimes"],
                    "category": "interpersonal",
                    "weight": 1.0,
                },
                {
                    "text": "Rate your leadership skills",
                    "question_type": "scale",
                    "category": "behavioral",
                    "weight": 1.0,
                },
                {
                    "text": "How analytical are you?",
                    "question_type": "scale",
                    "category": "cognitive",
                    "weight": 1.0,
                },
                {
                    "text": "How do you handle conflict?",
                    "question_type": "text",
                    "category": "emotional",
                    "weight": 0.9,
                },
                {
                    "text": "What motivates you?",
                    "question_type": "text",
                    "category": "motivational",
                    "weight": 1.0,
                },
            ],
        }

        response = client.post("/api/v1/assessments/", json=assessment_data)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == assessment_data["title"]
        assert data["description"] == assessment_data["description"]
        assert data["version"] == assessment_data["version"]
        assert "id" in data
        assert "created_at" in data
        assert data["status"] == "draft"

    def test_create_assessment_minimal(self, client):
        """Test creating an assessment with minimal fields."""
        assessment_data = {
            "title": "Minimal Assessment",
            "questions": [
                {
                    "text": f"Question {i}",
                    "question_type": "scale",
                    "category": "cognitive",
                    "weight": 1.0,
                }
                for i in range(1, 6)
            ],
        }

        response = client.post("/api/v1/assessments/", json=assessment_data)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == assessment_data["title"]
        assert data["description"] is None

    def test_create_assessment_too_few_questions(self, client):
        """Test creating an assessment with too few questions fails."""
        assessment_data = {
            "title": "Invalid Assessment",
            "questions": [
                {
                    "text": "Only one question",
                    "question_type": "scale",
                    "category": "cognitive",
                    "weight": 1.0,
                },
            ],
        }

        response = client.post("/api/v1/assessments/", json=assessment_data)

        assert response.status_code == 400
        data = response.json()
        assert "at least" in data["detail"].lower()

    def test_create_assessment_no_title(self, client):
        """Test creating an assessment without title fails."""
        assessment_data = {
            "questions": [
                {
                    "text": f"Question {i}",
                    "question_type": "scale",
                    "category": "cognitive",
                    "weight": 1.0,
                }
                for i in range(1, 6)
            ],
        }

        response = client.post("/api/v1/assessments/", json=assessment_data)

        assert response.status_code == 422  # Validation error


class TestGetAssessment:
    """Tests for GET /assessments/{assessment_id} endpoint."""

    def test_get_assessment_success(self, client, sample_assessment):
        """Test retrieving an assessment by ID successfully."""
        response = client.get(f"/api/v1/assessments/{sample_assessment.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_assessment.id
        assert data["title"] == sample_assessment.title
        assert data["description"] == sample_assessment.description
        assert "created_at" in data
        assert "updated_at" in data

    def test_get_assessment_with_responses(
        self, client, sample_assessment, sample_responses
    ):
        """Test retrieving an assessment with responses."""
        response = client.get(f"/api/v1/assessments/{sample_assessment.id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data["responses"]) == len(sample_responses)

    def test_get_assessment_not_found(self, client):
        """Test retrieving a non-existent assessment returns 404."""
        response = client.get("/api/v1/assessments/99999")

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()


class TestListAssessments:
    """Tests for GET /assessments/ endpoint."""

    def test_list_assessments_empty(self, client):
        """Test listing assessments when none exist."""
        response = client.get("/api/v1/assessments/")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_list_assessments_with_data(self, client, db_session):
        """Test listing assessments with data."""
        # Create multiple assessments
        assessments = [
            AssessmentORM(
                title=f"Assessment {i}",
                description=f"Description {i}",
                version="1.0.0",
            )
            for i in range(1, 6)
        ]
        for assessment in assessments:
            db_session.add(assessment)
        db_session.commit()

        response = client.get("/api/v1/assessments/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

    def test_list_assessments_pagination(self, client, db_session):
        """Test pagination in assessment listing."""
        # Create 10 assessments
        assessments = [
            AssessmentORM(
                title=f"Assessment {i}",
                description=f"Description {i}",
                version="1.0.0",
            )
            for i in range(1, 11)
        ]
        for assessment in assessments:
            db_session.add(assessment)
        db_session.commit()

        # Test skip and limit
        response = client.get("/api/v1/assessments/?skip=2&limit=3")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3


class TestSubmitResponse:
    """Tests for POST /assessments/{assessment_id}/responses endpoint."""

    def test_submit_response_success(
        self, client, sample_assessment, sample_questions
    ):
        """Test submitting a response successfully."""
        response_data = {
            "question_id": sample_questions[0].id,
            "answer": "In a team",
            "confidence": 0.9,
        }

        response = client.post(
            f"/api/v1/assessments/{sample_assessment.id}/responses",
            json=response_data,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["assessment_id"] == sample_assessment.id
        assert data["question_id"] == response_data["question_id"]
        assert data["answer"] == response_data["answer"]
        assert data["confidence"] == response_data["confidence"]
        assert "id" in data
        assert "created_at" in data

    def test_submit_response_no_confidence(
        self, client, sample_assessment, sample_questions
    ):
        """Test submitting a response without confidence."""
        response_data = {
            "question_id": sample_questions[1].id,
            "answer": 80,
        }

        response = client.post(
            f"/api/v1/assessments/{sample_assessment.id}/responses",
            json=response_data,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["confidence"] is None

    def test_submit_response_assessment_not_found(self, client, sample_questions):
        """Test submitting a response to non-existent assessment fails."""
        response_data = {
            "question_id": sample_questions[0].id,
            "answer": "Test",
        }

        response = client.post(
            "/api/v1/assessments/99999/responses",
            json=response_data,
        )

        assert response.status_code == 404
        data = response.json()
        assert "assessment" in data["detail"].lower()
        assert "not found" in data["detail"].lower()

    def test_submit_response_question_not_found(self, client, sample_assessment):
        """Test submitting a response to non-existent question fails."""
        response_data = {
            "question_id": 99999,
            "answer": "Test",
        }

        response = client.post(
            f"/api/v1/assessments/{sample_assessment.id}/responses",
            json=response_data,
        )

        assert response.status_code == 404
        data = response.json()
        assert "question" in data["detail"].lower()
        assert "not found" in data["detail"].lower()

    def test_submit_response_invalid_confidence(
        self, client, sample_assessment, sample_questions
    ):
        """Test submitting a response with invalid confidence fails."""
        response_data = {
            "question_id": sample_questions[0].id,
            "answer": "Test",
            "confidence": 1.5,  # Invalid - must be 0-1
        }

        response = client.post(
            f"/api/v1/assessments/{sample_assessment.id}/responses",
            json=response_data,
        )

        # Pydantic validation returns 422, not 400
        assert response.status_code == 422
        data = response.json()
        # Check that it's a validation error
        assert "detail" in data


class TestCalculateResults:
    """Tests for POST /assessments/{assessment_id}/calculate endpoint."""

    def test_calculate_results_success(
        self, client, sample_assessment, sample_questions, sample_responses
    ):
        """Test calculating assessment results successfully."""
        response = client.post(
            f"/api/v1/assessments/{sample_assessment.id}/calculate"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["assessment_id"] == sample_assessment.id
        assert data["status"] == "completed"
        assert "results" in data
        assert "total_score" in data["results"]
        assert "category_scores" in data["results"]
        assert "trait_scores" in data["results"]
        assert "completion_percentage" in data["results"]

    def test_calculate_results_no_responses(
        self, client, sample_assessment, sample_questions
    ):
        """Test calculating results with no responses."""
        response = client.post(
            f"/api/v1/assessments/{sample_assessment.id}/calculate"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["results"]["total_score"] == 0.0
        assert data["results"]["completion_percentage"] == 0.0

    def test_calculate_results_assessment_not_found(self, client):
        """Test calculating results for non-existent assessment fails."""
        response = client.post("/api/v1/assessments/99999/calculate")

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
