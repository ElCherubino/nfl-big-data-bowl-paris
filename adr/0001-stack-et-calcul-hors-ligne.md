---
status: accepted
date: 2026-10-21
---

# ADR-0001 — Python pour les calculs, React/Vite pour le produit statique

Le dépôt possède déjà une stack Python scientifique et un template React/Vite. Nous conservons Python pour transformer les CSV en résultats publiables, et React/Vite en JavaScript pour les afficher : calculer une fois hors ligne évite de dupliquer les règles dans le navigateur et permet une démo sans base de données, serveur métier ou clé cloud.

## Stack retenue

| Usage | Choix | Situation / action |
| --- | --- | --- |
| Runtime calcul | Python ≥ 3.11, environnement `.venv` | Préparation existante ; validation locale actuelle en Python 3.12 |
| Tables / géométrie / bootstrap | pandas, NumPy | Déjà déclarés ; processing tracking par match, pas toute la saison en mémoire |
| Validation de contrat | JSON Schema Draft 2020-12 + `jsonschema` Python | Schémas à créer ; déclarer la dépendance directement même si elle est déjà transitive |
| Tests métier | pytest | Déjà déclaré ; fixtures communes et tests sur exports |
| Frontend | React 19, JavaScript/JSX, CSS existante, lucide-react | Déclarés par le template ; garder le lockfile, installer avec `npm ci` |
| Build / développement | Vite 7, Node ≥ 22.12 et npm | Conserver les scripts existants ; pas de migration de framework |
| Rejeu | SVG natif + requestAnimationFrame | Remplace le terrain statique ; aucun moteur 3D requis |
| Tests navigateur | Playwright Test, Chromium | Dépendance de développement et navigateur à installer et verrouiller lors du lot C |
| Livraison | Build Vite + fichiers JSON statiques | Hébergement local suffisant pour le POC ; hébergement public à décider séparément |

Les versions majeures React/Vite viennent des déclarations actuelles du dépôt ; leur résolution exacte reste celle du lockfile. Les nouvelles dépendances sont ajoutées par le propriétaire du lot indiqué dans le plan, sans mise à jour générale du reste de la stack.

## Organisation cible

| Zone à créer ou étendre | Responsabilité |
| --- | --- |
| `rb_lifeline/` | Package Python : entrée CLI, chargement, évaluation, agrégats et publication |
| `tests/` | Tests métier Python et cohérence entre exports |
| `contracts/` | Schémas JSON et fixtures partagées, indépendants du build frontend |
| `website/src/data/` | Client unique de lecture et contrôles de contrat |
| `website/src/features/coach/` | Sélection match, jeux, résumés match/saison |
| `website/src/features/broadcaster/` | Classement ligue de saison |
| `website/src/features/replay/` | Projection terrain, horloge, commandes et annotations |
| `website/tests/` | Tests navigateur sur le build et les fixtures |
| `outputs/site/` | Exports générés ; staging puis copie vers les ressources publiques du site |

L’interface publique Python est la génération d’une publication et sa validation. Les fonctions de géométrie et les étapes du pipeline restent internes au package ; les développeurs web consomment uniquement les exports documentés.

## Alternatives et conséquences

Un backend FastAPI et une base ajouteraient une configuration d’exécution et des requêtes sans besoin de données modifiables en ligne. Streamlit accélère une analyse mais dupliquerait ici le produit déjà dessiné : le starter existant reste un outil de préparation, et le lanceur final devra ouvrir React. Une migration TypeScript généralisée est reportée pour garder le travail centré sur le branchement métier ; JSDoc et les fixtures décrivent les formes échangées.

Les dépendances scientifiques déjà présentes mais inutilisées n’imposent pas leur usage. AWS/Bedrock n’intervient pas dans le POC. Des fichiers de match volumineux constituent le coût assumé du statique et seront mesurés lors de la validation, avant toute décision de fragmentation supplémentaire.

## Références techniques

Vite documente le build statique et précise que `preview` sert à la vérification locale, pas à la production : [guide Vite](https://vite.dev/guide/static-deploy.html). Les tests navigateur utiliseront actions et assertions sur le rendu : [Playwright](https://playwright.dev/docs/writing-tests). Les exports seront validés avec le draft explicite : [JSON Schema 2020-12](https://json-schema.org/draft/2020-12), [validation Python](https://python-jsonschema.readthedocs.io/en/stable/validate/).
