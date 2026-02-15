# Déploiement sur Vercel - Euloge Learning Platform

## Auteur
**MABIALA EULOGE**

## Configuration du Déploiement

### 1. Structure du Projet pour Vercel
```
euloge-learning-platform/
├── api/
│   └── index.py          # Point d'entrée pour Vercel
├── vercel.json          # Configuration Vercel
├── requirements-vercel.txt  # Dépendances Python
├── gunicorn_config.py   # Configuration Gunicorn
└── package.json         # Scripts de build
```

### 2. Variables d'Environnement Requises
- `AUTHOR`: MABIALA EULOGE
- `PROJECT_NAME`: Euloge Learning Platform
- `DATABASE_URL`: URL de la base de données
- `PYTHON_VERSION`: 3.11

### 3. Étapes de Déploiement

1. **Connexion à Vercel**
   ```bash
   vercel login
   ```

2. **Configuration du Projet**
   ```bash
   vercel link
   ```

3. **Déploiement**
   ```bash
   vercel deploy
   ```

### 4. Points d'Attention

- Le backend Flask est servi via `/api`
- Le frontend React est servi à la racine
- La base de données doit être configurée dans les variables d'environnement Vercel

### 5. Vérification du Déploiement

1. **Santé de l'API**
   ```
   https://[votre-domaine].vercel.app/api/health
   ```

2. **Frontend**
   ```
   https://[votre-domaine].vercel.app
   ```

## Support

Pour toute question sur le déploiement, contactez l'auteur :
- **Auteur** : MABIALA EULOGE
- **GitHub** : [@eulogep](https://github.com/eulogep)

---

© 2024 MABIALA EULOGE - Tous droits réservés
