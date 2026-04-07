# CI/CD Pipeline Setup

## Overview

This project uses GitHub Actions for continuous integration and deployment. The pipeline automatically runs tests, checks code quality, and generates coverage reports on every push and pull request.

## Workflows

### 1. Tests Workflow (`tests.yml`)

**Triggers**: Push to main/develop, Pull requests to main/develop

**Jobs**:
- **Test**: Runs on multiple Python versions (3.9, 3.10, 3.11, 3.12, 3.14)
  - Runs on: Ubuntu, Windows, macOS
  - Tests all 109 tests
  - Uploads coverage to Codecov (Ubuntu/Python 3.12 only)

- **Lint**: Code quality checks (Ubuntu only)
  - Black (code formatting)
  - isort (import sorting)
  - flake8 (style guide enforcement)

- **Build**: Structure verification
  - Checks required directories exist
  - Checks required files exist
  - Verifies project integrity

### 2. Coverage Workflow (`coverage.yml`)

**Triggers**: Push to main, Pull requests to main

**Jobs**:
- **Coverage**: Detailed coverage analysis
  - Generates HTML coverage report
  - Uploads to Codecov
  - Comments on PRs with coverage summary
  - Shows coverage deltas

## Status Badges

Add these badges to your README.md:

```markdown
[![Tests](https://github.com/UPBGE/upbge-nodejs-sdk/actions/workflows/tests.yml/badge.svg)](https://github.com/UPBGE/upbge-nodejs-sdk/actions/workflows/tests.yml)
[![Coverage](https://codecov.io/gh/UPBGE/upbge-nodejs-sdk/branch/main/graph/badge.svg)](https://codecov.io/gh/UPBGE/upbge-nodejs-sdk)
```

## Coverage Goals

- **Green** (70%+): Excellent coverage
- **Orange** (50-70%): Acceptable coverage, needs improvement
- **Red** (<50%): Poor coverage, must improve

## How to View Results

### Test Results
1. Go to repository
2. Click "Actions" tab
3. Select workflow run
4. View job logs

### Coverage Reports
1. Go to [codecov.io](https://codecov.io)
2. Link your GitHub account
3. Select this repository
4. View coverage graphs and history

### PR Comments
- Coverage comments automatically appear on PRs
- Shows coverage change compared to main branch
- Color-coded coverage indicators

## Local Testing

Run tests locally before pushing:

```bash
# Install test dependencies
pip install pytest pytest-cov coverage

# Run all tests
pytest tests/ -v

# Generate coverage report
coverage run -m pytest tests/
coverage report -m
coverage html  # Opens htmlcov/index.html
```

## Customization

### Add more Python versions
Edit `tests.yml`:
```yaml
python-version: ['3.9', '3.10', '3.11', '3.12', '3.14', '3.15']
```

### Require specific coverage
Edit `coverage.yml`:
```yaml
MINIMUM_GREEN: 80  # Require 80% for green
MINIMUM_ORANGE: 60
```

### Add more linting tools
Edit `tests.yml` lint job:
```bash
pip install pylint mypy
pylint python/
mypy python/
```

### Run on specific branches
Edit workflows (both files):
```yaml
on:
  push:
    branches: [ main, develop, feature/** ]
```

## Troubleshooting

### Tests failing locally but passing in CI
- Check Python version: `python --version`
- Check pytest installed: `pip install pytest`
- Clear cache: `rm -rf .pytest_cache __pycache__`

### Coverage not uploading
- Codecov token may need setup
- Check repository is public or Codecov token is configured
- View Codecov logs in GitHub Actions

### Linting fails on Windows
- Line endings might differ (CRLF vs LF)
- Configure git: `git config core.autocrlf input`

## CI/CD Best Practices

1. **Run tests locally before pushing**
   ```bash
   pytest tests/ && coverage report
   ```

2. **Keep tests fast** (<5s for full suite is ideal)

3. **Fail fast on syntax errors** (CI does this)

4. **Use meaningful commit messages** for better tracking

5. **Link commits to issues** with `Fixes #123`

6. **Review PR comments** from coverage bot

## Next Steps

- [ ] Link Codecov account to repository
- [ ] Configure branch protection rules (require CI to pass)
- [ ] Add status badges to README.md
- [ ] Set up code review requirements
- [ ] Configure auto-merge for passing PRs (optional)

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Codecov Documentation](https://docs.codecov.io/)
- [pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
