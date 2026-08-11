# Module d’apprentissage adaptatif — TOEIC et informatique

**Auteur : Manus AI**  
**Date : 11 août 2026**

## Finalité

Le module étend le planificateur FSRS déjà intégré à Mentor Evolution. Il ne remplace pas la compréhension, les projets ou les exercices pratiques par des cartes. Il permet de **réactiver au bon moment les éléments à mémoriser** : vocabulaire et collocations TOEIC, règles grammaticales, commandes, protocoles, définitions, concepts et heuristiques informatiques.

> La planification est adaptative au niveau de chaque carte : elle exploite l’historique de rappels de cette carte. Elle ne déduit pas un profil cognitif caché, ne déclare pas de compétence professionnelle et n’optimise pas de poids individuels sans historique suffisant.

FSRS associe explicitement la rétention souhaitée à un compromis entre connaissances récupérables et charge de travail. Ses graphiques et simulations dépendent des paramètres et de l’historique de chaque apprenant ; ils ne doivent donc pas être présentés comme une prédiction universelle. [1]

## Décisions de conception

| Élément | Décision | Justification |
|---|---|---|
| Unité de planification | Chaque `Card` dispose d’un état FSRS et d’un journal `ReviewLog` existants. | Les erreurs, délais et rappels d’une notion ne doivent pas influencer arbitrairement une autre notion. |
| Domaine | Chaque carte porte un domaine `language`, `computing`, `productivity`, `data`, `infrastructure`, `security` ou `general`. | Les sessions peuvent distinguer vocabulaire TOEIC et informatique tout en conservant le même moteur. |
| Profil adaptatif | L’utilisateur peut choisir une rétention cible par domaine. En l’absence de profil, son réglage global est conservé. | La rétention cible règle un compromis explicite ; elle n’est pas ajustée silencieusement. [1] |
| Valeurs autorisées | 80 % à 97 %, avec valeur de repli 90 %. | Ces bornes correspondent à celles déjà protégées par le planificateur du produit. |
| Sessions ciblées | Une session peut ne montrer que les cartes d’un domaine effectivement dues. | Le TOEIC et l’informatique deviennent des espaces de pratique distincts, sans doubler les données. |
| Explicabilité | Le tableau expose cartes dues, revues récentes, taux descriptif de rappel, délai estimé et rétention configurée. | Les recommandations reposent sur des données observées, pas sur une promesse de score ou de maîtrise. |

## Parcours utilisateur

| Étape | Vocabulaire TOEIC | Informatique |
|---|---|---|
| Créer | Carte liée au parcours Langues, étiquetée `language`. | Carte liée au parcours Fondamentaux de l’informatique, étiquetée `computing`. |
| Réviser | Répondre avant de voir une définition, un exemple ou une collocation. | Expliquer un concept, une commande ou le rôle d’un protocole avant correction. |
| Évaluer | Choisir À revoir, Difficile, Bien ou Facile. | Même échelle de rappel, sans prétendre évaluer l’exécution d’un projet. |
| Adapter | FSRS calcule la prochaine échéance de la carte et le journal conserve le résultat. | Même mécanisme, avec une session filtrée par domaine et un objectif de rétention choisi. |
| Compléter | Ajouter écoute, lecture et production hors cartes. | Ajouter laboratoire autorisé, diagnostic et artefact pratique hors cartes. |

## Contrats proposés

| Endpoint | Méthode | Rôle |
|---|---|---|
| `/api/spaced-repetition/adaptive-overview` | `GET` | Retourner les domaines effectivement étudiés, les cartes dues, les revues récentes et les indicateurs descriptifs. |
| `/api/spaced-repetition/adaptive-profiles` | `GET` | Retourner la rétention globale, les profils par domaine et leurs limites. |
| `/api/spaced-repetition/adaptive-profiles/<domain>` | `PUT` | Enregistrer un objectif de rétention explicite pour un domaine autorisé. |
| `/api/spaced-repetition/get-due-cards?domain=<domain>` | `GET` | Démarrer une session ciblée avec uniquement les cartes dues du domaine. |

La route de revue emploie le profil du domaine de la carte si un profil explicite existe. Le retour affiche toujours l’objectif effectif réellement appliqué et la date d’échéance calculée.

## Critères d’acceptation

Le module doit permettre de créer et réviser des cartes de vocabulaire TOEIC et de notions informatiques avec le même moteur FSRS, mais dans des sessions séparables par domaine. Un changement d’objectif de rétention doit être validé, persistant et utilisé lors de la revue suivante. Les cartes et journaux antérieurs doivent rester compatibles. Aucune session ne doit afficher de métrique fictive lorsque l’utilisateur ne possède aucune donnée dans le domaine.

## Références

[1] [FSRS4Anki — *The Optimal Retention*](https://github.com/open-spaced-repetition/fsrs4anki/wiki/The-optimal-retention)
