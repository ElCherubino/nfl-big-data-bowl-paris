# Plan technique et synchronisation de l’équipe

**État après implémentation (21 octobre 2026) :** voir le [registre par spec](../spec/IMPLEMENTATION_STATUS.md) et les [preuves de validation](../docs/validation.md). Le plan et son registre initial ci-dessous sont conservés comme référence de conception ; ils ne représentent plus l’état courant des livrables.

Objectif : trois personnes peuvent développer en même temps sans inventer des interfaces différentes. Les rôles A/B/C sont à attribuer aux personnes présentes ; chaque rôle conserve un propriétaire responsable de l’intégration de son lot.

## 1. État de départ

| Élément | État constaté |
| --- | --- |
| Environnement Python, préparation et diagnostics | Existant ; vérifications génériques déjà exécutées |
| Template React/Vite, CSS, dépendances et lockfile | Existants ; données et terrain encore illustratifs |
| Sous-module de données et description RB Lifeline | Existants |
| Pipeline, schémas, tests métier, rejeu dynamique, tableaux réels | À implémenter |
| Specs et ADR | Documents de conception ; ne constituent pas une preuve de produit terminé |

## 2. Responsabilités

| Rôle | Lot principal | Zones de fichiers possédées | Livrable à transmettre |
| --- | --- | --- | --- |
| A — Données et calculs | Chargement, évaluateur, statistiques, exports | `rb_lifeline/`, `tests/`, `contracts/`, dépendances Python | Publication validée avec flags, résumés match, saison, qualité |
| B — Site et tableaux | Client de données, navigation Coach/Broadcaster, listes et classements | `website/src/data/`, vues coach/broadcaster, shell, CSS | Parcours réels branchés sur le contrat, états erreur/vide, URL |
| C — Rejeu et intégration | Animation, commandes, traces et tests navigateur | `website/src/features/replay/`, `website/tests/`, configuration des tests | Rejeu dynamique testé puis contrôle du produit intégré |

Correspondance specs : A porte 01–04 et 09 ; C porte 05 ; B porte 06–07 ; 08 est intégrée par C avec A/B. Ces responsabilités techniques ne changent pas les critères fonctionnels des specs.

B est responsable de `website/package.json`, du lockfile, du point d’entrée et de la CSS commune. C lui transmet les ajouts nécessaires pour Playwright dans une modification coordonnée, puis travaille dans ses zones. A porte les schémas ; B/C n’en créent pas de copies concurrentes. Le lanceur et les instructions de livraison sont intégrés par B avec C.

Les branches par lot sont facultatives ; des modifications sur le même fichier sont discutées entre propriétaires avant édition. Les contrats et fixtures partagés arrivent avant le branchement de tous les écrans. Les dépendances lourdes entre tâches sont listées ci-dessous ; un mock local ne vaut pas intégration.

## 3. Modules Python et interface cible

| Module cible | Implémentation attendue | Contrat avec le reste |
| --- | --- | --- |
| `rb_lifeline/data.py` | Lecture tables, contrôle clés/jointures, itération tracking par match | Jeux sources + participants complets + diagnostics |
| `rb_lifeline/metrics.py` | Normalisation, événements, pression, cinq checks à toutes les frames | Résultat d’un jeu : frames, états RB et observations fixes |
| `rb_lifeline/targets.py` | Parsing description et correspondance unique | Cible reconnue/inconnue/ambiguë/non applicable |
| `rb_lifeline/aggregates.py` | Comptes match et saison, bootstrap, shrinkage, strates, sensibilités | Objets décrits dans CONTRACTS, sans logique dans les vues |
| `rb_lifeline/publish.py` | Validation des schémas, conservation, staging et manifeste final | Publication cohérente ou échec explicite |
| `rb_lifeline/__main__.py` | CLI : build et validate | Configuration centralisée et codes de sortie fiables |

Interface externe cible : `python -m rb_lifeline build --data-dir nfl-data/data --output outputs/site` puis `python -m rb_lifeline validate --output outputs/site`. Ces commandes sont **à implémenter**, pas disponibles au moment de rédaction. La configuration de build porte les paramètres du manifeste et la graine ; aucune constante métier concurrente dans React.

La fonction interne `evaluate_play(play, participants, frames, parameters)` retourne le résultat complet sans écrire de fichier ; `aggregate_season(game_results, parameters)` retourne tableaux et analyses ; `publish(publication, output_dir)` vérifie puis écrit. Adapter ces noms exige de mettre à jour leurs consommateurs Python, pas les modules web qui restent couplés au JSON seulement.

## 4. Modules web et raccordement

| Module cible | Propriétaire | Interface |
| --- | --- | --- |
| `data/siteData.js` | B | loadCatalog / loadSeason / loadGame, erreurs CONTRACTS |
| `features/coach/CoachDashboard.jsx` | B | Sélection jeu et back depuis le bundle du match |
| `features/coach/GameRbTable.jsx` | B | Lignes rbSummary ; émet un nflId pour filtrer les jeux |
| `features/coach/SeasonTables.jsx` | B | Tables publiées ; recherche/tri/filtres de lignes |
| `features/broadcaster/BroadcasterDashboard.jsx` | B | Classement saison ligue sans dépendance au rejeu |
| `features/replay/FieldAnimation.jsx` | C | Reçoit play, players, selectedNflId, onSelectBack ; aucune requête réseau |
| `features/replay/PressurePanel.jsx` | C | Reçoit observation fixe, paramètres et temps courant distinct |

