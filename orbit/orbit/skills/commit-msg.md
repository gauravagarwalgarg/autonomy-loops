---
model: codellama
temperature: 0.2
description: Generate conventional commit message from diff
---
Generate a conventional commit message for the provided git diff.
Format: type(scope): description

Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore
Keep subject under 72 chars. Add body only if changes are complex.
Return ONLY the commit message.
