# Code Mode Team Style (Example)

## Additional Coding Standards

- Maximum function length: 30 lines (excluding blank lines and comments)
- Maximum file length: 300 lines
- Maximum cyclomatic complexity: 10
- All functions must have type annotations (Python) or TypeScript strict mode
- No `any` types in TypeScript use `unknown` and narrow

## Dependency Rules

- No new dependencies without team discussion
- Pin exact versions in requirements/lockfiles
- Check for known vulnerabilities before adding (Snyk, npm audit)
- Prefer standard library over third-party for simple tasks

## Performance

- All database queries must use indexes (explain plan in PR)
- No N+1 queries use eager loading or batch fetching
- API responses must complete in < 200ms (p95)
- Use pagination for list endpoints (default 20, max 100)
