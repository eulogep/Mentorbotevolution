# Audit et livraison — Mentor Evolution

**Auteur : Manus AI**  
**Date : 11 août 2026**  
**Branche : `refactor/evidence-learning-loop`**

## Synthèse exécutive

Le dépôt disposait d’un socle **React 18 / Vite / Flask / SQLAlchemy** fonctionnel, mais l’expérience essentielle était encore principalement démonstrative. L’audit a mis en évidence une dissociation entre les promesses de l’interface et les données réellement calculées : scores TOEIC, recommandations, prédictions et plusieurs modules étaient figés ; la validation pouvait s’exécuter sur un concept factice ; et la planification de révision du pipeline appliquait des intervalles identiques à tous les concepts.

La livraison transforme le noyau du produit en une boucle d’apprentissage exploitable : **rappel actif → correction → évaluation explicite → calendrier FSRS → journal de revue → analytics descriptifs**. Les modules qui n’étaient pas reliés à des données ne sont plus mis en avant comme des fonctions opérationnelles. L’interface emploie désormais le positionnement « apprentissage TOEIC fondé sur les preuves », évite les promesses de diagnostic cérébral et écarte les « styles d’apprentissage » comme mécanisme de personnalisation.

> **Statut.** Le backend, la migration de schéma, le lint et le build de production ont été validés. La refonte est prête à être revue puis déployée après application de la migration sur l’environnement de production.

## Constats de l’audit initial

| Domaine | Constat vérifié | Risque ou impact | Réponse apportée |
|---|---|---|---|
| Interface | `App.jsx` mélangeait un tableau de bord fonctionnel avec des métriques et prédictions figées. | Un utilisateur pouvait confondre démonstration et mesure personnelle. | Nouvelle coque centrée sur les données réelles, les sessions de révision et les sources scientifiques. |
| Révision espacée | Le backend utilisait SM-2 ; le pipeline utilisait en parallèle le calendrier fixe `[1, 3, 7, 14, 30]`. | La planification ne dépendait pas systématiquement des réponses observées. | Adaptateur FSRS, état versionné sur chaque carte et notes `again / hard / good / easy`. |
| Traçabilité | Seuls des compteurs cumulés étaient stockés pour les cartes. | Impossible d’expliquer finement une échéance ou de préparer une optimisation individuelle. | Nouvelle table `ReviewLog` qui conserve l’évaluation, le temps de réponse, l’état antérieur, l’état suivant et le journal FSRS. |
| Validation | Le module Feynman recevait par défaut `concept_ui`. | Une validation pouvait être associée à une notion inexistante. | Le tableau de bord impose la sélection d’une notion persistée avant d’ouvrir la validation. |
| Analytics | Le frontend attendait des champs absents de l’API, notamment une « rétention » et une « régularité » non calculées. | Risque de chiffres incohérents ou d’écran dégradé. | Analytics réécrits autour des journaux réels : révisions, réponses retrouvées, temps de réponse, répartition des évaluations et cartes fragiles. |
| Qualité | La suite de tests était opérationnelle, mais `pytest` n’était pas installé dans l’environnement initial et les migrations devaient être vérifiées. | Validation incomplète sur une machine neuve. | Dépendances préparées pour le contrôle, nouveaux tests FSRS et validation d’upgrade/downgrade Alembic isolée. |

## Évolutions livrées

### Planification FSRS et persistance

Le paquet **Py-FSRS 6.3.2**, sous licence MIT et compatible Python 3.10+, est déclaré dans `requirements.txt` et `requirements-vercel.txt`. Il remplace le calcul SM-2 actif de l’endpoint de révision, tout en préservant les champs historiques afin de permettre une migration progressive des cartes existantes. Le paquet modélise la récupérabilité, la stabilité et la difficulté de chaque carte ; l’utilisateur peut ultérieurement régler une rétention cible explicite plutôt que des paramètres techniques opaques. [1] [2]

