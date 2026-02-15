<div align="center">

# 🧠 MentorBot Evolution

### Plateforme d'Apprentissage Augmentée par l'IA

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.3+-000000?style=for-the-badge&logo=flask&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-4.4+-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-3.3+-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)
[![Vercel Deployment](https://deploy-badge.vercel.app/vercel/mentorbotevolution)](https://mentorbotevolution.vercel.app)

<p align="center">
  Une approche <b>neuroscientifique</b> de la préparation au TOEIC.<br>
  Analyse de documents par OCR, Plans d'études adaptatifs et Répétition Espacée.
</p>

[Fonctionnalités](#-fonctionnalités-clés) •
[Installation](#-installation) •
[API](#-api) •
[Contribuer](#-contribuer) •
[Démo Live 🚀](https://mentorbotevolution.vercel.app)

</div>

---

## 🚀 Présentation

**MentorBot Evolution** n'est pas juste une autre application de quiz. C'est un **coach personnel intelligent** qui s'adapte à votre façon d'apprendre.

En combinant la puissance de l'IA (**OCR Tesseract, NLP**) avec les principes de la **courbe de l'oubli (Ebbinghaus)**, la plateforme optimise chaque minute de votre temps de révision pour maximiser la rétention à long terme.

## ✨ Fonctionnalités Clés

| Fonctionnalité | Description | Technologie |
| :--- | :--- | :--- |
| **🔐 Auth Sécurisée** | Inscription/Connexion robuste avec JWT et hachage. | `Flask-JWT`, `Werkzeug` |
| **👁️ Analyse Documents** | Extraction de texte et concepts depuis PDF/Images/Texte. | `Tesseract OCR`, `Regex/NLP` |
| **📊 Dashboard** | Suivi visuel de la progression et des métriques d'étude. | `Recharts`, `Radix UI` |
| **🧠 Apprentissage Adaptatif** | Plans générés selon votre chronotype et style d'apprentissage. | `Algorithme SM-2` |
| **🔁 Répétition Espacée** | Système de flashcards intelligent qui prédit quand réviser. | `Python Backend` |

## 🛠️ Stack Technique

**Frontend**

- **Framework**: React 18 + Vite
- **UI/UX**: TailwindCSS, Shadcn/Radix UI, Lucide Icons
- **State**: Context API (Auth), Axios (API)

**Backend**

- **Core**: Python 3.11, Flask
- **Sécurité**: JWT-Extended, Werkzeug Security
- **Data**: SQLAlchemy (ORM), SQLite (Dev) / PostgreSQL (Prod)
- **AI**: Pytesseract, Pillow

## 📂 Structure du Projet

```bash
mentorbotevolution-main/
├── 📂 src/                  # ⚛️ Frontend React
│   ├── 🧩 components/       # Composants UI modulaires
│   ├── 🔐 context/          # Gestion d'état (Auth)
│   ├── 🚦 routes/           # Pages (Login, Dashboard...)
│   └── 🛠️ utils/            # Helpers
├── 📂 src/routes/           # 🐍 Blueprints Backend API
├── 📂 src/models/           # 🗄️ Modèles de BDD
├── 📂 src/utils/            # 🧠 Modules IA (OCR, NLP)
├── 📄 main.py               # Point d'entrée Flask
├── 📄 package.json          # Dépendances Node
└── 📄 requirements.txt      # Dépendances Python
```

## ⚡ Installation Rapide

### Prérequis

- Node.js (v18+)
- Python (v3.10+)
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) (Installé et dans le PATH)

### 1. Clonage & Setup

```bash
git clone https://github.com/eulogep/mentorbotevolution.git
cd mentorbotevolution
```

### 2. Backend (Terminal A)

```bash
# Setup environnement virtuel
python -m venv venv
# Windows: venv\Scripts\activate  |  Mac/Linux: source venv/bin/activate

# Installation deps
pip install -r requirements.txt

# Création fichier .env
echo "SECRET_KEY=dev-secret" > .env
echo "JWT_SECRET_KEY=dev-jwt-secret" >> .env
echo "DATABASE_URL=sqlite:///app.db" >> .env

# Lancement
python main.py
```

### 3. Frontend (Terminal B)

```bash
npm install
npm run dev
```

🚀 **Ouvrez** `http://localhost:3000` pour commencer !

## 🔌 API Endpoints

L'API est accessible via `/api`. Les endpoints protégés nécessitent un header `Authorization: Bearer <token>`.

- **Auth**: `POST /auth/register`, `POST /auth/login`
- **Analysis**: `POST /analysis/analyze-document` (Multipart File)
- **Mastery**: `GET /mastery/subjects`
- **Spaced Repetition**: `GET /spaced-repetition/get-due-cards`

## 🌍 Déploiement

Le projet est déployé en production sur Vercel.

- **URL de Production** : [https://mentorbotevolution.vercel.app](https://mentorbotevolution.vercel.app)
- **Statut** : ✅ En ligne

---
<div align="center">
  <p>Fait avec ❤️ par <a href="https://github.com/eulogep">MABIALA EULOGE</a></p>
</div>
