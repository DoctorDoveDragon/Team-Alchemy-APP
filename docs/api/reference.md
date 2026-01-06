# API Reference

## REST API Endpoints

### Assessments

#### Create Assessment
```
POST /assessments/
```

Create a new assessment.

**Request Body:**
```json
{
  "title": "string",
  "description": "string",
  "questions": []
}
```

#### Get Assessment
```
GET /assessments/{assessment_id}
```

Retrieve an assessment by ID.

#### Submit Response
```
POST /assessments/{assessment_id}/responses
```

Submit a response to an assessment question.

### Analysis

#### Analyze Team
```
POST /analysis/team/{team_id}
```

Analyze team dynamics and composition.

#### Individual Analysis
```
GET /analysis/individual/{user_id}
```

Get individual personality analysis.

### Teams

#### Create Team
```
POST /teams/
```

Create a new team.

#### Get Team
```
GET /teams/{team_id}
```

Retrieve team information.

#### Add Team Member
```
POST /teams/{team_id}/members/{user_id}
```

Add a member to a team.

## Data Models

### Assessment
```python
{
  "id": int,
  "title": str,
  "description": str,
  "status": str,
  "created_at": datetime,
  "responses": []
}
```

### TraitProfile
```python
{
  "scores": Dict[str, float]
}
```

## Authentication

All API requests require authentication via Bearer token:

```
Authorization: Bearer <token>
```