| Élément | Implémentation | Bénéfice utilisateur |
|---|---|---|
| `User.desired_retention` | Cible bornée entre 0,80 et 0,97, par défaut 0,90. | Le compromis entre charge de révision et rappel visé devient explicite. |
| `Card.scheduler_*` | Type, version et état JSON FSRS par carte. | Le système peut migrer les cartes à leur prochaine revue sans réécrire l’historique. |
| `ReviewLog` | Évaluation, temps de réponse, récupérabilité antérieure, intervalle, état antérieur/suivant, journal FSRS. | Les décisions sont auditables et ouvrent la voie à une optimisation ultérieure, avec garde-fous. |
| `POST /review-card` | Accepte la nouvelle note textuelle et convertit encore `quality_response` 0–5 pour les clients existants. | Compatibilité conservée, interaction plus compréhensible. |
| `GET/PUT /settings` | Expose et valide la rétention cible. | La personnalisation est expliquée au lieu d’être cachée. |

### Session de rappel actif

L’écran de révision ne montre plus une simple échelle numérique. L’apprenant formule d’abord une réponse, révèle ensuite la correction, puis choisit entre **À revoir**, **Difficile**, **Bien** ou **Facile**. L’interface affiche l’action suivante, la rétention cible et la stabilité estimée. La réponse libre reste locale à l’écran : la base ne stocke que l’évaluation, le temps de réponse et les états de planification nécessaires.

Cette conception s’appuie sur la récupération espacée, dont la méta-analyse de Latimier, Peyre et Ramus met en évidence un avantage marqué face à la récupération massée (*g* = 0,74), sans établir un avantage général des intervalles forcément croissants. [3] Pour le TOEIC, la revue de Kim et Webb confirme l’intérêt de l’espacement dans l’apprentissage d’une langue seconde et rappelle que la pratique, le feedback, le délai de rétention et le type de cible modèrent les résultats. [4]

### Interface et communication scientifique

Le nouveau tableau de bord affiche uniquement des informations issues des API : matières, cartes dues, notions persistées et historique de revue. Les liens vers les sources sont visibles dans l’interface. Le discours évite les neuromythes : aucune personnalisation par « style visuel, auditif ou kinesthésique » n’est proposée, conformément à la méta-analyse concluant que les bénéfices d’un appariement aux styles sont trop faibles et trop rares pour justifier une adoption généralisée. [5]

L’auto-explication est conservée comme activité structurée, mais elle n’est plus présentée comme une preuve automatique de maîtrise. La méta-analyse de Bisra et al. décrit l’auto-explication comme la génération d’inférences sur les liens conceptuels et conclut que des prompts peuvent constituer une intervention puissante ; elle ne justifie pas de transformer une simple case cochée en score certain. [6]

## Validation effectuée

| Contrôle | Résultat | Observation |
|---|---|---|
| Compilation Python | Réussite | `python3 -m compileall -q main.py src api backend tests` |
| Tests backend | **23 réussis** | Couverture ajoutée pour les notes FSRS, la sérialisation et la création du journal de revue. |
| Lint frontend | Réussite sans avertissement | `npm run lint` |
| Build frontend | Réussite | `npm run build` ; bundle principal ≈ 401 kB non compressé. |
| Migration Alembic | Réussite | Upgrade isolé jusqu’à `b4f6a8d1e2c3`. |
| Réversibilité migration | Réussite | Downgrade à la migration initiale, puis upgrade à nouveau dans une base SQLite temporaire. |
| Parcours navigateur | Réussite | Inscription locale de test, vue sans données, création d’une carte, rappel avant correction, note `Bien`, feedback FSRS et analytics cohérents. |

Les tests existants produisent encore **43 avertissements**, principalement liés aux usages hérités de `datetime.utcnow()`. Ils ne bloquent pas la livraison, mais doivent être traités dans une passe dédiée de modernisation temporelle.

## Sécurité et dette technique résiduelle

