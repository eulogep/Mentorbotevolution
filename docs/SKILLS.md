# Skills Strategy

## Purpose

This project uses agent skills to reduce repeated reasoning, improve consistency, and avoid unnecessary refactors.

## Skill-First Protocol

1. Identify the task type.
2. Check local skills.
3. Use `find-skills` only when needed.
4. Select maximum 1–3 relevant skills.
5. Apply the skill within the task scope.
6. Run tests.
7. Document the result.

## Local Skill Locations

- `/home/euloge/.agents/skills`
- `/media/recoveryusb/skills`

## Approved Skill Categories

- Backend Flask
- Database migrations
- SQLAlchemy/PostgreSQL
- Vercel deployment
- Test generation
- PR review
- Security review
- JSON/schema validation
- Playwright/browser testing
- Token/log compression
- Documentation

## Forbidden Usage

Skills must not be used to:
- rewrite the backend in FastAPI
- add Kubernetes/Terraform/Vault
- change Vercel runtime without proof
- modify secrets
- touch payments or production credentials
- expand MCP tools unnecessarily
- mix unrelated PR objectives

## Skill Registry

| Skill | Source | Purpose | Status | Notes |
|------|--------|---------|--------|-------|
| find-skills | vercel-labs/skills | Find relevant skills | Optional | Use only when needed |
| z-schema validating-json-data | zaggino/z-schema | JSON/schema validation | Candidate | Use later for schema validation |
| playwright-test | posthog/posthog | Browser testing | Candidate | Use later for frontend flow tests |
