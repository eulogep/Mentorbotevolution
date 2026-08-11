# Diagnostic lecture — anglais professionnel

## Statut et objectif

Cette fonctionnalité introduit un diagnostic formatif original de **19 items de lecture**. Il sert à décrire les réponses observées sur la grammaire, le vocabulaire professionnel, la cohésion, le repérage d’information et l’inférence simple. Il ne s’agit ni d’un examen officiel, ni d’une simulation certifiée, ni d’un estimateur de score.

Le format couvre des familles de tâches cohérentes avec la compréhension écrite professionnelle décrite par ETS, sans reprendre de questions, textes ou corrections d’ETS. [1]

> **TOEIC® est une marque déposée d’ETS. Ce produit n’est ni approuvé ni endossé par ETS.**

## Contenu et structure

| Cible | Nombre d’items | Type de tâche | Remédiation FSRS possible |
|---|---:|---|---|
| Grammaire en contexte | 5 | Phrase à compléter | Oui, si erreur ; contraste ou formulation atomique |
| Vocabulaire professionnel | 4 | Phrase à compléter | Oui, si erreur ; mot ou collocation réutilisable |
| Cohésion du texte | 4 | Texte à compléter | Non automatique ; pratique guidée de textes analogues |
| Repérage d’information | 4 | Compréhension de document | Non automatique ; lecture et justification d’indices |
| Inférence simple | 2 | Compréhension de document | Non automatique ; échantillon insuffisant pour cibler une lacune |

Les scénarios sont entièrement originaux : réunions, courriels, logistique, maintenance, relation client, avis de bureau, comptes rendus, offres d’emploi et politiques de retour. Les réponses correctes, explications et métadonnées de remédiation ne sont jamais renvoyées au client avant la soumission de la tentative.

## Contrat API

| Route | Rôle |
|---|---|
| `GET /api/diagnostic/toeic-reading` | Retourne les métadonnées et items publics, sans correction |
| `POST /api/diagnostic/toeic-reading/start` | Crée une tentative rattachée à un parcours Langues explicite |
| `POST /api/diagnostic/attempts/<id>/submit` | Vérifie la réponse de chaque item une fois, persiste les résultats et retourne une analyse descriptive |
| `POST /api/diagnostic/attempts/<id>/create-remediation` | Crée, sur demande, des cartes FSRS dédupliquées pour les erreurs grammaticales ou lexicales réutilisables |

La soumission enregistre l’exactitude, le temps de réponse et la confiance déclarée. Les résultats sont regroupés par cible. Une recommandation de création de cartes n’est proposée qu’à partir de **deux erreurs** dans une cible avec **au moins quatre items** et une remédiation atomique disponible. Une erreur isolée ne devient donc pas artificiellement une « lacune ».

## Articulation avec FSRS

FSRS conserve son rôle de planification de récupération pour les cartes atomiques seulement. Les cartes créées appartiennent au domaine `language`, reçoivent les étiquettes `toeic`, `diagnostic`, `reading` et la cible correspondante, puis sont disponibles immédiatement pour une première récupération. Les activités de compréhension de document restent séparées des cartes : elles exigent pratique, justification et nouveaux contextes.

Les notes de revue restent choisies explicitement par l’utilisateur après récupération, conformément à la logique FSRS existante. Le diagnostic ne convertit pas mécaniquement une note de QCM en évaluation de mémoire.

## Données et migrations

La migration `f8c4a2d9e7b3` ajoute les tables `diagnostic_attempt` et `diagnostic_response`. Elles sont liées à l’utilisateur, peuvent être rattachées à un parcours, conservent l’horodatage, l’état de tentative, les réponses et les cibles observées. La migration est réversible.

## Limites assumées

Le lot de 19 items est un point de départ. Il ne suffit pas à décrire de manière stable toutes les compétences de compréhension écrite, en particulier l’inférence. Les résultats ne doivent pas être interprétés comme un niveau certifié ou un score TOEIC prédit. L’évaluation formative sert à orienter la pratique suivante et le feedback, ce qui est distinct d’une évaluation certificative. [2]

Le prochain incrément pourra ajouter des textes nouveaux et des items parallèles avant d’augmenter toute sophistication adaptative. Le module d’écoute doit faire l’objet d’une branche distincte après constitution de scripts originaux et d’audios dont l’origine et la licence sont traçables.

## Références

[1]: https://www.ets.org/toeic/about/listening-reading.html "About the TOEIC Listening and Reading Test — ETS"
[2]: https://www.edresearch.edu.au/summaries-explainers/explainers/formative-assessment "Formative assessment — Australian Education Research Organisation"
