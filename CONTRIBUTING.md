# Contributing Guide

Thank you for your interest in contributing to **Forex Monitor**! This guide will help you get started.

---

## Code of Conduct

This project follows a mutual-respect code of conduct. All contributors are expected to:
- Be respectful and constructive in all interactions
- Accept constructive criticism gracefully
- Focus on what is best for the community

---

## Branching Model — Git Flow

This project uses **[Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)**. Please follow this model strictly:

```
main          ←─── production-ready code, tagged releases only
  ↑
release/x.y.z ←─── release preparation (version bump, changelog)
  ↑
develop       ←─── integration branch, all feature PRs target here
  ↑
feature/*     ←─── new features (branched from develop)
hotfix/*      ←─── urgent fixes branched from main
```

| Branch prefix | Branched from | Merges into | Purpose |
|---|---|---|---|
| `feature/*` | `develop` | `develop` | New features |
| `bugfix/*` | `develop` | `develop` | Non-urgent bug fixes |
| `release/*` | `develop` | `main` + `develop` | Release preparation |
| `hotfix/*` | `main` | `main` + `develop` | Critical production fixes |

> [!IMPORTANT]
> **Always branch from `develop`**, never from `main`. Pull Requests must target `develop`.

---

## How to Contribute

### Reporting Bugs

1. Check that the bug has not already been reported in [Issues](../../issues)
2. Create a new issue using the **Bug Report** template with:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behaviour
   - Screenshots if applicable
   - Environment (OS, Python/Node version, browser)

### Suggesting Features

1. Review the [README](README.md) roadmap for planned features
2. Open an issue using the **Feature Request** template with label `enhancement`
3. Describe the use case and the benefit it brings

### Pull Requests

1. Fork the repository
2. Create a branch **from `develop`**:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/my-feature
   ```
3. Make your changes following the style guides below
4. Ensure all tests pass:
   ```bash
   cd backend && pytest tests/ -v
   ```
5. Commit with descriptive messages following [Conventional Commits](https://www.conventionalcommits.org/):
   ```bash
   git commit -m "feat: add EUR/GBP pair support"
   ```
6. Push and open a Pull Request **targeting `develop`**

---

## Project Structure

```
forex-monitor/
├── backend/           # Python FastAPI API
│   ├── app/
│   │   ├── api/       # REST endpoints
│   │   ├── models/    # SQLAlchemy models
│   │   ├── services/  # Business logic
│   │   └── jobs/      # Scheduled tasks
│   └── tests/         # Unit tests
├── frontend/          # Next.js + React UI
│   ├── src/
│   │   ├── app/       # Pages (App Router)
│   │   ├── components/# React components
│   │   └── lib/       # Utilities / API client
│   └── public/        # Static assets
└── docs/              # Extended documentation
```

---

## Style Guides

### Python (Backend)

- Follow [PEP 8](https://pep8.org/)
- Use type hints on all public functions
- Add docstrings to classes and main functions
- Use descriptive names in `snake_case`

```python
async def get_exchange_rate(
    base: str = "USD",
    target: str = "EUR"
) -> ExchangeRate:
    """
    Fetch the current exchange rate.

    Args:
        base: Base currency (default USD)
        target: Target currency (default EUR)

    Returns:
        ExchangeRate with the current rate
    """
    ...
```

### TypeScript (Frontend)

- Use strict TypeScript
- Define interfaces for component props
- `camelCase` for variables and functions, `PascalCase` for components

```typescript
interface ExchangeCardProps {
  rate: ExchangeRate;
  onRefresh?: () => void;
}

export function ExchangeCard({ rate, onRefresh }: ExchangeCardProps) {
  ...
}
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix | When to use |
|---|---|
| `feat:` | New functionality |
| `fix:` | Bug fix |
| `docs:` | Documentation changes |
| `style:` | Formatting (no logic change) |
| `refactor:` | Code refactoring |
| `test:` | Adding or updating tests |
| `chore:` | Maintenance, dependencies |
| `ci:` | CI/CD pipeline changes |

---

## Local Development

### Requirements
| Dependency | Version |
|---|---|
| Python | 3.10+ |
| Node.js | 18+ |
| npm | 9+ |

### Setup

```bash
# Clone the repository
git clone https://github.com/Yasma90/forex-monitor.git
cd forex-monitor

# Backend — create virtual environment
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### Run in development mode

```bash
# Terminal 1 — Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
npm run dev
```

### Tests

```bash
# Backend — run all tests
cd backend
pytest tests/ -v

# With coverage report
pytest tests/ --cov=app --cov-report=html
```

---

## Areas for Contribution

### High Priority
- [ ] User authentication (JWT)
- [ ] Multi-currency support
- [ ] Integration / E2E tests (Playwright)

### Medium Priority
- [ ] Dark mode
- [ ] CSV/Excel data export
- [ ] Economic calendar

### Documentation
- [ ] Add API usage examples
- [ ] Video tutorial / demo GIF

---

## Questions

If you have questions, open an issue with the label `question` or contact the maintainers.

---

*Thank you for contributing to Forex Monitor!* 🚀
