# Testing Guide

This document provides comprehensive information about testing the Linoroso Shopify Automation codebase.

## Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Coverage](#test-coverage)
- [Writing Tests](#writing-tests)
- [Continuous Integration](#continuous-integration)

## Overview

The project uses **pytest** as the testing framework, along with several plugins for enhanced functionality:

- `pytest`: Core testing framework
- `pytest-cov`: Code coverage reporting
- `pytest-mock`: Mocking and patching utilities
- `pytest-asyncio`: Support for async tests

## Test Structure

```
tests/
├── __init__.py
├── test_settings.py          # Configuration and settings tests
├── test_content_engine.py    # Content generation tests
└── test_optimizer.py         # Product optimization tests
```

### Test Categories

Tests are organized by module and include:

1. **Unit Tests**: Test individual functions and classes in isolation
2. **Integration Tests**: Test interactions between components (marked with `@pytest.mark.integration`)
3. **Validation Tests**: Test configuration validation and error handling

## Running Tests

### Install Dependencies

First, ensure all testing dependencies are installed:

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_settings.py
```

### Run Specific Test Class or Function

```bash
# Run specific test class
pytest tests/test_settings.py::TestClaudeConfig

# Run specific test function
pytest tests/test_settings.py::TestClaudeConfig::test_valid_config
```

### Run Tests with Verbose Output

```bash
pytest -v
```

### Run Tests with Coverage

```bash
pytest --cov=. --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`.

### Run Tests Matching a Pattern

```bash
# Run all tests with "config" in the name
pytest -k config

# Run all tests except slow tests
pytest -m "not slow"
```

## Test Coverage

### View Coverage Report

After running tests with coverage:

```bash
# Terminal report
pytest --cov=. --cov-report=term-missing

# HTML report (opens in browser)
open htmlcov/index.html
```

### Coverage Goals

- **Target**: 80%+ code coverage
- **Critical modules**: 90%+ coverage for settings.py, content_engine.py, optimizer.py
- **Excluded**: Test files, __init__.py files, and setup scripts

## Writing Tests

### Test File Naming

- Test files: `test_<module>.py`
- Test classes: `Test<ClassName>`
- Test functions: `test_<description>`

### Example Test Structure

```python
"""
Module docstring explaining what is being tested.
"""

import pytest
from unittest.mock import Mock, patch

from module_name import ClassToTest


class TestClassName:
    """Test ClassName class."""

    def test_valid_scenario(self):
        """Test description of what this tests."""
        # Arrange
        instance = ClassToTest()

        # Act
        result = instance.method()

        # Assert
        assert result == expected_value

    def test_error_handling(self):
        """Test that errors are handled correctly."""
        with pytest.raises(ValueError, match="error message"):
            ClassToTest().method_that_raises()

    @patch('module_name.dependency')
    def test_with_mock(self, mock_dependency):
        """Test using mocks for dependencies."""
        mock_dependency.return_value = "mocked value"
        result = ClassToTest().method()
        assert result == "expected"
```

### Best Practices

1. **Arrange-Act-Assert Pattern**: Structure tests clearly
2. **Descriptive Names**: Test names should explain what they test
3. **One Assertion Per Test**: Keep tests focused
4. **Use Fixtures**: For shared setup/teardown
5. **Mock External Dependencies**: Don't make real API calls in tests
6. **Test Edge Cases**: Include boundary conditions and error cases

### Using Fixtures

```python
@pytest.fixture
def sample_product():
    """Fixture providing a sample product for tests."""
    return Product(
        handle='test-product',
        title='Test Product',
        # ... other fields
    )


def test_with_fixture(sample_product):
    """Test using the fixture."""
    assert sample_product.handle == 'test-product'
```

### Parametrized Tests

```python
@pytest.mark.parametrize("input,expected", [
    (10, 20),
    (5, 10),
    (0, 0),
])
def test_multiplication(input, expected):
    """Test with multiple inputs."""
    assert input * 2 == expected
```

## Test Environment

### Environment Variables

Tests should not depend on actual environment variables. Use mocking:

```python
@patch.dict(os.environ, {'API_KEY': 'test_key'})
def test_with_env_var():
    config = Config.from_env()
    assert config.api_key == 'test_key'
```

### Test Data

- Mock all external API calls
- Use in-memory databases or mocks for database tests
- Create fixture factories for complex test data

## Continuous Integration

### GitHub Actions (Example)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the project is in PYTHONPATH
   ```bash
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   pytest
   ```

2. **Mock Not Working**: Check that you're patching the correct path
   ```python
   # Patch where it's used, not where it's defined
   @patch('module_that_uses_it.dependency')
   ```

3. **Fixtures Not Found**: Ensure fixture is defined in same file or conftest.py

### Debug Mode

Run pytest with extra debugging:

```bash
# Show print statements
pytest -s

# Drop into debugger on failure
pytest --pdb

# Show local variables on failure
pytest -l
```

## Test Markers

Available markers:

- `@pytest.mark.unit`: Unit tests (default)
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.slow`: Slow-running tests

Run specific markers:

```bash
pytest -m integration  # Run only integration tests
pytest -m "not slow"   # Skip slow tests
```

## Contributing

When adding new code:

1. Write tests **before** or **alongside** implementation
2. Ensure all tests pass: `pytest`
3. Check coverage: `pytest --cov`
4. Add docstrings to test functions
5. Update this document if adding new test patterns

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)
- [Effective Python Testing With Pytest](https://realpython.com/pytest-python-testing/)
