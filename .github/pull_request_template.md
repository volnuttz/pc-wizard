## Summary

Describe the change and its user-visible effect.

## Scope checklist

- [ ] This change stays within the current level-1 SRD scope, or explains the
      intentional scope expansion.
- [ ] JSON remains the canonical character record and the PDF remains a rendered
      view.
- [ ] Source PDFs and official template fixtures are unchanged.
- [ ] Dependencies are justified when the standard library and current tools are
      insufficient.

## Verification

- [ ] `uv run ruff format --check .`
- [ ] `uv run ruff check .`
- [ ] `uv run pyright`
- [ ] `uv run pytest`
- [ ] Relevant CLI, PDF read-back, binary, packaging, or workflow checks run.

## Documentation

- [ ] Tests cover changed behavior.
- [ ] `docs/roadmap.md` is updated when roadmap scope or status changes.
- [ ] `CHANGELOG.md` includes user-visible changes, if applicable.

## Notes for reviewers

Call out compatibility concerns, known limitations, or follow-up work.
