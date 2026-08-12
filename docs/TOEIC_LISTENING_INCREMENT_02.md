# TOEIC Listening — incrément 2 : conversations et présentations originales

## Positionnement

Cet incrément ajoute un diagnostic d’écoute original de huit réponses observables, organisé en deux conversations et deux présentations professionnelles. Il s’inspire seulement de familles d’écoute décrites publiquement par ETS ; il ne reproduit aucun enregistrement, script, question, choix, visuel, corrigé ni mécanisme de score ETS. Mentor Evolution ne fournit ni score TOEIC estimé ni niveau certifié.

## Périmètre fonctionnel

Chaque stimulus audio est rattaché à deux questions. L’utilisateur lance une unique écoute, validée par l’API avant de pouvoir répondre. Les choix sont affichés sous les libellés A, B et C ; leur texte, les scripts, les noms de locuteurs, la correction et les explications restent absents du navigateur avant soumission.

| Stimulus | Type | Questions | Cibles descriptives | Scénario |
|---|---|---:|---|---|
| `conversation-01` | Conversation | 2 | détail, inférence | Livraison et installation |
| `conversation-02` | Conversation | 2 | détail, inférence | Briefing client hybride |
| `talk-01` | Présentation | 2 | détail, idée principale | Consigne de sécurité du bâtiment |
| `talk-02` | Présentation | 2 | détail, inférence | Mise à jour de la procédure de retours |

## Provenance et intégrité

Les quatre scripts sont versionnés dans `src/content/toeic_listening_conversations_talks.py`. Les quatre WAV sont décrits dans `src/content/listening_conversations_talks_assets.json`, avec leur identifiant de stimulus, version de script, hachage SHA-256, durée mesurée, format et origine vocale synthétique générique. Les fichiers sont tous des WAV PCM mono 16 bits à 24 kHz. Aucun actif n’imite ni ne clone une personne identifiable.

## Modèle de lecture contrôlée

La table `diagnostic_stimulus_playback` est la source de vérité pour l’événement de lecture. Elle impose une contrainte unique sur `(attempt_id, stimulus_id)`. Le client demande ensuite la soumission des réponses sans envoyer de compteur, d’identifiant audio, de version de script, de transcript, de choix ou de correction. Le serveur vérifie qu’un événement de lecture unique existe pour chaque stimulus puis copie les métadonnées d’audit dans les réponses créées.

La migration `c5e8f1a2b4d6` ajoute `content_version` aux tentatives, `stimulus_id`, `script_version` et `audio_duration_seconds` aux réponses, ainsi que la table de lecture. Elle est additive et réversible ; elle doit être testée localement puis confirmée avant l’application sur Neon Production.

## Confidentialité pédagogique et accessibilité

Les routes de catalogue et de démarrage reposent sur des listes blanches de propriétés non sensibles. La route de revue `GET /api/diagnostic/attempts/<id>/listening-review` exige un JWT, la propriété de la tentative et l’état `completed`. Elle est la seule route qui retourne les scripts attribués aux locuteurs, les choix textuels, les corrections et les explications. Toutes les réponses sensibles utilisent `Cache-Control: no-store`.

L’interface permet une commande Lecture et Arrêter accessibles au clavier, annonce l’état du lecteur avec une région `aria-live` et n’autorise les choix qu’après validation serveur de la lecture. Après soumission, la revue affiche un lecteur standard, le transcript attribué aux locuteurs et les corrections, pour rendre le média utilisable sans compromettre la première réponse.

## FSRS

Les cartes FSRS restent facultatives. Elles sont générées uniquement pour les formulations atomiques marquées dans le contenu, par exemple réserver une salle au nom d’une personne ou annoncer une disponibilité future. Une erreur sur une conversation entière, sur l’idée principale ou sur une inférence ne produit jamais automatiquement une flashcard.

## Validations intégrées

La suite comprend les contrôles de catalogue public, la non-exposition des champs privés, la revue refusée avant soumission, le refus de toute lecture déclarée par le client, la lecture unique côté serveur, la persistance des métadonnées, la revue post-soumission, les remédiations dédupliquées et la vérification du manifeste audio. La migration est également contrôlée en montée, descente et nouvelle montée sur une base SQLite isolée.
