# 🛡️ Agent Guidelines & Rules

Ce document regroupe les règles de développement, de comportement et d'interaction pour tout agent IA travaillant sur ce dépôt.

---

## 🤝 Pair Programming & Interaction
- **Transparence** : Expliquez brièvement l'intention technique d'une action avant de l'exécuter.
- **Préservation** : Ne supprimez pas les docstrings, commentaires ou blocs de code existants sauf s'ils sont explicitement obsolètes ou demandés à la suppression par l'utilisateur.
- **Modération** : Ne proposez pas de refactorisations massives ou de réécritures complètes de frameworks existants (e.g., migrer de Flask à FastAPI ou de React à Next.js) sans accord écrit dans un plan d'implémentation approuvé.

---

## 🪤 Pièges Connus (Known Traps)

Pour éviter de casser le projet en production ou en local, gardez à l'esprit ces pièges récurrents :

### 1. Ne pas casser le déploiement Vercel Python 3.12/3.11
- Vercel utilise le fichier `api/index.py` comme point d'entrée serverless par défaut, lequel importe `main.py`.
- Toute dépendance ajoutée à `requirements.txt` **doit** également être reportée dans `requirements-vercel.txt` avec sa version épinglée.
- N'utilisez pas de fonctionnalités de Python 3.13+ non supportées par la runtime Vercel active (actuellement configurée en Python 3.11/3.12).

### 2. Ne pas rendre Tesseract-OCR obligatoire au démarrage
- L'application intègre une détection d'image par OCR via Tesseract. Cependant, le binaire Tesseract n'est pas forcément présent dans le PATH des machines de dev ou de production.
- Le fichier `src/utils/ocr.py` ne doit **jamais** lever d'exception bloquante ou empêcher le serveur Flask de démarrer si Tesseract est introuvable.
- S'il est absent, l'application doit journaliser un warning et retourner un fallback de texte simulé de façon transparente.

### 3. Ne pas masquer une simulation comme vraie IA
- L'analyse de documents par OCR/NLP et l'algorithme SM-2 sont réels et connectés en base de données.
- Certaines parties de l'explication et de la génération d'exercices restent simulées via des structures de données probabilistes locales.
- Documentez clairement ce qui est persisté, ce qui est calculé par un algorithme local et ce qui est simulé pour éviter de faire croire à l'utilisateur qu'une IA distante (comme OpenAI) est connectée alors qu'elle ne l'est pas.

### 4. Ne pas mélanger la persistance DB et le refactoring IA
- Si vous devez modifier les modèles SQLAlchemy (`Subject`, `Concept`, `Card`, `StudySession`), isolez cette tâche.
- Ne tentez pas d'implémenter de nouvelles logiques d'apprentissage ou des modèles NLP avancés dans la même PR ou le même commit que les modifications de schéma de base de données.

---

## 📝 Qualité du Code
- **Typage dynamique** : Soyez vigilant sur le typage des entrées de l'API (par exemple, normaliser les chaînes `"high"` / `"medium"` reçues en valeurs numériques `float` pour les calculs de seuil).
- **Gestion des transactions** : Toujours utiliser `db.session.rollback()` dans les blocs `except` de vos routes Flask pour éviter de bloquer la base de données SQLite en cas d'erreur.