C définit les types JSDoc des props dans son module et fournit à B un exemple d’utilisation à partir de la fixture commune. B conserve le chargement, la navigation et les erreurs ; C conserve l’horloge et les interactions terrain. Les autres pages consomment le même client, sans import direct de JSON depuis un écran.

La préparation du build valide puis copie l’arborescence de `outputs/site/` vers `website/public/data/`. Le chemin public du manifeste est résolu depuis `import.meta.env.BASE_URL`, pour fonctionner sous un sous-répertoire d’hébergement. Les exports générés de `website/public/data/` sont ignorés par Git et restent dans l’artefact de livraison ; les petites fixtures de test sont versionnées séparément. Le script de préparation et la règle d’ignore font partie du lot B, après livraison du validateur par A.

## 5. Jalons d’intégration

| Jalon | Travail | Condition de passage / preuve |
| --- | --- | --- |
| J0 — Contrat | A crée schémas et fixtures ; B/C vérifient les besoins des consommateurs | Validation des fixtures, champs analysis/quality complétés, même génération et unités partout |
| J1 — Un jeu réel | A évalue et exporte un jeu ; C anime la fixture ; B branche le client et les écrans simples | Flags pression = verdict ; sélection d’un vrai jeu visible dans le site |
| J2 — Un match complet | A exporte tous les jeux et rbSummary ; B/C raccordent liste, tableau et rejeu | Jeux sans pression/au bloc consultables, changement rapide de sélection correct |
| J3 — Saison | A produit les 122 bundles et tableaux ; B branche Coach saison/Broadcaster | Sommes match = saison, rang minimum et référence ligue identiques entre vues |
| J4 — Livraison | C vérifie navigateur/build ; B finalise lancement et README ; A explique les écarts prototype | Cinq jeux audités, build autonome avec JSON servis, limites visibles |

Après J0, B et C avancent en parallèle avec les fixtures partagées pendant qu’A traite les données réelles. J1 puis J2 doivent être intégrés avant le polissage visuel. La carte broadcast par jeu, le GIF et un espace scout dédié restent des extensions, sans bloquer ces jalons.

## 6. Registre de travail partagé

Le propriétaire remplace « à attribuer » par son nom avant de commencer. Un statut passe à intégré seulement avec une référence de commit/PR et une preuve reproductible. La réussite d’un test d’environnement n’autorise pas à marquer une spec métier terminée.

| Travail | Responsable | Statut initial | Dépendance | Preuve attendue |
| --- | --- | --- | --- | --- |
| Contrats, schémas et fixtures J0 | A — à attribuer | À faire | CONTRACTS | Validation et consommation B/C |
| Données et évaluateur | A — à attribuer | À faire | J0 | Tests des seuils, direction, pression et flags |
| Cibles, agrégats et publication | A — à attribuer | À faire | Évaluateur | Conservation match/saison et diagnostics |
| Client web et tableaux | B — à attribuer | À faire | J0 | Parcours match/jeux et deux tables saison |
| Rejeu et pression | C — à attribuer | À faire | J0 | Points mobiles, pause pression, trails et orientation |
| Écran Broadcaster | B — à attribuer | À faire | Tables saison | Classement n≥20, moyenne et caption |
| Livraison et preuves réelles | C avec A/B | À faire | J2/J3 | Tests build + cinq contrôles de jeux |

Statuts autorisés : À faire → En cours → À intégrer → Intégré ; Bloqué indique la ressource ou décision concrète manquante. Un blocage de contrat est traité ensemble avant d’ajouter une variante locale.

## 7. Changer sans désynchroniser

1. Décrire le changement, son motif et les modules consommateurs affectés.
2. Modifier le contrat ou les seuils à leur source, puis les schémas, fixtures et tests correspondants dans le même lot.
3. Mettre à jour la spec ou l’ADR concerné et la version requise ; régénérer toute la publication si les résultats changent.
4. Faire vérifier le même jeu et ses comptes par les modules concernés avant intégration. Une correction locale d’affichage ne répare pas un calcul erroné.
5. Reporter commit/PR, commande exécutée et résultat dans le registre ; les données générées restent identifiées par generationId.

## 8. Vérifications et commandes cibles

Existant : `./prepare_environnement --no-skills`, `./test_env --no-skills`, `npm ci`, `npm run build` et `npm run preview` dans le dossier web. Le lanceur existant ouvre encore Streamlit et doit être adapté au site lors de J4.

À fournir pendant l’implémentation : les CLI build/validate ci-dessus ; `.venv/bin/python -m pytest` pour les tests métier ; `npm run test:e2e` pour Playwright. Le test navigateur tourne sur le build Vite servi localement et vérifie que catalogue, bundles et traces sont réellement accessibles, y compris sous un préfixe de chemin.

Vérifications communes : identifiants stables ; aucune statistique fictive ; couleur et panneau à pression concordants ; pas de dénominateur modifié par pagination/filtre ; conservation match/saison ; cibles inconnues visibles ; mauvais schéma et mauvaise génération refusés. Les cinq contrôles réels consignent gameId/playId/nflId, frame de pression, distances/angle, résultat et nom du vérificateur.
