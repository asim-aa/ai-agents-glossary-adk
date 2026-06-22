
---

## Step 9 — Fill in `docs/architecture.md`

Open `docs/architecture.md` and paste:

```markdown
# Architecture

## Why Sequential Pipeline?

This project uses a fixed staged pipeline instead of an autonomous routing coordinator.

The goal is not to let the model decide which agent to call next. The goal is to guarantee that the same writer-reviewer-reviser process runs in the same order every time.

## Pipeline

```text
Term Planner
    ↓
Definition Writer
    ↓
Definition Reviewer
    ↓
Definition Reviser
    ↓
Glossary Writer A
    ↓
Glossary Writer B
    ↓
Glossary Reviewer
    ↓
Glossary Reviser
    ↓
Review Summary Writer
    ↓
Final Assembler