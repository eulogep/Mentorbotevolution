# Audit de généralisation multi-domaines — Mentor Evolution

**Date : 11 août 2026**  
**Périmètre : préparation TOEIC conservée comme parcours initial ; évolution vers l’informatique, Excel, réseau, cybersécurité, Power BI et d’autres matières.**

## Conclusion

Le noyau de données est déjà **partiellement générique** : `Subject`, `Concept`, `Card`, `ReviewLog` et la planification FSRS ne dépendent pas d’une matière particulière. En revanche, le produit conserve plusieurs hypothèses TOEIC ou pseudo-personnalisées dans les parcours de création, les données de démonstration et les plans générés. La généralisation ne requiert donc pas une réécriture complète ; elle exige une couche explicite de **domaine, objectif et type de pratique**, ainsi que l’élimination des scénarios générés artificiellement.

| Élément | État constaté | Décision de généralisation |
|---|---|---|
| `Subject` | Nom et description génériques ; `target_score` et `current_score` supposent un examen chiffré. | Ajouter un type de domaine et un objectif configurable ; conserver les scores uniquement pour les parcours certifiants qui les définissent réellement. |
| `Concept` | Entité déjà générique, avec statut et maîtrise. | Préserver ; enrichir par type de compétence, prérequis et critères de preuve. |
| `Card` / `ReviewLog` / FSRS | Agnostiques au contenu. | Préserver comme moteur de mémorisation commun à tous les domaines. |
| Création automatique de matière | `GET /mastery/get-subjects` crée un faux parcours TOEIC avec scores et concepts. | Ne jamais créer de contenu fictif ; présenter un état vide et proposer un assistant de création de parcours. |
| Générateur de plan | Suppose une note sur 20, un score TOEIC, un style d’apprentissage, un chronotype et une probabilité de succès. | Remplacer par un objectif de compétence, une échéance, une disponibilité et des jalons observables. |
| Fallback d’analyse | Génère aléatoirement des concepts TOEIC lorsqu’un fichier ne peut être lu. | Remplacer par une erreur utile ou une saisie guidée des notions, jamais par du contenu fictif. |
| Exercices | Flashcards heuristiques génériques ; activité de validation et cartes FSRS réutilisables. | Introduire des « types de pratique » choisis par domaine : rappel, explication, exécution, diagnostic, production et simulation. |

## Implications produit

Le TOEIC reste un **parcours** avec ses propres formes de pratique — vocabulaire, grammaire, compréhension orale, lecture chronométrée — et non le modèle de données de toute l’application. L’informatique peut devenir le premier parcours non linguistique avec, par exemple, des bases de programmation, systèmes, réseau ou données. Excel, Power BI et la cybersécurité utiliseront le même moteur de progression mais privilégieront des preuves pratiques : fichier produit, requête exécutée, diagnostic argumenté, procédure documentée ou laboratoire sécurisé.

La planification de révision FSRS est adaptée aux connaissances déclaratives et procédurales que l’on veut retrouver à long terme. Elle ne suffit pas à attester une compétence appliquée. Chaque parcours devra donc combiner la mémoire avec des tâches de transfert et des critères de réussite spécifiques, sans convertir arbitrairement une activité en « score de maîtrise ».

## Priorité d’implémentation

La première évolution doit créer un sélecteur de domaine et une structure de parcours générique, supprimer les fallbacks TOEIC fictifs, et remplacer les réglages « style d’apprentissage », « chronotype » et « probabilité de succès » par des paramètres observables. Le premier contenu de référence recommandé est **Fondamentaux de l’informatique**, car il permet de tester des connaissances, des explications et des mini-tâches pratiques sans rendre le produit dépendant d’un outil propriétaire.
