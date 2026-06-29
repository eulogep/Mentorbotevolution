# ADR 0001 : Garder Flask pour l'instant

## Statut
Accepté

## Contexte
Le backend de l'application est écrit en Flask. Il utilise Flask-SQLAlchemy pour la persistance, Flask-CORS pour le cross-origin et Flask-JWT-Extended pour l'authentification et les sessions sécurisées.

## Décision
Nous conservons Flask comme framework backend principal à court/moyen terme.
- L'infrastructure existante fonctionne de manière fluide et tous les modules de logique métier et d'authentification y sont étroitement liés.
- Flask s'exécute de façon stable sur l'environnement serverless Vercel en utilisant `@vercel/python`.

## Conséquences
- Toute nouvelle route API doit être ajoutée sous forme de Blueprint Flask et enregistrée dans `main.py`.
- Le point d'entrée `api/index.py` doit relayer l'instance `app` de `main.py` de manière transparente.
