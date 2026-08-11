# Notes de recherche — 11 août 2026

## Résultats confirmés

| Axe | Résultat exploitable | Implication produit | Source |
|---|---|---|---|
| Récupération espacée | La méta-analyse de Latimier, Peyre et Ramus indique un fort avantage de la récupération espacée face à la récupération massée (*g* = 0,74). Elle ne confirme pas un avantage général des intervalles nécessairement croissants par rapport à un espacement uniforme (*g* = 0,034, non significatif). | Remplacer les séquences fixes rigides par un ordonnancement fondé sur les rappels réussis/échoués, le délai écoulé et la date d’échéance, sans présenter la croissance d’intervalles comme une loi scientifique. | [Latimier et al., 2021](https://link.springer.com/article/10.1007/s10648-020-09572-8) |

## Points de vigilance

- L’accès automatisé à la page PubMed de Dunlosky et al. a rencontré une page de vérification ; la source n’est pas encore exploitée dans les décisions.
- Ces notes de travail seront transformées en document final cité après recoupement avec d’autres sources académiques et références open source.


## Références open source — planification adaptative

| Référence | Élément vérifié | Décision d’architecture envisagée |
|---|---|---|
| [FSRS4Anki — The Algorithm](https://github.com/open-spaced-repetition/fsrs4anki/wiki/The-Algorithm) | La documentation de référence renvoie aux travaux « A Stochastic Shortest Path Algorithm for Optimizing Spaced Repetition Scheduling » et « Optimizing Spaced Repetition Schedule by Capturing the Dynamics of Memory », ainsi qu’à des jeux de données ouverts de journaux de révision. | Ne pas réimplémenter le modèle de recherche dans la première itération. Concevoir une couche de planification remplaçable, des journaux de revue complets et des paramètres explicitement versionnés afin de permettre une migration ultérieure vers une implémentation FSRS validée. |
| [Awesome FSRS Wiki](https://github.com/open-spaced-repetition/awesome-fsrs/wiki/) | Le projet rassemble une documentation dédiée aux mécanismes, à l’optimisation, aux métriques et aux benchmarks. | Utiliser FSRS comme référence de conception, pas comme promesse marketing ; toute intégration devra passer par une bibliothèque compatible et une revue de licence. |

## Conception pédagogique — sources académiques

| Axe | Résultat exploitable | Implication produit | Source |
|---|---|---|---|
| Auto-explication guidée | Bisra et al. définissent l’auto-explication comme la production d’inférences sur des relations causales ou conceptuelles. Leur méta-analyse conclut que les sollicitations d’auto-explication peuvent être une intervention puissante dans diverses conditions d’enseignement et suggère d’explorer la génération informatique de prompts. | Le flux « Feynman » doit demander une explication ciblée, puis confronter l’apprenant à une question de transfert et à un exemple corrigé, au lieu de transformer des cases cochées et une confiance déclarée en score de maîtrise. | [Bisra et al., 2018](https://link.springer.com/article/10.1007/s10648-018-9434-x) |
| Langue seconde / TOEIC | Kim et Webb ont synthétisé 98 tailles d’effet issues de 48 expériences (*N* = 3 411). Ils trouvent un effet moyen à fort de l’espacement pour l’apprentissage d’une L2 ; un intervalle plus long est plus favorable aux tests différés, tandis que des intervalles égaux et croissants sont statistiquement équivalents. Les effets dépendent notamment du type de cible, du nombre de sessions, de la pratique, du feedback et du délai de rétention. | Définir la planification selon un objectif de rétention et des réponses observées, conserver un feedback correctif immédiat pour les items échoués et évaluer séparément vocabulaire, grammaire, compréhension orale et lecture. | [Kim & Webb, 2022](https://onlinelibrary.wiley.com/doi/abs/10.1111/lang.12479) |

## Références produit — pratiques réutilisables sans copie de code

| Référence | Élément vérifié | Transposition prudente dans Mentor Evolution |
|---|---|---|
| [FAQ Anki — algorithmes de répétition](https://faqs.ankiweb.net/what-spaced-repetition-algorithm) | FSRS modélise pour chaque carte la récupérabilité, la stabilité et la difficulté ; il ajuste ses paramètres à partir de l’historique des révisions. L’apprenant règle une rétention cible, qui exprime un compromis explicite entre le volume de révisions et le souvenir visé. | Ajouter un suivi de résultat par révision, afficher la charge quotidienne et rendre le compromis « temps / rétention cible » compréhensible. La première version restera déterministe et transparente ; une personnalisation statistique ne viendra qu’après collecte suffisante et consentie. |
| [H5P — types de contenus](https://h5p.org/content-types-and-applications) | H5P propose notamment des cartes, dictées avec feedback immédiat, textes à trous, questions, scénarios ramifiés, supports interactifs et enregistrements audio. | Prioriser, en code natif, des exercices TOEIC à rappel actif : question à réponse libre, texte à trous, choix justifié, dictée et explication de règle. Étudier H5P uniquement comme intégration future, après vérification de licence, d’hébergement et de maintenance. |

## Garde-fou scientifique

| Risque | Conclusion vérifiée | Règle de produit |
|---|---|---|
| « Styles d’apprentissage » | La méta-analyse de Clinton-Lisell et Litzinger conclut que les bénéfices de l’appariement entre instruction et styles d’apprentissage sont trop faibles et trop rares pour justifier une adoption généralisée. | Ne jamais diagnostiquer ni prescrire un style « visuel / auditif / kinesthésique ». Personnaliser sur les performances observées, les objectifs, le délai de rétention, les erreurs et la disponibilité, pas sur un profil cognitif revendiqué. |

Source : [Clinton-Lisell & Litzinger, 2024](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2024.1428732/full).

## Faisabilité technique — intégration FSRS

| Vérification | Résultat | Décision |
|---|---|---|
| Paquet | `fsrs` 6.3.2 (Py-FSRS), Python ≥ 3.10, licence MIT. | Compatible avec les runtimes Python 3.11/3.12 du projet et sans conflit de licence identifié. |
| Contrat principal | Une `Card` est mise à jour via `Scheduler.review_card(card, rating)` ; `Rating` distingue *Again*, *Hard*, *Good* et *Easy*. Les objets `Card` et `ReviewLog` sont sérialisables en JSON. | Stocker l’état FSRS par carte sous forme de JSON et journaliser les résultats de révision. Conserver les champs SM-2 existants le temps de la migration pour une compatibilité graduelle. |
| Personnalisation | La documentation conseille de ne pas modifier manuellement les poids par défaut. La rétention cible est le paramètre utilisateur pertinent ; l’optimisation requiert un historique de journaux. | Proposer une rétention cible explicite (par défaut 90 %) et ne pas prétendre à une personnalisation ML avant un volume d’historique suffisant. |

Source : [Py-FSRS 6.3.2 sur PyPI](https://pypi.org/project/fsrs/).

