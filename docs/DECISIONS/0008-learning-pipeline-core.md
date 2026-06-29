# ADR 0008 — Learning Pipeline Core

## Status

Accepted

## Context

MentorBot Evolution needs a clear learning pipeline connecting document analysis, concept extraction, flashcard generation, spaced repetition and progress tracking.

## Decision

Introduce a backend learning pipeline service with explicit heuristic/simulated markers where no external AI is used.

## Constraints

- Keep Flask.
- Do not add external AI APIs.
- Do not change Vercel.
- Do not change database migrations.
- Preserve existing API compatibility.
- Mark simulated or heuristic outputs clearly.

## Consequences

The backend becomes easier to test, extend and connect to future AI features.
