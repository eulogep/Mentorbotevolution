# MentorBot Evolution

Plateforme d'apprentissage TOEIC avec frontend React/Vite et backend Flask.

Le projet est stabilise progressivement. Il garde l'architecture actuelle:
React/Vite cote client, Flask + SQLAlchemy cote API, SQLite en local et
PostgreSQL possible via `DATABASE_URL`.

## Fonctionnalites disponibles

- Authentification utilisateur avec inscription, connexion et JWT.
- Backend Flask expose sous `/api`.
- Modeles SQLAlchemy pour utilisateurs, sujets, concepts, flashcards et sessions d'etude.
- Plans de maitrise TOEIC basiques.
- Repetition espacee avec cartes persistantes et algorithme SM-2 simplifie.
- Analyse de documents:
  - texte brut;
  - images via OCR Tesseract;
  - PDF avec extraction de texte PyMuPDF;
  - OCR de secours pour PDF scannes quand aucun texte embarque n'est trouve.
- Frontend React/Vite avec dashboard, upload de documents et vues de repetition espacee.

## Fonctionnalites partiellement implementees

- L'analyse NLP reste heuristique: extraction de mots/concepts par frequence et regex.
- Les recommandations d'apprentissage sont encore simples et parfois statiques.
- Certains fallbacks generent des concepts TOEIC simules quand aucun texte exploitable
  n'est extrait. Ces reponses sont marquees par `is_simulated: true`.
- La persistance sur Vercel peut fonctionner avec SQLite dans `/tmp`, mais ce stockage
  est ephemere et ne convient pas a une vraie production.

## Fonctionnalites prevues

- Brancher une base PostgreSQL geree en production via `DATABASE_URL`.
- Ajouter de vraies migrations de schema.
- Remplacer progressivement les heuristiques NLP par une analyse plus robuste.
- Ameliorer les tests d'integration frontend/backend.
- Ajouter un suivi de progression plus precis et moins statique.

## Limites connues

- Pas de migration vers FastAPI prevue a court terme.
- Pas de Kubernetes, Terraform, Vault, Redis, S3 ou file cloud queue dans cette phase.
- L'OCR depend d'une installation Tesseract disponible sur la machine ou l'environnement.
- Les fichiers DOCX ne sont pas encore extraits reellement.
- Les tests historiques dans `tests/backend_test.py` ciblent un serveur HTTP lance a part;
  les tests pytest modernes sont dans `tests/test_backend_flask.py`.

## Prerequis

- Node.js 18 ou plus recent.
- Python 3.12 recommande.
- Tesseract OCR pour l'analyse d'images et le fallback OCR des PDF scannes.
- PostgreSQL optionnel pour un environnement proche production.

## Installation locale

```bash
npm install
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Linux/macOS:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Creer un fichier `.env` local. `DATABASE_URL` est optionnel en developpement:
si la variable est absente, l'application utilise automatiquement
`database/app.db`.

```env
SECRET_KEY=dev-secret-change-me
JWT_SECRET_KEY=dev-jwt-secret-change-me
# Optionnel: DATABASE_URL=sqlite:///database/app.db
```

Pour PostgreSQL:

```env
DATABASE_URL=postgresql://user:password@host:5432/mentorbot
```

## Lancement

Backend Flask:

```bash
python main.py
```

Frontend Vite:

```bash
npm run dev
```

Build frontend:

```bash
npm run build
```

Lint frontend:

```bash
npm run lint
```

## Tests

Tests Flask rapides:

```bash
python -m pytest tests/test_backend_flask.py -q
```

Compilation Python:

```bash
python -m compileall main.py src api backend tests
```

Audit npm:

```bash
npm audit --audit-level=moderate
```

## API principale

- `POST /api/user/register`
- `POST /api/user/login`
- `GET /api/health`
- `POST /api/analysis/analyze-document`
- `POST /api/analysis/generate-plan`
- `POST /api/analysis/update-progress`
- `POST /api/spaced-repetition/create-card`
- `POST /api/spaced-repetition/review-card`
- `GET /api/spaced-repetition/get-due-cards`
- `GET /api/spaced-repetition/get-schedule`
- `GET /api/learning/progress`
- `GET /api/mastery/get-subjects`

## Deploiement

Le fichier `vercel.json` conserve un deploiement Vite + fonction Python Flask via
`api/index.py`.

Pour une production durable, configurer `DATABASE_URL` vers PostgreSQL. Sans cette
variable, Vercel retombe sur SQLite dans `/tmp`, ce qui est uniquement un fallback
temporaire.
