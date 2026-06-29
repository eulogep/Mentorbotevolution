# ADR 0004 : Ne pas migrer vers FastAPI maintenant

## Statut
Accepté

## Contexte
Des propositions ont été faites pour migrer le backend de Flask vers FastAPI afin de bénéficier de l'asynchronisme natif et de la validation Pydantic.

## Décision
Nous rejetons la migration vers FastAPI à ce stade du projet.
- **Complexité de réécriture** : La réécriture totale des filtres SQLAlchemy, des configurations CORS, de l'authentification JWT et de la structure des Blueprints Flask consommerait trop de temps et de ressources pour un gain marginal immédiat.
- **Absence de besoin de performances asynchrones massives** : Les requêtes d'entraînement individuelles de la plateforme n'ont pas besoin d'un niveau de concurrence nécessitant de l'E/S asynchrone (asyncio).

## Conséquences
- Nous conservons le modèle synchrone classique de Flask (avec threading standard géré par Gunicorn en production).
- Tout agent futur doit respecter cette contrainte et ne pas tenter de portage vers FastAPI.
