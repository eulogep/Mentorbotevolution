# Mentor Evolution

Mentor Evolution est une plateforme personnelle d’apprentissage **multi-domaines**. Elle combine rappel actif, répétition espacée adaptative et suivi de pratique pour l’anglais, l’informatique, Excel, Power BI, le réseau, la cybersécurité et les parcours libres. Le TOEIC est un parcours de référence, non la limite du modèle de données.

Le projet conserve une architecture React/Vite côté client et Flask/SQLAlchemy côté API. SQLite est adapté au développement local ; PostgreSQL est recommandé pour un déploiement durable via `DATABASE_URL`.

## Fonctionnalités disponibles

| Fonction | État |
|---|---|
| Authentification par inscription, connexion et JWT | Disponible |
| Catalogue de parcours explicites | Disponible : TOEIC, informatique, Excel, Power BI, réseau, cybersécurité et parcours libre |
| Parcours « Préparation TOEIC » | Disponible avec un socle original de 36 cartes de vocabulaire professionnel, immédiatement planifiées dans le domaine Langues |
| Parcours « Fondamentaux de l’informatique » | Disponible avec cinq notions initiales : données, algorithmique, systèmes, réseau et hygiène numérique |
| Sujets, notions et critères de preuve | Persistés et génériques par domaine |
| Cartes et répétition espacée FSRS | Disponibles, avec journal de revue et rétention cible configurable |
| Session de rappel actif | Disponible : réponse avant correction, évaluation explicite, feedback et prochaine échéance |
| Analytics personnels | Disponibles à partir des journaux de révision réels |
| Import de documents | Disponible pour texte brut, images OCR et PDF avec texte ou OCR de secours |

## Principes de produit

> Les modèles de parcours offrent une structure de départ ; ils ne constituent ni diagnostic de niveau, ni promesse de réussite, ni certification.

Les connaissances, procédures, productions et diagnostics ne sont pas confondus. FSRS planifie le rappel à long terme des notions, mais une compétence appliquée exige en plus une activité et une preuve adaptées au domaine. Les parcours cyber doivent rester défensifs et s’appuyer sur des laboratoires ou environnements explicitement autorisés.

Le projet ne personnalise pas les contenus à partir de « styles d’apprentissage » supposés, de chronotype ni de probabilités individuelles de réussite. Les réglages utiles sont la disponibilité, l’échéance, les objectifs formulés et les données de pratique observées.

## Architecture de domaine

| Niveau | Rôle |
|---|---|
| Domaine | Langues, informatique, bureautique, données, infrastructure, cybersécurité ou parcours libre |
| Parcours | Objectif personnel, modèle choisi ou parcours libre ; il peut porter une échéance et un rythme hebdomadaire |
| Compétence / notion | Élément à comprendre, appliquer, produire, diagnostiquer ou expliquer |
| Activité | Rappel, auto-explication, exercice pratique, diagnostic ou production ; les activités pratiques seront enrichies progressivement |
| Preuve | Résultat observable d’une activité ; les cartes FSRS seules ne sont pas une certification |

La documentation détaillée se trouve dans [l’architecture multi-domaines](docs/ARCHITECTURE_MULTI_DOMAINES_2026-08-11.md), [l’audit de généralisation](docs/AUDIT_GENERALISATION_MULTI_DOMAINES_2026-08-11.md), les [notes de recherche](docs/RECHERCHE_MULTI_DOMAINES_2026-08-11.md) et le [socle TOEIC initial](docs/PARCOURS_TOEIC_FONDATIONS.md).

## Limites actuelles et prochaines étapes

L’extraction de notions depuis un document reste heuristique. Lorsqu’aucun texte ou concept exploitable ne peut être extrait, l’API renvoie un état vide nécessitant une saisie manuelle ; elle n’invente pas de contenu TOEIC ni de fausse analyse.

Les prochains incréments concernent les activités pratiques et preuves pour Excel, Power BI et programmation, puis les parcours réseau et cybersécurité fondés sur tâches et laboratoires autorisés. L’optimisation fine de la planification ne sera considérée qu’après un historique réel de revues.

## Prérequis

- Node.js 18 ou plus récent.
- Python 3.12 recommandé.
- Tesseract OCR pour l’analyse d’images et de PDF scannés.
- PostgreSQL, optionnel en local et recommandé en production.

## Installation locale

```bash
npm install
python -m venv .venv
```

Sous Linux ou macOS :

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Sous Windows PowerShell :

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Créez ensuite un fichier `.env`. En l’absence de `DATABASE_URL`, l’application utilise `database/app.db` en développement.

```env
SECRET_KEY=dev-secret-change-me
JWT_SECRET_KEY=dev-jwt-secret-change-me
# Optionnel : DATABASE_URL=sqlite:///database/app.db
```

Après une mise à jour du schéma, utilisez Alembic :

```bash
python -m flask --app main db upgrade
```

## Lancement et validation

Démarrez le backend puis le frontend dans deux terminaux :

```bash
python main.py
npm run dev
```

Les validations principales sont les suivantes :

```bash
python -m compileall main.py src api backend tests
python -m pytest -q
npm run lint
npm run build
```

## API principale

| Endpoint | Usage |
|---|---|
| `POST /api/user/register` et `POST /api/user/login` | Authentification |
| `GET /api/mastery/catalog` | Catalogue de modèles et domaines, sans création automatique |
| `POST /api/mastery/create-path` | Création explicite d’un parcours libre ou depuis un modèle |
| `GET /api/mastery/get-subjects` | Parcours persistés de l’utilisateur |
| `POST /api/analysis/analyze-document` | Extraction de texte et notions, avec retour honnête si une saisie est nécessaire |
| `POST /api/spaced-repetition/create-card` | Création d’une carte |
| `POST /api/spaced-repetition/review-card` | Revue FSRS avec note explicite |
| `GET /api/spaced-repetition/get-due-cards` | Cartes réellement dues |
| `GET /api/spaced-repetition/performance-analytics` | Analytics descriptifs de pratique |

## Déploiement

Le fichier `vercel.json` conserve un déploiement Vite avec fonction Flask via `api/index.py`. Pour une production durable, configurez `DATABASE_URL` vers PostgreSQL, installez `requirements-vercel.txt`, puis appliquez les migrations. SQLite dans `/tmp` sur Vercel reste un fallback temporaire, non une base de production.
