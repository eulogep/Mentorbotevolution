# 🪙 Token & Context Optimization Strategy

Ce document fournit des techniques pour réduire la consommation de tokens lors de vos interactions avec le dépôt, garantissant des réponses rapides et des coûts réduits.

---

## 🔍 Outils de Recherche Ciblés
- **Ripgrep (grep_search)** : Utilisez `grep_search` pour localiser précisément les symboles ou les chaînes de texte au lieu de lire des répertoires entiers.
- **Filtres glob (Includes)** : Filtrez toujours vos recherches par extension de fichier (e.g. `*.py` ou `*.jsx`) pour limiter le nombre de correspondances inutiles.

---

## 📖 Lectures de Fichiers Segmentées
- **Ne lisez pas de fichiers entiers** : Si un fichier dépasse 150 lignes (comme [src/App.jsx](src/App.jsx) qui fait 800+ lignes), lisez uniquement la plage de lignes concernée par votre tâche en fournissant les arguments `StartLine` et `EndLine` à l'outil `view_file`.
- **Limites** : Restreignez vos lectures à 100 lignes maximum à la fois lorsque vous cherchez un bloc de logique spécifique.

---

## ✏️ Éditions Chirurgicales
- **Remplacements locaux** : Utilisez l'outil `replace_file_content` pour modifier des blocs contigus ciblés. Évitez de réécrire ou de remplacer le fichier entier pour de simples modifications de fonctions.
- **Modifications multiples disjointes** : Si vous devez modifier plusieurs sections d'un même fichier, utilisez `multi_replace_file_content` avec des blocs de remplacement (`ReplacementChunks`) extrêmement resserrés (moins de 10 lignes de contexte autour de la modification).

---

## 🗣️ Style de Communication Concis
- **Pas de paraphrase de code** : Ne répétez pas ce que fait le code dans vos réponses textuelles. Si un changement a été effectué, pointez simplement vers le fichier modifié ou vers le [walkthrough](file:///C:/Users/mabia/.gemini/antigravity-ide/brain/ab464901-4355-4059-8e01-1b3f596f9630/walkthrough.md).
- **Direct au but** : Évitez les formules de politesse à rallonge et les explications théoriques inutiles.