L’audit des dépendances de production signale **deux dépendances affectées** (`react-router` et `react-router-dom`) et **trois avis GHSA modérés**, sans niveau élevé ni critique. Deux avis concernent des redirections ouvertes dans React Router ; le troisième concerne l’hydratation SSR. Le projet est une SPA Vite et n’emploie pas le chemin SSR identifié, mais les deux dépendances restent à mettre à niveau dans une itération isolée après vérification de la compatibilité React Router v7. [7] [8] [9]

| Sujet à traiter ensuite | Décision recommandée | Motif |
|---|---|---|
| React Router | Créer une PR dédiée vers une version corrigée, avec tests de navigation et de liens. | Corriger les vulnérabilités modérées sans mélanger une mise à niveau majeure à cette refonte métier. |
| Horodatages | Remplacer progressivement `datetime.utcnow()` par des instants UTC conscients du fuseau. | Éliminer les avertissements et renforcer la cohérence entre PostgreSQL et SQLite. |
| Optimisation FSRS | Ne l’activer qu’après un historique substantiel de `ReviewLog`, avec consentement et explication. | Éviter une personnalisation statistique instable ou opaque. |
| Exercices TOEIC | Ajouter, par ordre de valeur, textes à trous, dictée, choix justifié et analyse de distracteurs. | Étendre le rappel actif sans réintroduire de fausses fonctionnalités. |
| IA conversationnelle | N’intégrer un modèle distant qu’avec traçabilité des données, évaluation des réponses et communication explicite sur ses limites. | Ne pas confondre heuristiques locales, contenu généré et tutorat fiable. |

## Déploiement et exploitation

Avant le déploiement, installer les dépendances puis appliquer la migration dans l’environnement visé. Sur une instance qui utilise PostgreSQL, ne pas compter sur la création automatique des tables : utiliser Alembic.

```bash
pip install -r requirements-vercel.txt
flask --app main db upgrade
npm ci
npm run build
```

Les cartes existantes restent lisibles. Leur état FSRS est initialisé lors de leur prochaine revue ; les champs SM-2 historiques sont conservés pendant cette transition. Aucun historique d’évaluation n’est inventé ou déduit a posteriori.

## Limites honnêtes de cette itération

Cette livraison ne contient pas encore un assistant IA distant, de prédiction de score TOEIC, de groupes d’étude, de mentorat humain, d’optimisation individualisée des poids FSRS ou de notifications. Ces éléments étaient soit simulés, soit insuffisamment reliés aux données pour être présentés comme opérationnels. La prochaine étape rationnelle consiste à enrichir les exercices TOEIC et la qualité du contenu, puis à observer des journaux de revue réels avant d’augmenter la sophistication algorithmique.

## Références

[1] [Anki FAQ — *What spaced repetition algorithm does Anki use?*](https://faqs.ankiweb.net/what-spaced-repetition-algorithm)  
[2] [Py-FSRS 6.3.2 — package Python, licence MIT](https://pypi.org/project/fsrs/)  
[3] [Latimier, Peyre & Ramus (2021) — *A Meta-Analytic Review of the Benefit of Spacing out Retrieval Practice Episodes on Retention*](https://link.springer.com/article/10.1007/s10648-020-09572-8)  
[4] [Kim & Webb (2022) — *The Effects of Spaced Practice on Second Language Learning: A Meta-Analysis*](https://onlinelibrary.wiley.com/doi/abs/10.1111/lang.12479)  
[5] [Clinton-Lisell & Litzinger (2024) — méta-analyse de l’hypothèse des styles d’apprentissage](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2024.1428732/full)  
[6] [Bisra et al. (2018) — *Inducing Self-Explanation: a Meta-Analysis*](https://link.springer.com/article/10.1007/s10648-018-9434-x)  
[7] [GHSA-wrjc-x8rr-h8h6 — React Router open redirect](https://github.com/advisories/GHSA-wrjc-x8rr-h8h6)  
[8] [GHSA-337j-9hxr-rhxg — React Router SSR hydration](https://github.com/advisories/GHSA-337j-9hxr-rhxg)  
[9] [GHSA-jjmj-jmhj-qwj2 — React Router open redirect leading to XSS](https://github.com/advisories/GHSA-jjmj-jmhj-qwj2)
