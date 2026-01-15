# Team Alchemy API Documentation

## Overview

Team Alchemy provides a comprehensive psychological analysis platform combining Jungian and Freudian frameworks with team dynamics assessment.

## API Endpoints

### Base URL

```
http://localhost:8000/api/v1
```

## Psychology Endpoints

### Jungian Analysis

#### Get Jungian Profile by MBTI Type

```
GET /psychology/jungian/profile/{mbti_type}
```

Returns the complete Jungian psychological profile for a given MBTI type, including:
- Cognitive function stack (dominant, auxiliary, tertiary, inferior)
- Archetype affinities
- Strengths
- Shadow aspects

**Example:**
```bash
curl http://localhost:8000/api/v1/psychology/jungian/profile/INTJ
```

**Response:**
```json
{
  "mbti_type": "INTJ",
  "dominant_function": "Ni",
  "auxiliary_function": "Te",
  "tertiary_function": "Fi",
  "inferior_function": "Se",
  "function_stack": ["Ni", "Te", "Fi", "Se"],
  "archetype_affinity": ["VISIONARY", "ANALYST"],
  "strengths": ["Strategic planning", "Systems thinking", "Independence"],
  "shadow": "May neglect emotional considerations"
}
```

#### Check MBTI Compatibility

```
GET /psychology/jungian/compatibility/{type1}/{type2}
```

Analyzes compatibility between two MBTI types based on cognitive function complementarity.

**Example:**
```bash
curl http://localhost:8000/api/v1/psychology/jungian/compatibility/INTJ/ENFP
```

#### List All MBTI Types

```
GET /psychology/jungian/types
```

Returns all 16 MBTI types with their basic information.

### Freudian Analysis

#### Analyze Defense Mechanisms

```
POST /psychology/freudian/defense-mechanisms
```

Identifies active defense mechanisms based on observed behaviors and stress responses.

**Request Body:**
```json
{
  "behaviors": [
    "justifies behavior",
    "creates logical explanations",
    "refuses to acknowledge reality"
  ],
  "stress_responses": {}
}
```

**Response:**
```json
{
  "defense_profiles": [
    {
      "mechanism": "rationalization",
      "frequency": 0.4,
      "adaptiveness": 0.5,
      "contexts": ["justifies behavior", "creates logical explanations"],
      "is_maladaptive": false
    }
  ],
  "defensiveness_level": 0.3,
  "defense_maturity": 0.6,
  "maladaptive_count": 1,
  "primary_conflicts": ["denial"],
  "recommendations": ["Work on acknowledging difficult realities"]
}
```

#### List Defense Mechanisms

```
GET /psychology/freudian/mechanisms
```

Returns all available Freudian defense mechanisms.

### Case Studies

#### List All Case Studies

```
GET /psychology/case-studies
```

Returns all available psychological case studies.

#### Get Case Study Details

```
GET /psychology/case-studies/{case_id}
```

Returns detailed information about a specific case study.

#### Find Similar Cases

```
POST /psychology/case-studies/similar
```

Finds case studies similar to a given profile.

**Request Body:**
```json
{
  "profile": {
    "team_size": 8,
    "primary_issues": ["communication", "conflict"]
  },
  "limit": 3
}
```

#### Get Intervention Recommendations

```
POST /psychology/case-studies/recommendations
```

Provides intervention recommendations based on similar case studies.

#### List Psychological Frameworks

```
GET /psychology/case-studies/frameworks
```

Returns all psychological frameworks used in case studies.

## Analysis Endpoints

### Team Analysis

#### Analyze Team

```
POST /analysis/team/{team_id}
```

Performs comprehensive team analysis integrating Jungian profiles, archetypes, and defense mechanisms.

**Request Body:**
```json
{
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
    }
  ]
}
```

**Response:**
```json
{
  "team_id": 1,
  "team_size": 2,
  "member_analyses": [...],
  "team_dynamics": {
    "mbti_distribution": {"INTJ": 1, "ENFP": 1},
    "diversity_score": 1.0,
    "balance": "balanced"
  },
  "collective_patterns": {...},
  "recommendations": [...]
}
```

### Individual Analysis

```
GET /analysis/individual/{user_id}?mbti_type={type}&behaviors={behaviors}
```

Analyzes an individual's psychological profile.

**Example:**
```bash
curl "http://localhost:8000/api/v1/analysis/individual/101?mbti_type=INTJ&behaviors=strategic+planning,analytical+thinking"
```

### Check Compatibility

```
POST /analysis/compatibility
```

Checks compatibility between multiple team members.

**Request Body:**
```json
{
  "user_ids": [101, 102, 103],
  "mbti_types": ["INTJ", "ENFP", "ISTJ"]
}
```

**Response:**
```json
{
  "compatibility_matrix": [
    {
      "user1": 101,
      "user2": 102,
      "mbti1": "INTJ",
      "mbti2": "ENFP",
      "compatible": true,
      "compatibility_score": 75
    }
  ],
  "overall_compatibility": 66.67,
  "total_pairs": 3
}
```

## Archetype Endpoints

### List All Archetypes

```
GET /archetypes/
```

Returns all available team archetypes.

### Get Specific Archetype

```
GET /archetypes/{archetype_type}
```

Returns detailed information about a specific archetype.

## Error Responses

All endpoints follow standard HTTP status codes:

- `200 OK`: Successful request
- `400 Bad Request`: Invalid input parameters
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

Error responses include a detail message:

```json
{
  "detail": "Invalid MBTI type: INVALID"
}
```

## Rate Limiting

Currently, no rate limiting is enforced. This may change in production environments.

## Authentication

The current implementation does not require authentication. Add authentication headers as needed for production deployments.

## Interactive Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation with the ability to test endpoints directly.

Visit `http://localhost:8000/redoc` for ReDoc-style documentation.
