# Vérification locale — diagnostic lecture TOEIC

## État du contrôle visuel

L’aperçu Vite local, relié à l’API Flask sur une base SQLite isolée, affiche correctement l’onglet **Diagnostiquer** aux côtés des parcours, de la révision FSRS, de l’adaptation et des données.

Un compte de contrôle non personnel a été créé sur l’aperçu local. Le flux Parcours expose le modèle **Préparation TOEIC** avec le domaine Langues, ses modalités de pratique et le bouton de création. La suite du contrôle doit créer ce parcours, ouvrir l’onglet Diagnostiquer, démarrer le diagnostic et vérifier un résultat descriptif sans estimation de score.

Le parcours TOEIC de contrôle a été créé avec succès. L’onglet **Diagnostiquer** sélectionne ce parcours de langue, affiche le périmètre de 19 items et rappelle explicitement l’absence d’estimation de score.

Le démarrage ouvre correctement le premier item (« Item 1 sur 19 »), affiche sa cible (« Grammaire en contexte »), les choix, la confiance facultative et la règle descriptive sur le temps. La correction n’est pas visible avant soumission. Une réponse peut être sélectionnée visuellement.

Après sélection d’une réponse sur le premier item, le bouton de navigation s’active et l’interface passe correctement à l’item 2 sur 19. La correction du premier item reste masquée ; l’interface conserve donc le caractère diagnostique sans rétroaction prématurée.

## Validations automatisées finales

La suite `pytest tests/test_backend_flask.py tests/test_fsrs_scheduler.py -q` a réussi avec **19 tests**. Le scénario couvre la confidentialité des corrections, les 19 réponses soumises une fois, l’analyse descriptive par cible et la création dédupliquée de cinq cartes grammaticales dans le domaine Langues.

La migration Alembic `f8c4a2d9e7b3` a été validée sur une base SQLite isolée en mode production : montée complète jusqu’à la tête, retour à `e4a9b2c7d6f1`, puis nouvelle montée jusqu’à la tête. Le lint React et le build Vite sont également réussis. Le build signale seulement une base Browserslist/caniuse-lite obsolète, sans échec de compilation.
