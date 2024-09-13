#!/bin/bash

# Run unit tests
python -m pytest tests/unit

# Run integration tests
python -m pytest tests/integration

# Run all tests with coverage
python -m pytest --cov=app tests/
