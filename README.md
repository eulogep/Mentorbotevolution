# Euloge Learning Platform – Plateforme d'apprentissage IA

Plateforme moderne d'apprentissage adaptatif, optimisée pour la préparation au TOEIC par des principes neuroscientifiques.
Frontend React (Vite + Tailwind + Radix UI) et backend Python (Flask + SQLAlchemy), sécurisés et augmentés par l'IA.

## Sommaire

- [Présentation](#présentation)
- [Fonctionnalités clés](#fonctionnalités-clés)
- [Stack technique](#stack-technique)
- [Structure du projet](#structure-du-projet)
- [Prérequis](#prérequis)
- [Installation et démarrage local](#installation-et-démarrage-local)
- [Configuration](#configuration)
- [API](#api)
- [Déploiement](#déploiement)
- [Licence](#licence)

---

## Présentation

Cette application propose une approche personnalisée de l'apprentissage :

- **Tableau de bord de maîtrise** : Suivi détaillé par compétence.
- **Plans adaptatifs** : Générés par IA selon votre profil et vos objectifs.
- **Répétition espacée** : Algorithme SM-2 optimisé pour la rétention long terme.
- **Analyse de documents (OCR/NLP)** : Extraction automatique de concepts à partir de vos cours (PDF, Images, Texte) pour générer des exercices.

## Fonctionnalités clés

- **Authentification Sécurisée** : Inscription/Connexion avec JWT et hachage de mots de passe.
- **OCR & NLP Réels** : Utilisation de Tesseract et Regex/NLP pour analyser le contenu réel des documents uploadés.
- **Visualisation de progression** : Graphiques interactifs de vos performances.
- **Recommandations dynamiques** : Basées sur votre chronotype et votre style d'apprentissage.

## Stack technique

- **Frontend** : React 18, Vite, TailwindCSS, Axios, Recharts, Lucide Icons.
- **Backend** : Python 3.11+, Flask 2.3+, Flask-JWT-Extended, Flask-SQLAlchemy.
- **IA/Data** : Pytesseract (OCR), Pillow, Scikit-learn (simulé/futur), Spacy/Regex (NLP).
- **Base de données** : SQLite (Dev) / PostgreSQL (Prod).

## Structure du projet

```text
mentorbotevolution-main/
├─ src/                       # Frontend React
│  ├─ components/             # Composants UI (MasteryPlan, etc.)
│  ├─ context/                # Gestion d'état (AuthContext)
│  ├─ routes/                 # Pages (Login, Register, Dashboard)
│  ├─ models/                 # Modèles de données frontend
│  ├─ utils/                  # Utilitaires frontend
│  ├─ App.jsx, main.jsx       # Entrée React
├─ backend/                   # (Dossier optionnel, code à la racine pour Vercel)
├─ src/routes/                # Blueprints Backend (API endpoints)
├─ src/models/                # Modèles SQLAlchemy (User, etc.)
├─ src/utils/                 # Utilitaires Backend (OCR, NLP)
├─ main.py                    # Point d'entrée Flask
├─ requirements.txt           # Dépendances Python
├─ package.json               # Dépendances Node
├─ .env                       # Secrets (non versionné)
└─ README.md                  # Documentation
```

## Prérequis

1. **Node.js** (v18+) et **npm**.
2. **Python** (v3.10+).
3. **Tesseract-OCR** : Doit être installé sur votre machine pour l'analyse d'images.
    - *Windows* : [Installeur UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) (Ajouter au PATH).
    - *Linux* : `sudo apt-get install tesseract-ocr`.
    - *Mac* : `brew install tesseract`.

## Installation et démarrage local

### 1. Backend (Flask)

```bash
# Créer un environnement virtuel (recommandé)
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 2. Frontend (React)

```bash
npm install
```

### 3. Configuration (.env)

Créez un fichier `.env` à la racine :

```ini
SECRET_KEY=votre_cle_secrete_super_securisee
JWT_SECRET_KEY=votre_cle_jwt_secrete
DATABASE_URL=sqlite:///app.db
# Tesseract path si non détecté automatiquement (optionnel)
# TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### 4. Lancement

**Terminal 1 (Backend)** :

```bash
python main.py
# Serveur sur http://localhost:5000
```

**Terminal 2 (Frontend)** :

```bash
npm run dev
# Application sur http://localhost:3000
```

## Configuration

### Variables d'environnement

- `SECRET_KEY` : Sécurisation des sessions Flask.
- `JWT_SECRET_KEY` : Signature des tokens d'authentification.
- `DATABASE_URL` : Connexion BDD (ex: `postgresql://user:pass@host/db`).

## API

L'API est préfixée par `/api`.

- **Auth**
  - `POST /api/user/register` : Créer un compte.
  - `POST /api/user/login` : Se connecter (retourne Access Token).

- **Analysis**
  - `POST /api/analysis/analyze-document` : Upload document -> Extraction Concepts.
  - `POST /api/analysis/generate-plan` : Création de plan (Protégé JWT).

- **Mastery & Spaced Repetition**
  - Endpoints pour la gestion des sujets et des révisions.

## Déploiement

Le projet est configuré pour **Vercel** (Frontend + Backend Serverless).

- `vercel.json` inclus à la racine.
- Nécessite une base de données externe (ex: Supabase, Neon) pour la production, car SQLite est éphémère sur Vercel.

## Licence

MIT License.
Auteur: MABIALA EULOGE (@eulogep)
