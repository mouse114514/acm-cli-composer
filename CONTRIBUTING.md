# Contributing to ACM Composer

Thank you for considering contributing! This document outlines the guidelines.

## Getting Started

1. Fork the repository
2. Clone your fork
3. Install in dev mode: `pip install -e .`
4. Run tests: `python -m pytest tests/ -v`

## Development

### Code Style

- Follow PEP 8
- Use type hints on public functions
- Keep backward compatibility
- No hard dependencies (numpy/cupy are optional)

### Testing

- All features must have tests
- Run the full suite before submitting
- Tests use only stdlib + pytest

### Commits

- Use conventional commit format: `type: description`
- Types: feat, fix, chore, docs, test, refactor, ci

## Pull Request Process

1. Update docs if adding/changing features
2. Ensure all tests pass
3. Add a brief description of changes
4. Reference any related issues

## Feature Requests

Open an issue with the `enhancement` label describing the use case.

## Bug Reports

Open an issue with the `bug` label including:
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS
