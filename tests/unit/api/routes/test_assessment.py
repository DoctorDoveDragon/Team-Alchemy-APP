"""
Unit tests for assessment API routes.

These tests mock the database layer to test the route logic in isolation.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from fastapi import HTTPException
from datetime import datetime

from team_alchemy.core.assessment.models import (
    Assessment,
    AssessmentCreate,
    AssessmentORM,
    AssessmentStatus,
    Response,
    ResponseBase,
    ResponseORM,
    QuestionORM,
    QuestionBase,
    QuestionType,
)
from team_alchemy.api.routes.assessment import (
    create_assessment,
    get_assessment,
    list_assessments,
    submit_response,
    calculate_results,
)


class TestCreateAssessment:
    """Unit tests for create_assessment endpoint."""

    @pytest.mark.asyncio
    async def test_create_assessment_success(self):
        """Test successful assessment creation."""
        # Mock database session
        mock_db = MagicMock()
        mock_assessment_orm = MagicMock(spec=AssessmentORM)
        mock_assessment_orm.id = 1
        mock_assessment_orm.title = "Test Assessment"
        mock_assessment_orm.to_pydantic.return_value = Assessment(
            id=1,
            title="Test Assessment",
            description="Test Description",
            version="1.0.0",
            status=AssessmentStatus.DRAFT,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            responses=[],
            results=None,
        )
        
        # Setup mock refresh to populate the mock object
        def mock_refresh(obj):
            obj.id = 1
        
        mock_db.refresh = mock_refresh
        mock_db.commit = MagicMock()
        
        # Create assessment data
        assessment_data = AssessmentCreate(
            title="Test Assessment",
            description="Test Description",
            version="1.0.0",
            questions=[
                QuestionBase(
                    text=f"Question {i}",
                    question_type=QuestionType.SCALE,
                    category="cognitive",
                    weight=1.0,
                )
                for i in range(1, 6)
            ],
        )
        
        # Call the endpoint
        with patch("team_alchemy.api.routes.assessment.AssessmentORM", return_value=mock_assessment_orm):
            result = await create_assessment(assessment_data, mock_db)
        
        # Verify
        assert result.id == 1
        assert result.title == "Test Assessment"
        mock_db.add.assert_called()
        mock_db.commit.assert_called()

    @pytest.mark.asyncio
    async def test_create_assessment_validation_fails(self):
        """Test that validation errors are raised."""
        mock_db = MagicMock()
        
        # Create assessment with too few questions
        assessment_data = AssessmentCreate(
            title="Test Assessment",
            description="Test Description",
            version="1.0.0",
            questions=[
                QuestionBase(
                    text="Only one question",
                    question_type=QuestionType.SCALE,
                    category="cognitive",
                    weight=1.0,
                )
            ],
        )
        
        # Call should raise validation error
        with pytest.raises(HTTPException) as exc_info:
            await create_assessment(assessment_data, mock_db)
        
        assert exc_info.value.status_code == 400
        assert "validation" in exc_info.value.detail.lower()


class TestGetAssessment:
    """Unit tests for get_assessment endpoint."""

    @pytest.mark.asyncio
    async def test_get_assessment_success(self):
        """Test successful assessment retrieval."""
        mock_db = MagicMock()
        mock_query = mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        
        mock_assessment_orm = MagicMock(spec=AssessmentORM)
        mock_assessment_orm.to_pydantic.return_value = Assessment(
            id=1,
            title="Test Assessment",
            description="Test Description",
            version="1.0.0",
            status=AssessmentStatus.DRAFT,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            responses=[],
            results=None,
        )
        
        mock_filter.first.return_value = mock_assessment_orm
        
        result = await get_assessment(1, mock_db)
        
        assert result.id == 1
        assert result.title == "Test Assessment"

    @pytest.mark.asyncio
    async def test_get_assessment_not_found(self):
        """Test getting non-existent assessment raises 404."""
        mock_db = MagicMock()
        mock_query = mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            await get_assessment(99999, mock_db)
        
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()


class TestListAssessments:
    """Unit tests for list_assessments endpoint."""

    @pytest.mark.asyncio
    async def test_list_assessments_empty(self):
        """Test listing when no assessments exist."""
        mock_db = MagicMock()
        mock_query = mock_db.query.return_value
        mock_offset = mock_query.offset.return_value
        mock_limit = mock_offset.limit.return_value
        mock_limit.all.return_value = []
        
        result = await list_assessments(0, 100, mock_db)
        
        assert result == []

    @pytest.mark.asyncio
    async def test_list_assessments_with_data(self):
        """Test listing assessments with data."""
        mock_db = MagicMock()
        
        # Create mock assessments
        mock_assessments = []
        for i in range(1, 4):
            mock_orm = MagicMock(spec=AssessmentORM)
            mock_orm.to_pydantic.return_value = Assessment(
                id=i,
                title=f"Assessment {i}",
                description=f"Description {i}",
                version="1.0.0",
                status=AssessmentStatus.DRAFT,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                responses=[],
                results=None,
            )
            mock_assessments.append(mock_orm)
        
        mock_query = mock_db.query.return_value
        mock_offset = mock_query.offset.return_value
        mock_limit = mock_offset.limit.return_value
        mock_limit.all.return_value = mock_assessments
        
        result = await list_assessments(0, 100, mock_db)
        
        assert len(result) == 3
        assert result[0].id == 1
        assert result[1].id == 2

    @pytest.mark.asyncio
    async def test_list_assessments_pagination(self):
        """Test pagination parameters are used."""
        mock_db = MagicMock()
        mock_query = mock_db.query.return_value
        mock_offset = mock_query.offset.return_value
        mock_limit = mock_offset.limit.return_value
        mock_limit.all.return_value = []
        
        await list_assessments(skip=10, limit=20, db=mock_db)
        
        mock_query.offset.assert_called_with(10)
        mock_offset.limit.assert_called_with(20)


class TestSubmitResponse:
    """Unit tests for submit_response endpoint."""

    @pytest.mark.asyncio
    async def test_submit_response_success(self):
        """Test successful response submission."""
        mock_db = MagicMock()
        
        # Mock assessment exists
        mock_assessment = MagicMock(spec=AssessmentORM)
        mock_assessment.id = 1
        
        # Mock question exists
        mock_question = MagicMock(spec=QuestionORM)
        mock_question.id = 1
        
        # Setup query mock to return different values for different calls
        def query_side_effect(model):
            mock_query = MagicMock()
            mock_filter = mock_query.filter.return_value
            if model == AssessmentORM:
                mock_filter.first.return_value = mock_assessment
            elif model == QuestionORM:
                mock_filter.first.return_value = mock_question
            return mock_query
        
        mock_db.query.side_effect = query_side_effect
        
        # Mock response ORM
        mock_response_orm = MagicMock(spec=ResponseORM)
        mock_response_orm.to_pydantic.return_value = Response(
            id=1,
            assessment_id=1,
            question_id=1,
            answer="Test answer",
            confidence=0.9,
            created_at=datetime.utcnow(),
        )
        
        def mock_refresh(obj):
            obj.id = 1
        
        mock_db.refresh = mock_refresh
        
        response_data = ResponseBase(
            question_id=1,
            answer="Test answer",
            confidence=0.9,
        )
        
        with patch("team_alchemy.api.routes.assessment.ResponseORM", return_value=mock_response_orm):
            result = await submit_response(1, response_data, mock_db)
        
        assert result.id == 1
        assert result.assessment_id == 1
        mock_db.add.assert_called()
        mock_db.commit.assert_called()

    @pytest.mark.asyncio
    async def test_submit_response_assessment_not_found(self):
        """Test submitting response to non-existent assessment."""
        mock_db = MagicMock()
        mock_query = mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = None
        
        response_data = ResponseBase(
            question_id=1,
            answer="Test",
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await submit_response(99999, response_data, mock_db)
        
        assert exc_info.value.status_code == 404
        assert "assessment" in exc_info.value.detail.lower()


class TestCalculateResults:
    """Unit tests for calculate_results endpoint."""

    @pytest.mark.asyncio
    async def test_calculate_results_success(self):
        """Test successful results calculation."""
        mock_db = MagicMock()
        
        # Mock assessment
        mock_assessment = MagicMock(spec=AssessmentORM)
        mock_assessment.id = 1
        mock_assessment.to_pydantic.return_value = Assessment(
            id=1,
            title="Test Assessment",
            description="Test",
            version="1.0.0",
            status=AssessmentStatus.IN_PROGRESS,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            responses=[],
            results=None,
        )
        
        # Setup query mocks
        def query_side_effect(model):
            mock_query = MagicMock()
            if model == AssessmentORM:
                mock_filter = mock_query.filter.return_value
                mock_filter.first.return_value = mock_assessment
            elif model == QuestionORM:
                mock_query.all.return_value = []
            return mock_query
        
        mock_db.query.side_effect = query_side_effect
        
        result = await calculate_results(1, mock_db)
        
        assert result["assessment_id"] == 1
        assert result["status"] == "completed"
        assert "results" in result
        mock_db.commit.assert_called()

    @pytest.mark.asyncio
    async def test_calculate_results_not_found(self):
        """Test calculating results for non-existent assessment."""
        mock_db = MagicMock()
        mock_query = mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            await calculate_results(99999, mock_db)
        
        assert exc_info.value.status_code == 404
