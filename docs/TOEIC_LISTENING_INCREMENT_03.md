# Troisième incrément Listening — stimuli professionnels approfondis

## Périmètre

Ce troisième incrément ajoute le diagnostic original `toeic-listening-multi-speaker-v1`. Il comprend deux conversations et deux présentations professionnelles, avec trois questions par extrait, soit douze réponses au total. Les cibles sont le détail explicitement énoncé, le sujet principal et l’inférence prudente.

Ce contenu est une pratique formative originale. Il ne reproduit aucun audio, script, item, choix, correction ou conversion de score ETS ; il ne fournit ni score TOEIC estimé ni niveau certifié.

## Provenance des actifs

Les scripts privés sont versionnés dans `src/content/toeic_listening_multi_speaker.py`. Les quatre WAV privés sont conservés dans `src/content/listening_audio/`, hors de `public/`. Leur manifeste `src/content/listening_multi_speaker_assets.json` enregistre l’identifiant de stimulus, la version de script, la durée mesurée, le format, l’empreinte SHA-256 et l’origine de la voix synthétique générique.

Les fichiers sont du WAV PCM mono 16 bits à 24 kHz. Les deux conversations utilisent deux voix synthétiques génériques distinctes ; les présentations utilisent chacune une voix synthétique générique unique. Aucun fichier ne clone, ne reproduit ou n’imite une personne identifiable.

## Réutilisation du socle partagé

La route `src/routes/diagnostic.py` utilise désormais `SHARED_LISTENING_CATALOGS`. Chaque entrée fournit un chargeur de contenu, d’item, de stimulus et de chemin audio. Les incréments 2 et 3 réutilisent donc les mêmes garanties :

- Le catalogue public ne retourne ni transcript, ni choix textuel, ni correction, ni nom de fichier privé.
- Le démarrage retourne une URL audio liée à une tentative mais l’audio reste inaccessible avant l’autorisation de lecture côté serveur.
- `diagnostic_stimulus_playback` enregistre une seule lecture par paire tentative–stimulus.
- La soumission refuse toute réponse sans lecture associée à son stimulus et ne retourne aucune transcription.
- La revue exige le JWT, la propriété de la tentative et l’état `completed` avant de fournir les scripts attribués aux locuteurs, les corrections et la réécoute guidée.

Cette réutilisation n’ajoute aucun modèle, champ ou index : la migration Neon `c5e8f1a2b4d6` déjà déployée couvre la persistance de `content_version`, des métadonnées de stimulus et du playback.

## Interface

`SharedListeningDiagnostic.jsx` remplace la duplication d’interface entre les incréments. Il reçoit l’endpoint et l’identifiant de module, récupère son catalogue, gère l’unique écoute, affiche le nombre réel de questions par stimulus et présente la revue uniquement après soumission. Les adaptateurs `ToeicListeningConversationsTalks.jsx` et `ToeicListeningMultiSpeaker.jsx` conservent les intégrations claires dans le tableau de bord.

Le lecteur reste accessible au clavier. Son état est annoncé par une région `aria-live`, une commande Arrêter est disponible pendant la lecture et les choix sont désactivés jusqu’à l’autorisation de lecture. Les transcriptions post-soumission identifient les locuteurs, afin d’offrir une alternative textuelle utile à la revue.

## Remédiations FSRS

Seules deux erreurs peuvent proposer une carte : déclencher une inspection après l’arrivée de palettes et conditionner une réservation à une confirmation. Ces formulations sont atomiques, réutilisables et explicitement marquées dans le contenu. Une erreur de compréhension globale, de thème ou d’inférence ne crée jamais automatiquement une flashcard.

## Validations

La couverture d’intégration vérifie les quatre stimuli, les douze réponses, trois réponses par stimulus, le masquage des données sensibles, le refus de soumission sans playback, l’audio privé après autorisation, la revue différée et les deux remédiations FSRS. Le test de manifeste vérifie les empreintes, durées, formats, disponibilité, distribution des réponses A/B/C et l’absence d’actifs `lms-*` dans les fichiers publics.
