# ADR 0009 — Display Learning Pipeline

## Status

Accepted

## Context

The backend now returns a learning pipeline block after document analysis.

## Decision

Display the learning pipeline in the frontend while preserving the existing analysis UI.

## Constraints

- No backend changes.
- No new API.
- No database changes.
- No Vercel changes.
- Must gracefully handle responses without `pipeline`.
- Must clearly mark heuristic/simulated output.

## Consequences

Users can now see the generated learning path, concepts, flashcards and review plan directly after analyzing a document.
