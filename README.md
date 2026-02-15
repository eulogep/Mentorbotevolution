# Euloge Learning Platform – Plateforme d'apprentissage IA

Plateforme moderne basée sur l'IA et les neurosciences, optimisée pour la préparation au TOEIC. Frontend React (Vite + Tailwind + Radix UI) et backend Python (Flask + SQLAlchemy), packagés pour un déploiement serverless sur Vercel.

## Sommaire

- Présentation
- Fonctionnalités clés
- Stack technique
- Structure du projet
- Prérequis
- Installation et démarrage local
- Scripts disponibles
- Variables d'environnement
- API (aperçu des endpoints)
- Tests backend
- Déploiement sur Vercel
- Notes de production
- Licence et Auteur

---

## Présentation

Cette application propose:

- Un tableau de bord de maîtrise des compétences TOEIC
- Des recommandations d'apprentissage basées sur des principes neuroscientifiques
- Un générateur de plan adaptatif
- Un moteur de répétition espacée (style SM-2 modifié)
- Un module d'analyse (simulation OCR/NLP) pour extraire des concepts et générer des exercices

## Fonctionnalités clés

- Visualisation de progression (listening/reading/speaking/writing)
- Recommandations dynamiques et planification hebdomadaire selon chronotype
- Spaced repetition: génération de cartes, calcul d'intervalles, analytics
- Génération de plan d'étude personnalisé (objectif, temps, style d'apprentissage)
- API REST modulaire (Flask Blueprints)

## Stack technique

- Frontend: React 18, Vite 4, TailwindCSS 3, Radix UI, Lucide Icons
- Backend: Python 3.11, Flask 2.3, Flask-CORS, Flask-SQLAlchemy
- Build/Dev: Node.js, NPM scripts, Vite
- Déploiement: Vercel (static-build + fonction Python)
- Base de données: SQLite (local) ou DATABASE_URL en prod (recommandé: Postgres)

## Structure du projet

```text
mentorbotevolution-main/
├─ src/                       # Frontend React
│  ├─ components/
│  ├─ utils/api.js            # Helper fetch + base /api
│  ├─ routes/                 # Blueprints backend (référencés par Flask)
│  ├─ models/
│  ├─ App.jsx, main.jsx, index.css
├─ static/                    # Optionnel: assets statiques servis par Flask
├─ dist/                      # Build frontend (vite build)
├─ api/                       # Point d'entrée API alternatif pour Vercel
├─ docs/                      # Documentation du projet
├─ tests/                     # Tests backend (backend_test.py)
├─ archive/                   # Anciennes versions de fichiers
├─ main.py                    # Serveur Flask (API + fallback SPA)
├─ vercel.json                # Config Vercel (static-build + python)
├─ requirements.txt           # Dépendances Python locales
├─ requirements-vercel.txt    # Dépendances Python pour Vercel
├─ package.json               # Scripts et deps Node
├─ vite.config.js             # Proxy /api vers Flask (dev)
├─ vercel-build.sh            # Script build (optionnel)
├─ .env                       # Variables d'environnement (local, non commité)
└─ README.md                  # Ce document
```

## Prérequis

- Node.js >= 18 et NPM
- Python 3.11 et pip
- Git

## Installation et démarrage local

1) Cloner et installer les dépendances

```bash
git clone https://github.com/eulogep/mentorbotevolution.git
cd mentorbotevolution/mentorbotevolution-main

# Frontend
npm install

# Backend
pip install -r requirements.txt
```

1) Démarrer le backend Flask (port 5000)

```bash
python main.py
```

1) Démarrer le frontend Vite (port 3000)

```bash
npm run dev
```

Le proxy Vite redirige automatiquement les requêtes « /api » vers <http://localhost:5000>.

1) (Optionnel) Tester le build frontend

```bash
npm run build
npm run preview
```

## Scripts disponibles (NPM)

- dev: lance Vite en mode développement
- build: construit le frontend dans dist/
- preview: sert le build localement
- lint: exécute ESLint
- deploy: build + publication GitHub Pages (si utilisé)
- vercel-build: alias de vite build pour CI Vercel

Exemples

```bash
npm run dev
npm run build
npm run preview
npm run lint
```

## Variables d'environnement

Frontend (Vite)

- VITE_API_BASE_URL: URL complète de l'API (par défaut: /api). Exemple .env.local:

```bash
VITE_API_BASE_URL=http://localhost:5000/api
```

Backend (Flask)

- SECRET_KEY: secret Flask
- DATABASE_URL: URI base de données (sinon SQLite est utilisé)
- En local, SQLite se crée sous ./database/app.db
- En environnement Vercel, si aucune DATABASE_URL n'est fournie, SQLite est placé en /tmp (éphémère)

Vercel

