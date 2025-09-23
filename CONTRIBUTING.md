# Contributing to Quiply Backend

Thank you for your interest in contributing to Quiply! This document provides guidelines for contributing to the project.

## Development Setup

### Prerequisites
- Python 3.10-3.12
- [uv](https://github.com/astral-sh/uv) package manager
- Git

### Setup Steps

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/quiply-backend.git
   cd quiply-backend
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run tests to ensure everything works**
   ```bash
   uv run pytest
   ```

## Development Workflow

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the coding standards below
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Run tests
   uv run pytest

   # Check code quality
   uv run ruff check
   uv run mypy src/
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

5. **Push and create a pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Coding Standards

### Python Code Style
- Follow PEP 8 guidelines
- Use type hints for all function parameters and return values
- Maximum line length: 88 characters (Black default)
- Use descriptive variable and function names

### Code Organization
- Place shared code only where used by ≥ 2 modules
- Prefer composition over inheritance
- Write small, focused functions
- Use Pydantic models for data validation

### Testing
- Write tests for all new functionality
- Separate unit tests from integration tests
- Use pytest fixtures for test setup
- Aim for >90% test coverage

### Documentation
- Update README.md for significant changes
- Add docstrings to public functions and classes
- Include examples in docstrings where helpful

## Pull Request Process

### Before Submitting
- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] No sensitive information is committed

### PR Description
Please include:
- Summary of changes
- Related issue numbers
- Breaking changes (if any)
- Testing instructions

### Review Process
1. Automated checks must pass
2. At least one maintainer review required
3. Address feedback promptly
4. Keep PRs focused and reasonably sized

## Project Structure

```
src/
├── framework/          # AI evaluation and generation framework
├── scenario/           # Conversation scenario engine
├── fastapi_app/       # Web API and routes
├── services/          # Backend services
├── models/            # Data models and schemas
└── websocket/         # Real-time communication
```

## Types of Contributions

### Bug Reports
- Use the issue template
- Include reproduction steps
- Provide system information
- Add relevant logs/screenshots

### Feature Requests
- Describe the use case
- Explain the expected behavior
- Consider implementation complexity
- Discuss alternatives

### Code Contributions
- Bug fixes
- New features
- Performance improvements
- Documentation improvements
- Test improvements

## Development Tools

### Available Scripts
```bash
# Run the application
uv run python startup.py

# Run tests
uv run pytest

# Code formatting
uv run black src/

# Linting
uv run ruff check src/

# Type checking
uv run mypy src/
```

### Useful Tools
- `tools/` directory contains development utilities
- Use debugger endpoints for testing AI responses
- Check `data/` for example configurations

## Questions?

- Open an issue for general questions
- Check existing issues and documentation first
- Be specific about your environment and use case

Thank you for contributing!