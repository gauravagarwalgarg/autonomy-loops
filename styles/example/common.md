# Team Conventions (Example)

These are team-specific conventions that layer on top of the base roles and modes.
Copy `styles/example/` to your project and customize.

## General Rules

- All code must pass CI before merge (lint + test + build)
- PR descriptions must explain WHY, not just WHAT
- Use conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`
- Maximum PR size: 400 lines changed (split larger changes)
- All public APIs must have documentation

## Naming Conventions

- Files: `kebab-case.ts`, `snake_case.py`
- Classes: `PascalCase`
- Functions/methods: `camelCase` (TS/JS) or `snake_case` (Python/Rust/Go)
- Constants: `SCREAMING_SNAKE_CASE`
- Boolean variables: prefix with `is`, `has`, `should`, `can`

## Error Handling

- Never catch and ignore exceptions
- Log errors with structured context (not just the message)
- Use custom error types for domain-specific failures
- Include correlation IDs in all error responses
