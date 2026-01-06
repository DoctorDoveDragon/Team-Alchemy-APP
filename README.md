# Team Alchemy

A comprehensive team dynamics and psychological assessment platform that combines modern psychology with data-driven insights.

## Features

- **🧠 Psychological Assessment**: Multi-dimensional personality profiling based on established psychological frameworks
- **👥 Team Analysis**: Comprehensive team composition and dynamics analysis
- **🎯 Archetype Classification**: Automatic classification into personality archetypes
- **🔮 Predictive Insights**: ML-powered predictions for team performance and compatibility
- **📊 Data-Driven Recommendations**: Actionable recommendations for team improvement
- **🔬 Deep Psychology Integration**: Jungian, Freudian, and shadow work frameworks

## Quick Start

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/DoctorDoveDragon/Team-Alchemy-APP.git
cd Team-Alchemy-APP

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Initialize Database

```bash
# Using CLI
team-alchemy init

# Or using script
python scripts/setup_database.py
```

### Run the Application

```bash
# Start the API server
uvicorn main:app --reload

# Or using Make
make run
```

The API will be available at `http://localhost:8000`

API documentation at `http://localhost:8000/docs`

## Usage

### Python API

```python
from team_alchemy.core.archetypes.traits import TraitProfile
from team_alchemy.core.archetypes.classifier_logic import ArchetypeClassifier

# Create a trait profile
profile = TraitProfile()
profile.add_score("Extraversion", 75.0)
profile.add_score("Analytical Thinking", 85.0)

# Classify into archetype
classifier = ArchetypeClassifier()
result = classifier.classify(profile)

print(f"Primary Archetype: {result.primary_archetype.value}")
print(f"Confidence: {result.confidence:.2%}")
```

### REST API

```bash
# Create an assessment
curl -X POST http://localhost:8000/assessments/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Team Assessment", "description": "Initial assessment"}'

# Analyze a team
curl http://localhost:8000/analysis/team/1
```

### CLI

```bash
# Initialize database
team-alchemy init

# Run an assessment
team-alchemy assess 101

# Analyze a team
team-alchemy analyze-team 1

# Get recommendations
team-alchemy recommend 1
```

## Architecture

### Core Modules

- **archetypes**: Personality type definitions and classification
- **assessment**: Assessment models, calculators, and validators
- **psychology**: Jungian, Freudian, and shadow work frameworks
- **scoring**: Composite scoring algorithms
- **utils**: Metrics and data transformers

### API Layer

- **routes**: RESTful API endpoints
- **middleware**: Authentication and validation

### Intelligence

- **optimizers**: Team composition optimization algorithms
- **predictors**: ML-based outcome prediction models

### Data Layer

- **models**: SQLAlchemy ORM models
- **repository**: Database session management

## Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### Run Tests

```bash
# All tests with coverage
make test

# Unit tests only
make test-unit

# Integration tests only
make test-integration
```

### Code Quality

```bash
# Format code
make format

# Run linters
make lint
```

### Docker

```bash
# Start all services
make docker-up

# View logs
make docker-logs

# Stop services
make docker-down
```

## Documentation

- [Getting Started Guide](docs/guides/getting_started.md)
- [API Reference](docs/api/reference.md)
- [Architecture Overview](docs/index.md)

## Examples

See the [examples](examples/) directory for:

- Basic usage examples
- Team analysis examples
- Sample data

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions, please use the [GitHub issue tracker](https://github.com/DoctorDoveDragon/Team-Alchemy-APP/issues).

## Acknowledgments

Built with modern Python frameworks:

- FastAPI for the REST API
- SQLAlchemy for database ORM
- Pydantic for data validation
- Celery for async task processing
- pytest for testing

---

**Team Alchemy** - Transforming team dynamics through psychological insights
