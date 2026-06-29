# Database Migrations

MentorBot Evolution uses Flask-SQLAlchemy for models and Flask-Migrate/Alembic
for schema migrations.

## Local SQLite vs Production PostgreSQL

Local development can run without `DATABASE_URL`. In that case, the app falls
back to `database/app.db`.

Production should use PostgreSQL through `DATABASE_URL`:

```env
DATABASE_URL=postgresql://user:password@host:5432/mentorbot
```

URLs that start with `postgres://` are normalized to `postgresql://` by
`get_database_uri()` for SQLAlchemy compatibility.

## Flask App Setup

Set `FLASK_APP` before running migration commands.

Windows PowerShell:

```powershell
$env:FLASK_APP="main.py"
```

Linux/macOS:

```bash
export FLASK_APP=main.py
```

## Apply Existing Migrations

```bash
flask db upgrade
```

or:

```bash
python -m flask db upgrade
```

## Create a New Migration

After changing models in `src/models/user.py`, generate a migration:

```bash
flask db migrate -m "Describe schema change"
```

Review the generated file in `migrations/versions/`, then apply it:

```bash
flask db upgrade
```

## Initial Migration

The initial migration creates the existing tables:

- `user`
- `subject`
- `concept`
- `card`
- `study_session`

## About db.create_all()

`db.create_all()` remains as a temporary SQLite development fallback so tests and
simple local runs keep working. It is not the long-term production schema
strategy. PostgreSQL deployments should run Alembic migrations with
`flask db upgrade`.

Set `AUTO_CREATE_DB=false` to disable automatic table creation explicitly.
