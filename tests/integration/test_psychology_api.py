"""
Integration tests for psychology API endpoints.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_get_jungian_profile():
    """Test getting a Jungian profile by MBTI type."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/psychology/jungian/profile/INTJ")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["mbti_type"] == "INTJ"
        assert "function_stack" in data
        assert len(data["function_stack"]) == 4
        assert "archetype_affinity" in data
        assert "strengths" in data
        assert "shadow" in data


@pytest.mark.asyncio
async def test_get_jungian_profile_invalid_type():
    """Test getting a Jungian profile with invalid MBTI type."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/psychology/jungian/profile/INVALID")
        
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_check_jungian_compatibility():
    """Test checking compatibility between two MBTI types."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/psychology/jungian/compatibility/INTJ/ENFP")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "compatible" in data
        assert "type1" in data
        assert "type2" in data
        assert "compatibility_score" in data


@pytest.mark.asyncio
async def test_list_mbti_types():
    """Test listing all MBTI types."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/psychology/jungian/types")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "types" in data
        assert len(data["types"]) == 16
        
        # Check structure of first type
        first_type = data["types"][0]
        assert "mbti_type" in first_type
        assert "archetype_affinity" in first_type
        assert "strengths" in first_type


@pytest.mark.asyncio
async def test_analyze_defense_mechanisms():
    """Test analyzing defense mechanisms."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        request_data = {
            "behaviors": [
                "justifies behavior",
                "creates logical explanations",
                "refuses to acknowledge reality"
            ],
            "stress_responses": {}
        }
        
        response = await client.post(
            "/api/v1/psychology/freudian/defense-mechanisms",
            json=request_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "defense_profiles" in data
        assert "defensiveness_level" in data
        assert "defense_maturity" in data
        assert "recommendations" in data
        
        # Check structure of defense profiles
        if len(data["defense_profiles"]) > 0:
            profile = data["defense_profiles"][0]
            assert "mechanism" in profile
            assert "frequency" in profile
            assert "adaptiveness" in profile
            assert "contexts" in profile


@pytest.mark.asyncio
async def test_list_defense_mechanisms():
    """Test listing all defense mechanisms."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/psychology/freudian/mechanisms")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "mechanisms" in data
        assert len(data["mechanisms"]) > 0


@pytest.mark.asyncio
async def test_list_case_studies():
    """Test listing case studies."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/psychology/case-studies")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Check structure of first case study
        study = data[0]
        assert "id" in study
        assert "title" in study
        assert "summary" in study
        assert "framework" in study


@pytest.mark.asyncio
async def test_get_case_study_detail():
    """Test getting detailed case study information."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # First, get the list to get a valid ID
        list_response = await client.get("/api/v1/psychology/case-studies")
        studies = list_response.json()
        
        if len(studies) > 0:
            study_id = studies[0]["id"]
            
            response = await client.get(f"/api/v1/psychology/case-studies/{study_id}")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["id"] == study_id
            assert "interventions" in data
            assert "outcomes" in data
            assert "profile" in data


@pytest.mark.asyncio
async def test_find_similar_cases():
    """Test finding similar case studies."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        request_data = {
            "profile": {
                "team_size": 8,
                "primary_issues": ["communication", "conflict"]
            },
            "limit": 3
        }
        
        response = await client.post(
            "/api/v1/psychology/case-studies/similar",
            json=request_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) <= 3


@pytest.mark.asyncio
async def test_get_intervention_recommendations():
    """Test getting intervention recommendations."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        request_data = {
            "profile": {
                "team_size": 5,
                "primary_issues": ["stress", "burnout"]
            },
            "limit": 3
        }
        
        response = await client.post(
            "/api/v1/psychology/case-studies/recommendations",
            json=request_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "recommendations" in data
        assert "similar_cases" in data
        assert isinstance(data["recommendations"], list)


@pytest.mark.asyncio
async def test_list_frameworks():
    """Test listing psychological frameworks."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/psychology/case-studies/frameworks")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "frameworks" in data
        assert isinstance(data["frameworks"], list)
