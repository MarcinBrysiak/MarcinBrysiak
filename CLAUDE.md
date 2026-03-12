# CLAUDE.md

This file provides guidance for AI assistants working in this repository.

## Repository Overview

This is a **GitHub profile repository** (`MarcinBrysiak/MarcinBrysiak`). GitHub treats a repository that shares the same name as the account owner as a special profile repository — its `README.md` is automatically rendered on the owner's public GitHub profile page at https://github.com/MarcinBrysiak.

## Repository Structure

```
MarcinBrysiak/
└── README.md   # GitHub profile page content (publicly visible)
```

There is no application code, build system, test suite, or dependency manifest in this repository.

## Purpose

The sole purpose of this repository is to display a personal introduction on the GitHub profile. The current README describes:

- Professional interest: medtech
- Current focus: data science
- Collaboration interest: global medtech companies
- Contact: https://www.linkedin.com/in/marcinbrysiak/

## Development Workflow

### Making Changes

1. Edit `README.md` directly — it is the only meaningful file.
2. Commit with a clear message describing what changed (e.g., `Update bio to reflect new role`).
3. Push to the appropriate branch and open a pull request targeting `master`.

### No Build or Test Steps

There are no build commands, linters, test runners, or CI pipelines configured. Changes take effect on the GitHub profile as soon as they are merged to the default branch (`master`).

## Conventions

- Keep the profile README concise and personal.
- Use Markdown formatting supported by GitHub's renderer (headings, lists, links, badges, HTML comments).
- The hidden HTML comment block at the bottom of `README.md` is a GitHub-generated note and should be preserved.
- Avoid committing sensitive information (credentials, personal contact details beyond what is intentionally public).

## Branch Strategy

| Branch | Purpose |
|--------|---------|
| `master` | Default branch; content here is live on the profile |
| `claude/*` | Branches used by AI assistants for proposed changes |

## Key Notes for AI Assistants

- **No code analysis needed** — there is no application logic to review.
- **Changes are immediately public** — anything merged to `master` appears on the GitHub profile page.
- **Minimal scope** — only edit `README.md` unless explicitly asked to add new files.
- **Markdown only** — output should be valid GitHub-flavored Markdown.
