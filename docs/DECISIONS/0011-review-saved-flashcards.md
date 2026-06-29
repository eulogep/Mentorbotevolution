# ADR 0011 — Review Saved Flashcards

## Status

Accepted

## Context

Pipeline flashcards can now be saved into the existing card system, but users need a way to review them.

## Decision

Add a scoped review flow for saved flashcards using existing spaced repetition models and routes.

## Constraints

- No database migration.
- No new dependencies.
- Keep Flask.
- Keep JWT protection.
- Preserve existing routes.
- Use existing Card and StudySession fields.
- Do not modify Vercel.

## Consequences

Users can now revise saved pipeline flashcards through a basic but functional review session.
