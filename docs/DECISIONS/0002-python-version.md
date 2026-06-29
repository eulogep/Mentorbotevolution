# ADR 0002 : Utiliser Python 3.12 sur Vercel

## Statut
Accepté

## Contexte
Vercel supporte les environnements de serverless Python 3.9, 3.10, 3.11, et 3.12. Pour tirer parti des optimisations de performances de la machine virtuelle Python et assurer un support à long terme, nous devons cibler une version moderne.

## Décision
Nous ciblons l'utilisation de Python 3.12 (ou 3.11 si contrainte technique de la plateforme) pour le déploiement sur Vercel. 

## Conséquences
- La version de Python est configurée via `env.PYTHON_VERSION` dans `vercel.json`.
- Aucune syntaxe ou dépendance incompatible avec Python 3.11/3.12 ne doit être introduite.
- Toutes les dépendances listées dans `requirements.txt` et `requirements-vercel.txt` doivent être compatibles et testées avec la version ciblée.
