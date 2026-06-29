# ADR 0010 — Save Pipeline Flashcards

## Status

Accepted

## Context

The learning pipeline can generate heuristic flashcards from analyzed documents, but users need to save them as real reviewable cards.

## Decision

Add a scoped backend import endpoint and a frontend action to save generated pipeline flashcards into the existing card system.

## Constraints

- No database migration.
- No external AI API.
- Keep Flask.
- Keep JWT protection.
- Preserve existing routes.
- Preserve pipeline transparency.
- Do not modify Vercel or dependencies.

## Consequences

Users can now transform generated pipeline output into persistent learning material.
