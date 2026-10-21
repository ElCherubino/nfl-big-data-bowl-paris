---
status: accepted
date: 2026-10-21
---

# ADR-0003 — Un évaluateur, trois niveaux de comptage

Le même back change de couleur pendant le rejeu, mais son taux est fixé par la frame de pression. Nous utilisons un unique évaluateur Python pour chaque frame et pour le verdict, puis des agrégateurs explicites par joueur, match et attaque afin d’éviter des règles divergentes.

## Interface de calcul et états

Le module d’évaluation reçoit un jeu normalisé et ses participants, et renvoie événements, états des backs par frame, observations fixes à la pression et diagnostics. Le module d’agrégation reçoit ces résultats, jamais les coordonnées frontend. Il produit les résumés match, saison et les comparaisons. Les appels et chemins cibles sont détaillés dans [IMPLEMENTATION](IMPLEMENTATION.md).

Le back au bloc a un état `blocking`, distinct de `unavailable`. Une mesure manquante conserve `unknown` si elle empêche de conclure ; un test connu faux suffit à établir l’indisponibilité. La qualité de l’instant de pression est contrôlée séparément : une première pression non garantie empêche de compter le verdict dans les statistiques, même si une frame isolée paraît mesurable.

## Granularités

| Objet | Unité de compte | Référence |
| --- | --- | --- |
| Résumé RB d’un match | Jeu distinct d’un RB/FB dans ce match | Comptes bruts, sans rang/shrinkage/intervalle |
| Saison RB | Observation évaluable joueur–jeu | Somme des résumés match du joueur, seuil n ≥ 20 |
| Saison attaque / résultats collectifs | Jeu distinct de l’attaque | Disponible si au moins un back admissible est disponible |

Si deux backs sont en route sur un jeu, chacun peut contribuer à son propre n. Le jeu contribue une fois au n d’attaque ; un joueur ciblé ne rend pas automatiquement l’autre joueur ciblé. La moyenne de régularisation individuelle porte sur les observations joueur–jeu ; la moyenne collective porte sur les jeux uniques. Les deux sont publiées séparément et peuvent différer.

Une observation à verdict inconnu est comptée dans le diagnostic d’opportunités pressurées mais exclue du n évaluable et du taux ; l’exclusion est visible à tous les niveaux. Ainsi les trois comptes suivants se conservent séparément du match à la saison : opportunités pressurées, observations évaluables, disponibles. Le site indique le n effectivement utilisé.

## Garde-fous de synchronisation

- L’état calculé à `pressureFrameId` est exactement le verdict individuel publié. Les tableaux n’utilisent pas la dernière couleur du rejeu.
- Les sommes des comptes joueur par match égalent les comptes saison du même joueur et périmètre. Pour l’attaque, sommer ses jeux uniques, pas les n des joueurs.
- Les taux, intervalles, ranks, percentiles et flags sont publiés par Python. Le navigateur peut trier, rechercher, masquer ou sélectionner des lignes ; il ne recalcule pas de statistique football.
- Le filtre équipe des tableaux saison sélectionne les lignes avec les statistiques saison ligue publiées et garde leur référence ligue. Un recalcul dans une autre cohorte exige un export explicite et étiqueté, absent du POC.
- Les comptes PFF/proxy, les inconnues de cible et les observations exclues sont conservés ; les nombres scratch du descriptif ne sont pas des assertions à forcer.

L’alternative consistant à agréger les lignes visibles du tableau dans le navigateur donne des valeurs trompeuses après pagination ou filtre. Elle est écartée au profit d’agrégats calculés et testés avec la population entière.
