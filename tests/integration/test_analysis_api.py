"""
Integration tests for team analysis API endpoints.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_analyze_team():
    """Test team analysis endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        request_data = {
            "team_id": 1,
            "members": [
                {
                    "user_id": 101,
                    "mbti_type": "INTJ",
                    "behaviors": ["strategic planning", "analytical thinking"],
                    "archetype": "analyst"
                },
                {
                    "user_id": 102,
                    "mbti_type": "ENFP",
                    "behaviors": ["creative problem solving", "team collaboration"],
                    "archetype": "innovator"
                },
                {
                    "user_id": 103,
                    "mbti_type": "ISTJ",
                    "behaviors": ["detail oriented", "reliable execution"],
                    "archetype": "organizer"
                }
            ]
        }
        
        response = await client.post("/api/v1/analysis/team/1", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["team_id"] == 1
        assert data["team_size"] == 3
        assert "member_analyses" in data
        assert len(data["member_analyses"]) == 3
        assert "team_dynamics" in data
        assert "collective_patterns" in data
        assert "recommendations" in data
        
        # Check member analysis structure
        member = data["member_analyses"][0]
        assert "user_id" in member
        assert "mbti_type" in member
        assert "jungian_profile" in member
        assert "dominant_archetypes" in member
        assert "defense_mechanisms" in member
        assert "recommendations" in member


@pytest.mark.asyncio
async def test_analyze_team_mismatch_id():
    """Test team analysis with mismatched team ID."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        request_data = {
            "team_id": 2,
            "members": [
                {
                    "user_id": 101,
                    "mbti_type": "INTJ",
                    "behaviors": [],
                    "archetype": "analyst"
                }
            ]
        }
        
        response = await client.post("/api/v1/analysis/team/1", json=request_data)
        
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_analyze_team_no_members():
    """Test team analysis with no members."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        request_data = {
            "team_id": 1,
            "members": []
        }
        
        response = await client.post("/api/v1/analysis/team/1", json=request_data)
        
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_individual_analysis():
    """Test individual analysis endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        params = {
            "mbti_type": "INTJ",
            "behaviors": "strategic planning,analytical thinking,independent work"
        }
        
        response = await client.get("/api/v1/analysis/individual/101", params=params)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["user_id"] == 101
        assert data["mbti_type"] == "INTJ"
        assert "jungian_profile" in data
        assert "dominant_archetypes" in data
        assert "defense_mechanisms" in data
        assert "recommendations" in data


@pytest.mark.asyncio
async def test_get_individual_analysis_no_mbti():
    """Test individual analysis without MBTI type."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/analysis/individual/101")
        
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_check_compatibility():
    """Test compatibility check endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        request_data = {
            "user_ids": [101, 102, 103],
            "mbti_types": ["INTJ", "ENFP", "ISTJ"]
        }
        
        response = await client.post("/api/v1/analysis/compatibility", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "compatibility_matrix" in data
        assert "overall_compatibility" in data
        assert "total_pairs" in data
        
        # For 3 members, we should have 3 pairs (3 choose 2)
        assert data["total_pairs"] == 3
        
        # Check matrix structure
        if len(data["compatibility_matrix"]) > 0:
            pair = data["compatibility_matrix"][0]
            assert "user1" in pair
            assert "user2" in pair
            assert "mbti1" in pair
            assert "mbti2" in pair
            assert "compatible" in pair
            assert "compatibility_score" in pair


@pytest.mark.asyncio
async def test_check_compatibility_length_mismatch():
    """Test compatibility check with mismatched lengths."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        request_data = {
            "user_ids": [101, 102],
            "mbti_types": ["INTJ"]
        }
        
        response = await client.post("/api/v1/analysis/compatibility", json=request_data)
        
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_check_compatibility_insufficient_users():
    """Test compatibility check with less than 2 users."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        request_data = {
            "user_ids": [101],
            "mbti_types": ["INTJ"]
        }
        
        response = await client.post("/api/v1/analysis/compatibility", json=request_data)
        
        assert response.status_code == 400
