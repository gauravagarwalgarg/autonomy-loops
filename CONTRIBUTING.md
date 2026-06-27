# Contributing to AutonomyLoops

## Dual-Platform Repository

AutonomyLoops is hosted on **both GitHub and GitLab** simultaneously. Both are first-class citizens CI/CD, documentation, and issue tracking work on either platform.

| Platform | Repository | Docs Site | Container Registry |
|---|---|---|---|
| **GitHub** | `github.com/GauravAgarwalGarg/AutonomyLoops` | GitHub Pages | `ghcr.io` |
| **GitLab** | `gitlab.com/GauravAgarwalGarg/AutonomyLoops` | GitLab Pages | GitLab Container Registry |

### How Mirroring Works

Choose one as primary (where you push) and mirror to the other:

```bash
# Option A: GitHub primary, mirror to GitLab
git remote add github git@github.com:GauravAgarwalGarg/AutonomyLoops.git
git remote add gitlab git@gitlab.com:GauravAgarwalGarg/AutonomyLoops.git
git push github main
git push gitlab main

# Option B: Use GitLab's built-in mirroring
# Settings → Repository → Mirroring repositories → Add GitHub as push mirror
```

Or use the provided `scripts/sync-remotes.sh` to push to both simultaneously.

### CI/CD Platform Parity

| Feature | GitHub Actions | GitLab CI/CD |
|---|---|---|
| Config file | `.github/workflows/ci.yml` | `.gitlab-ci.yml` |
| Lint + Test | ✓ | ✓ |
| Build package | ✓ | ✓ |
| Build docs | ✓ (MkDocs) | ✓ (MkDocs) |
| Deploy docs | GitHub Pages | GitLab Pages |
| MR/PR previews | | ✓ (review environments) |
| Docker build | ✓ (buildx) | ✓ (docker-in-docker) |
| Container push | ghcr.io | $CI_REGISTRY |

Both CI configurations are functionally identical same lint rules, same test matrix, same docs build. They only differ in platform-specific deployment mechanisms.

## Development Setup

```bash
# Clone
git clone https://github.com/GauravAgarwalGarg/AutonomyLoops.git
cd AutonomyLoops

# Install with dev dependencies
pip install -e ".[dev,all]"

# Run tests
pytest tests/ -v

# Run linter
ruff check autonomy_loops/ tests/

# Run type checker
mypy autonomy_loops/

# Build docs locally
pip install mkdocs-material mkdocs-minify-plugin mkdocs-git-revision-date-localized-plugin
mkdocs serve  # http://localhost:8000
```

## Code Style

- Python 3.11+ with full type annotations
- `ruff` for linting and formatting
- `mypy --strict` for type checking
- Async-first for all I/O operations
- `structlog` for logging (not print or stdlib logging)
- Docstrings on all public functions and classes

## Pull Request / Merge Request Guidelines

1. Branch from `main`, PR/MR back to `main`
2. Keep changes focused one concern per PR
3. Tests must pass (`pytest tests/ -v`)
4. Lint must pass (`ruff check autonomy_loops/`)
5. Add tests for new features
6. Update docs if behavior changes
7. Use conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`

## Project Structure

```
autonomy_loops/     → Core Python package (the framework)
roles/              → Agent persona definitions (markdown)
modes/              → Lifecycle mode definitions (markdown)
plugins/            → Industry-specific knowledge packs (markdown)
pipelines/          → Multi-agent workflow definitions (YAML)
styles/             → Team customization overlays (markdown)
tests/              → Test suite (pytest)
docs/               → Documentation source (MkDocs)
.github/workflows/  → GitHub Actions CI
.gitlab-ci.yml      → GitLab CI/CD
```

## Adding Steering Content

- **New role**: Create `roles/{name}.md`, add tests
- **New mode**: Create `modes/{name}.md`, update `modes/mode-map.json`
- **New plugin**: Create `plugins/{id}/` directory with `.md` files, update `plugins/plugin-registry.json`
- **New pipeline**: Create `pipelines/{name}.yaml` with step definitions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
