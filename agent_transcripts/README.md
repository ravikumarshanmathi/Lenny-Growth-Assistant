# Agent Transcripts

This directory captures AI coding agent prompt histories and iteration logs for audit, reproducibility, and evaluator review.

## Purpose

- **Traceability:** Record what prompts were used, what changes were made, and the reasoning behind architectural decisions.
- **Evaluation:** Demonstrate the iterative development process for assignment review.
- **Debugging:** Enable post-hoc analysis of agent-assisted code generation.

## Naming Convention

```
{phase}_{task_description}_{timestamp}.md
```

Example: `phase1_repo_scaffold_2026-10-10.md`

## Contents

Each transcript should include:
1. The prompt/instruction given to the agent
2. Key decisions made during the iteration
3. Files created or modified
4. Any issues encountered and how they were resolved