- PYTHON_VERSION: 3.11 (défini dans vercel.json)
- Toute variable sensible doit être configurée dans Vercel > Project Settings > Environment Variables

## API (aperçu des endpoints)

Base: /api

User

- POST /api/user/register
  - body: { username, email }
  - 201: { message, user_id }
- POST /api/user/login
  - body: { email }
  - 200: { message, user_id }

Learning

- GET /api/learning/progress -> données de progression simulées
- GET /api/learning/recommendations -> recommandations d'étude

Mastery

- GET /api/mastery/subjects -> liste simple (simulation)
- GET /api/mastery/get-subjects -> format riche pour dashboard
- POST /api/mastery/plan -> crée un plan simple

Analysis

- POST /api/analysis/analyze-document -> upload fichier (simulation OCR/NLP) + concepts + exercices
- POST /api/analysis/generate-plan -> génère un plan adaptatif

Spaced Repetition

- POST /api/spaced-repetition/create-card -> crée une carte
- POST /api/spaced-repetition/review-card -> met à jour l’intervalle d’une carte
- GET  /api/spaced-repetition/get-due-cards -> cartes dues
- GET  /api/spaced-repetition/get-schedule?days_ahead=N -> planning
- POST /api/spaced-repetition/adaptive-settings -> MAJ des paramètres adaptatifs
- GET  /api/spaced-repetition/performance-analytics -> analytics

Exemple rapide

```bash
curl -X GET http://localhost:5000/api/learning/progress
curl -X POST http://localhost:5000/api/user/register -H "Content-Type: application/json" -d '{"username":"test","email":"test@example.com"}'
```

## Tests backend

Un script de tests d’API est fourni: backend_test.py

Par défaut il cible <http://localhost:5000>. Lancez le serveur (`python main.py`) dans un terminal, puis:

```bash
python tests/backend_test.py
```

Le script couvre: health, mastery, learning, spaced-repetition, user register/login, generate-plan.

## Déploiement sur Vercel

Pré-requis

- Vercel CLI installé: `npm i -g vercel` (ou `npx vercel`)
- Compte Vercel lié: `vercel login`

Étapes (CLI)

```bash
vercel link                 # lier le dossier au projet Vercel
vercel                      # déploiement (preview)
vercel --prod               # déploiement production
```

Notes

- vercel.json définit 2 builds:
  - { src: "package.json", use: "@vercel/static-build" } -> build React (dist)
  - { src: "main.py", use: "@vercel/python" } -> API Flask
- Routage:
  - /api/(.*) -> main.py
  - /(.*) -> /index.html (SPA)
- Configurez les variables d’environnement dans Vercel (DATABASE_URL, SECRET_KEY, etc.). SQLite en /tmp est éphémère: préférez une base externe (Postgres/Supabase) en production.

Intégration GitHub (recommandée)

- Connecter le repo GitHub à Vercel pour des déploiements automatiques à chaque push (Preview sur branches, Production sur main).

## Notes de production

- Secrets: ne jamais committer de tokens/API keys. Gérer via variables d’environnement.
- Base de données: SQLite est pratique en local, mais non persistant sur Vercel. Utiliser une base managée (Postgres) via DATABASE_URL pour la prod.
- Sécurité: hasher les mots de passe (ex: argon2/bcrypt) et ajouter une authentification JWT pour sécuriser les endpoints.
- Observabilité: activer des logs/monitoring sur Vercel. Ajouter une route /health dédiée si nécessaire.

## Perspectives et améliorations futures

Pour rendre cette plateforme plus complète et fiable, plusieurs axes de travail sont nécessaires :

1. **Moteur OCR/NLP réel** : remplacer la simulation actuelle d’analyse de document par l’intégration de Tesseract ou d’une autre solution OCR pour extraire le texte, puis utiliser un framework NLP (spaCy, CamemBERT) pour identifier les concepts et générer des exercices adaptés.
2. **Authentification sécurisée** : mettre en place une authentification avec JSON Web Tokens (JWT) et hachage de mot de passe (bcrypt ou argon2), afin de sécuriser les endpoints (`/register`, `/login`) et de protéger les données des utilisateurs.
3. **Persistance et observabilité** : migrer la base de données vers un service persistant (Postgres/Supabase) et configurer un système de logs et de monitoring. Introduire des migrations (Alembic) et améliorer l’API pour tracer les performances.
4. **Algorithmes de recommandation** : expliciter et implémenter les modèles neuroscientifiques sous‑jacents (courbe de l’oubli, chronotypes) afin de personnaliser la répétition espacée et les plans d’étude.

## Licence et Auteur

- Licence: MIT (voir fichier LICENSE)
- Auteur: MABIALA EULOGE (@eulogep)
- Projet: Euloge Learning Platform – Plateforme d’apprentissage IA
