# Claude Code Guidelines for Screambot

## Development Workflow

### Branching and Pull Requests
- **Always create a feature branch** for changes - never commit directly to `master`
- Branch naming: Use descriptive names like `fix-bug-name`, `add-feature-name`, or `update-docs`
- **Always create a Pull Request** after pushing changes
- Wait for review/approval before merging

### Code Quality
- **Always run tests before committing**: `./bin/pytest -v`
- All tests must pass before creating a PR
- **Review your own code** before committing:
  - Read through all changes
  - Check for potential issues
  - Ensure code follows existing patterns
  - Verify no debugging code or commented-out code is included

### Commit Standards
- Write clear, descriptive commit messages
- Include `Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>` in commits
- Use conventional commit format when appropriate

## Project-Specific Guidelines

### Code Style
- Follow existing code patterns in the repository
- Use descriptive variable and function names
- Add docstrings to functions explaining purpose, args, and returns
- Keep functions focused and single-purpose

### Testing
- Test file location: `test_screambot.py`, `test_storage.py`
- Run tests with: `./bin/pytest -v` (using virtual environment)
- Write tests for new features
- Ensure edge cases are covered

### Dependencies
- Python 3.7+ required
- Virtual environment files (`bin/`, `lib/`, `pyvenv.cfg`) are gitignored
- Dependencies listed in `requirements.txt`
- Use `pip3 install -r requirements.txt` to install

### Database
- SQLite database: `screambot.db` (gitignored)
- Storage manager: `storage.py`
- Always use the storage manager for database operations

### Security
- Never commit `secret.py` (contains Slack tokens)
- Never commit database files
- Escape user input to prevent Slack markup injection (use `escape_slack_markup()`)
- Validate input lengths and formats

### Slack Integration
- Uses Slack Bolt framework
- Socket Mode for real-time messaging
- Bot responds to mentions and custom commands
- Custom commands support template variables (`$what`)

## Common Tasks

### Running Locally
```bash
python3 app.py
```

### Running Tests
```bash
./bin/pytest -v
```

### Adding a Custom Command
Custom commands are managed through the Slack UI or the storage module. They support:
- Exact match commands (e.g., "panic" → response)
- Template commands with `$what` variable (e.g., "love $what" → "I love $what SO MUCH!")

### Deployment
Production runs on Google Compute Engine VM using systemd. See README.md for deployment instructions.

## Review Checklist

Before creating a PR, ensure:
- [ ] All tests pass (`./bin/pytest -v`)
- [ ] Code has been reviewed for quality and security
- [ ] No debugging code or commented-out code remains
- [ ] Changes follow existing patterns
- [ ] Commit messages are clear and descriptive
- [ ] Virtual environment files are not included in commits
- [ ] No secrets or sensitive data in commits
