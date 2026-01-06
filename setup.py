"""
Setup script for Team Alchemy.
"""

from setuptools import setup, find_packages

setup(
    name="team-alchemy",
    version="0.1.0",
    description="A comprehensive team dynamics and psychological assessment platform",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Team Alchemy Development Team",
    url="https://github.com/DoctorDoveDragon/Team-Alchemy-APP",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.9",
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "sqlalchemy>=2.0.0",
        "python-multipart>=0.0.6",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "celery>=5.3.0",
        "redis>=5.0.0",
        "typer>=0.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.21.0",
            "httpx>=0.25.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "isort>=5.12.0",
            "pylint>=3.0.0",
            "pre-commit>=3.4.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "team-alchemy=team_alchemy.cli.main:app",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
