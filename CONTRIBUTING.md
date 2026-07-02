# Contributing to CommandDesk

First off, thank you for considering contributing to CommandDesk! We welcome contributions from everyone.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How Can I Contribute?

### Reporting Bugs

- **Ensure the bug was not already reported** by searching [GitHub Issues](https://github.com/JorahOne-Services/CommandDesk/issues)
- If you can't find an open issue addressing the problem, [open a new one](https://github.com/JorahOne-Services/CommandDesk/issues/new)
- Include a clear title and description, as much relevant information as possible, and a code sample or test case demonstrating the expected behavior

### Suggesting Enhancements

- Open a [GitHub Issue](https://github.com/JorahOne-Services/CommandDesk/issues/new) with a clear title and description
- Provide any relevant examples or mockups
- Explain why this enhancement would be useful to most users

### Pull Requests

1. **Fork the repository** and create your branch from `master`
2. **Install dependencies** — `pip install -r requirements.txt`
3. **Make your changes** — Follow the coding conventions below
4. **Add or update tests** as appropriate
5. **Run the linter** — `flake8 scripts/ --max-line-length=120`
6. **Commit your changes** — Use clear, descriptive commit messages
7. **Push to your fork** and submit a pull request to `master`

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/CommandDesk.git
cd CommandDesk

# Install Python dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install pytest pytest-asyncio flake8 black mypy

# Copy environment template
cp .env.example .env
# Edit .env with your settings
```

## Coding Conventions

### Python

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with a max line length of 120 characters
- Use type hints for all function signatures
- Use docstrings for all modules, classes, and public functions
- Use `from __future__ import annotations` at the top of files
- Prefer `async/await` over synchronous code where possible
- Use structured logging (the `logging` module) instead of `print()`

### Docker

- Use specific image tags (not `latest`) in production Dockerfiles
- Run as non-root user inside containers
- Use multi-stage builds where appropriate
- Keep images small — prefer `-slim` or `-alpine` base images

### Shell Scripts

- Use `set -euo pipefail` at the top of all bash scripts
- Check for required commands before using them
- Provide clear error messages
- Support `--help` flag

## Testing

- Write tests for all new features and bug fixes
- Place tests in the `tests/` directory
- Use `pytest` as the test runner
- Run tests with: `python -m pytest tests/ -v`

## Documentation

- Update `README.md` if you change functionality
- Add or update docstrings for any new/modified Python code
- Update `docs/` if you add new configuration options or API endpoints
- Document any breaking changes clearly

## Review Process

1. Maintainers will review your PR within a few days
2. Address any feedback or requested changes
3. Once approved, a maintainer will merge your PR

## Questions?

Open a [GitHub Discussion](https://github.com/JorahOne-Services/CommandDesk/discussions) or reach out to the maintainers.

Thank you for contributing! 🚀
