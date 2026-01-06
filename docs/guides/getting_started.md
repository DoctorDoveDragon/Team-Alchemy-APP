# Getting Started with Team Alchemy

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Install from source

```bash
git clone https://github.com/DoctorDoveDragon/Team-Alchemy-APP.git
cd Team-Alchemy-APP
pip install -r requirements.txt
pip install -e .
```

### Using Docker

```bash
docker-compose up
```

## Configuration

Copy the example environment file and configure:

```bash
cp .env.example .env
```

Edit `.env` with your settings.

## Initialize Database

```bash
python -m team_alchemy.cli init
```

Or using the CLI:

```bash
team-alchemy init
```

## Basic Usage

### Python API

```python
from team_alchemy.core.archetypes.traits import TraitProfile
from team_alchemy.core.archetypes.classifier_logic import ArchetypeClassifier

# Create a trait profile
profile = TraitProfile()
profile.add_score("Extraversion", 75.0)
profile.add_score("Analytical Thinking", 85.0)

# Classify
classifier = ArchetypeClassifier()
result = classifier.classify(profile)

print(f"Primary Archetype: {result.primary_archetype.value}")
print(f"Confidence: {result.confidence:.2%}")
```

### REST API

Start the server:

```bash
uvicorn main:app --reload
```

Access the API at `http://localhost:8000`

API documentation at `http://localhost:8000/docs`

### CLI

```bash
# Initialize database
team-alchemy init

# Run assessment
team-alchemy assess 101

# Analyze team
team-alchemy analyze-team 1
```

## Next Steps

- Read the [API Reference](../api/reference.md)
- Check out the [examples](../../examples/)
- Explore the [architecture documentation](../index.md)
