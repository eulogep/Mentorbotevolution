# Database Strategy

## Local development

SQLite is used by default for local development and tests.
In local environments, if no `DATABASE_URL` is configured, the application falls back to `database/app.db`.

## Production

PostgreSQL should be used through DATABASE_URL.
URLs starting with `postgres://` are automatically normalized to `postgresql://` for SQLAlchemy compatibility.

## Migrations

Use Flask-Migrate/Alembic.

### Initialize migrations

To initialize the migration environment in the project (only run once if `migrations/` does not exist):
```bash
# Windows PowerShell
$env:FLASK_APP="main.py"
flask db init

# Linux / WSL / macOS
export FLASK_APP=main.py
flask db init
```

### Create a migration

Whenever you modify SQLAlchemy models (e.g. in `src/models/user.py`), generate a new migration file:
```bash
flask db migrate -m "Description of changes"
```
Review the generated script under `migrations/versions/` to verify it maps to your changes.

### Apply migrations

To apply pending migrations to the database (both locally and in production):
```bash
flask db upgrade
```

### Rollback

To rollback the last applied migration:
```bash
flask db downgrade
```

## Important note

`db.create_all()` is acceptable for local bootstrap/testing, but migrations are the production strategy.
Automatic table creation via `db.create_all()` runs only on SQLite default configurations or if `AUTO_CREATE_DB` env is set to `true`.
