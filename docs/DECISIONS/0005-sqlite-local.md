# ADR 0005 : Garder SQLite pour local/test

## Statut
Accepté

## Contexte
Pour exécuter et tester rapidement l'application en local sans nécessiter de base de données lourde à configurer (Docker, instance PostgreSQL locale), SQLite offre un environnement fichier léger et sans configuration (*zero-config*).

## Décision
Nous conservons SQLite comme base de données par défaut pour le développement local et l'exécution de la suite de tests d'intégration.

## Conséquences
- En l'absence de variable `DATABASE_URL`, l'application s'initialise automatiquement sur SQLite dans `database/app.db` (ou `/tmp/app.db` sur Vercel en mode fallback).
- Les fichiers binaires de base de données (e.g. `*.db`, `*.sqlite3`) ne doivent **pas** être poussés sur GitHub (ils doivent être exclus via `.gitignore`).
- La base SQLite locale peut être supprimée à tout moment par les scripts de test pour être recréée à partir du schéma SQLAlchemy.
