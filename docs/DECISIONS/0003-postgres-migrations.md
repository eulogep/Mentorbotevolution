# ADR 0003 : Préparer PostgreSQL via des migrations

## Statut
Accepté

## Contexte
Actuellement, l'application utilise une base de données locale SQLite. SQLite n'est pas adapté pour les déploiements serverless en production (comme Vercel) car le système de fichiers est éphémère (les données dans `/tmp` sont perdues à chaque redémarrage de la fonction lambda). Nous devons migrer vers une base relationnelle persistante distante (PostgreSQL).

## Décision
Nous préparons l'application à supporter PostgreSQL pour l'environnement de production. Pour cela, nous utiliserons un système de migrations (Alembic / Flask-Migrate) afin d'assurer l'évolution fluide du schéma de base de données.

## Conséquences
- L'URL de la base de données doit être fournie dynamiquement via la variable d'environnement `DATABASE_URL` (détectant le protocole `postgresql://`).
- Le code SQL brut doit être proscrit : toutes les requêtes doivent passer par l'ORM SQLAlchemy pour garantir la compatibilité double SQLite (dev) / PostgreSQL (prod).
- Flask-Migrate doit être configuré lors de la transition pour générer les fichiers de migration dans un dossier `migrations/`.
