# ADR 0006 : Database Migrations Strategy

## Statut
Accepté

## Contexte
L'application utilise Flask + Flask-SQLAlchemy. Auparavant, les schémas de base de données étaient gérés via des appels directs à `db.create_all()`. Cela pose problème pour la production, notamment avec une base PostgreSQL distante (par exemple sur Supabase, Neon, ou AWS RDS) où les migrations incrémentales sont indispensables pour éviter les pertes de données et assurer le suivi des schémas.

## Décision
1. Nous introduisons et configurons **Flask-Migrate** (basé sur Alembic) pour gérer les schémas de base de données de manière incrémentale.
2. Nous conservons SQLite comme base locale (`database/app.db`) et en mémoire pour les tests unitaires afin de garantir une exécution locale rapide et sans friction.
3. PostgreSQL est configuré pour être utilisé en production via la variable d'environnement `DATABASE_URL`. Les adresses utilisant l'ancienne désignation `postgres://` sont automatiquement converties en `postgresql://`.
4. La création automatique `db.create_all()` reste activée en local/test (lorsque le schéma SQLite est détecté ou avec la variable `AUTO_CREATE_DB=true`) pour éviter que les tests locaux ne nécessitent le passage forcé par une migration.
5. Nous rejetons la migration vers FastAPI à cette étape car cela nécessiterait de récrire l'ensemble des contrôleurs, middleware de sécurité JWT et intégrations de base de données existantes.
6. Le nettoyage des vulnérabilités NPM et le refactoring d'autres services ne sont pas inclus dans cette PR afin de conserver un scope de commit strictement limité aux migrations DB.

## Conséquences
- Les changements sur les modèles SQLAlchemy dans `src/models/user.py` doivent être suivis par la génération d'une nouvelle migration via `flask db migrate`.
- Les déploiements en production sur Vercel/PostgreSQL doivent appliquer les migrations en exécutant `flask db upgrade` (par exemple au build ou lors d'un script de démarrage).
