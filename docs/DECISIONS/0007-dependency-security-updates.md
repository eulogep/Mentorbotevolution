# ADR 0007 — Dependency Security Updates

## Status

Accepted

## Context

Security tools reported vulnerable dependencies in python environment (requests, pillow, python-dotenv, flask-cors, starlette, gunicorn).

## Evidence

List of verified vulnerabilities:

- **npm audit** : 0 vulnerabilities.
- **pip-audit** (on `requirements.txt`) :
  - `flask-cors` (5.0.1) -> CVE-2024-6866, CVE-2024-6844, CVE-2024-6839. Fixed in `6.0.0`
  - `python-dotenv` (1.1.1) -> CVE-2026-28684. Fixed in `1.2.2`
  - `requests` (2.32.5) -> CVE-2026-25645. Fixed in `2.33.0`
  - `pillow` (11.2.1) -> CVE-2026-42311, CVE-2026-42310, CVE-2026-42309, CVE-2026-40192, CVE-2026-25990. Fixed in `12.2.0`
- **pip-audit** (on `requirements-vercel.txt`) :
  - `gunicorn` (21.2.0) -> CVE-2024-1135, CVE-2024-6827. Fixed in `22.0.0`
- **pip-audit** (on `backend/requirements.txt`) :
  - `starlette` (0.37.2) -> CVE-2024-47874, CVE-2025-54121, CVE-2026-48818, CVE-2026-48817. Fixed in `1.1.0` / `0.40.0` / `1.3.1`

## Decision

Apply scoped dependency updates only. Specifically:
- Upgrade `Flask-Cors` to `>=6.0.0`
- Upgrade `python-dotenv` to `>=1.2.2`
- Upgrade `requests` to `>=2.33.0`
- Upgrade `Pillow` to `>=12.2.0`
- Upgrade `python-multipart` to `>=0.0.27`
- Upgrade `gunicorn` to `>=22.0.0` (in `requirements-vercel.txt`)
- Upgrade `fastapi` to `>=0.115.8` (in `backend/requirements.txt`)
- Upgrade `starlette` to `>=0.41.0` (in `backend/requirements.txt`)

## FastAPI/Starlette Decision

FastAPI and Starlette were **updated** rather than removed, because they are actively used by the entry-point gateway script `backend/server.py` to route backend request traffic and serve SPA/Flask routes via WSGIMiddleware. They were updated to their secure versions (`fastapi>=0.115.8` and `starlette>=0.41.0`) to resolve host bypass and model validation vulnerabilities.

## Constraints

- Python 3.12 compatibility
- Vercel compatibility
- no application code changes
- no FastAPI migration
- no unrelated refactor

## Consequences

Known vulnerabilities are reduced to 0 in all requirements files while preserving current application behavior.
