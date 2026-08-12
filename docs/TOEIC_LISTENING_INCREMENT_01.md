# Listening 01 — Questions et réponses originales

## Finalité

Cet incrément ajoute un diagnostic formatif d’écoute de quatre exercices **Question–réponse** en anglais professionnel. Il s’agit de contenu éditorial original : il ne reproduit aucun enregistrement, script, item, corrigé ou visuel ETS. Mentor Evolution ne présente pas cette activité comme un test TOEIC officiel et ne calcule aucun score ni niveau certifié.

Le diagnostic s’attache à décrire les réponses observées. Les remédiations FSRS sont limitées à des formulations atomiques et réutilisables ; une conversation ou un item complet ne devient jamais une carte de répétition espacée.

## Parcours utilisateur

L’apprenant rattache l’activité à un parcours du domaine `language`. Pour chaque item, l’interface autorise une seule écoute puis expose seulement les choix neutres **A**, **B** et **C**. La transcription, les réponses textuelles, la correction et l’explication restent côté serveur avant la soumission. Après soumission, la revue affiche la transcription et la justification afin de permettre une réécoute guidée et une alternative textuelle.

| Contrôle | Garantie mise en œuvre |
|---|---|
| Originalité | Scripts et corrections versionnés dans `src/content/toeic_listening_question_response.py`. |
| Confidentialité pédagogique | Les routes publiques retirent `choices`, `transcript`, `correct_index`, `explanation` et `remediation`. |
| Écoute | La soumission refuse toute réponse dont `play_count` est inférieur à 1 ou dépasse la limite de l’item. |
| Accessibilité | Contrôle audio libellé, focus visible, statut `aria-live` et transcript après soumission. |
| FSRS | Les erreurs de formulation atomique peuvent créer des cartes du domaine `language` de façon dédupliquée. |

## Provenance audio

Le manifeste `src/content/listening_assets.json` relie chaque actif à un identifiant de script, une version, un hachage SHA-256, une durée, une origine vocale et un état de revue. L’interface n’autorise le démarrage du diagnostic que si les quatre états `audio_status` fournis par l’API sont `available`. Le test `tests/test_listening_assets.py` vérifie séparément la présence des fichiers statiques, leur hachage et leur durée réelle.

Les quatre extraits sont désormais disponibles et leur intégrité technique est vérifiée. `lqr-01` utilise une voix synthétique générique générée par le service de synthèse du projet. Après indisponibilité de ce service pour les trois autres extraits, `lqr-02` à `lqr-04` ont été générés à partir des scripts originaux par une voix synthétique générique locale eSpeak NG ; cette différence d’origine est explicitement consignée dans le manifeste. Aucun actif n’imite ni ne clone une personne identifiable.

## Références

[1] [W3C WAI — Making Audio and Video Media Accessible](https://www.w3.org/WAI/media/av/)

[2] [W3C WAI — Media Players](https://www.w3.org/WAI/media/av/player/)

[3] [W3C WCAG 2.2 — Understanding SC 1.2.1](https://www.w3.org/WAI/WCAG22/Understanding/audio-only-and-video-only-prerecorded)

[4] [ETS — TOEIC Listening and Reading](https://www.ets.org/toeic/about/listening-reading.html)

[5] [ETS — Permissions](https://www.ets.org/legal/permissions.html)
