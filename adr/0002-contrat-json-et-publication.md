---
status: accepted
date: 2026-10-21
---

# ADR-0002 — Un contrat partagé et une publication immuable par génération

Les développeurs Python, tableaux web et rejeu ont besoin d’une interface stable pour travailler séparément. Nous publions les fichiers imposés par le produit avec une enveloppe commune, des identifiants et unités fixes, et un bundle chargé par match ; le détail normatif figure dans [CONTRACTS](CONTRACTS.md).

Une publication contient `manifest.json`, `games.json`, `season_rb.json`, `season_team.json`, puis un `game_<gameId>.json` pour chaque match. Les comparaisons statistiques sont publiées dans `analysis.json` et les diagnostics dans `quality.json`, référencés par le même manifeste. Le bundle de match contient tous ses dropbacks, leurs frames, observations et résumé RB ; une sélection de jeu ne déclenche pas une seconde requête de trajectoire.

## Cohérence de publication

- `schemaVersion` initial vaut `1.0.0`. `generationId` identifie sources, paramètres et version de calcul ; même génération dans tous les fichiers.
- Écrire dans un dossier temporaire, valider schémas et références, puis déplacer dans un dossier immuable de génération. Le manifeste public est remplacé en dernier ; il référence les ressources par chemin relatif incluant la génération.
- Exemple de localisation finale : `data/manifest.json` référence `generations/<generationId>/games.json` et les autres ressources. L’index des jeux référence les bundles de cette même génération.
- Le site charge une fois le manifeste et garde sa génération pendant la session. Un fichier d’une autre génération provoque une erreur lisible ; le client ne fusionne pas des fragments incompatibles.
- Des fichiers immuables peuvent être mis en cache ; le manifeste doit être revalidé au chargement. Conserver l’ancienne génération tant qu’un client peut encore l’utiliser ou livrer l’ensemble dans une archive/build cohérent.
- Les coordonnées publiées sont arrondies à 0,1 yd pour la taille des fichiers. Les seuils et flags sont calculés sur la précision source ; le site ne recalcule aucun score à partir des coordonnées arrondies.

## Évolution du contrat

Le propriétaire du pipeline porte le schéma, et les propriétaires des deux consommateurs relisent ses changements. Un champ requis, un nom, une unité, un sens de flag ou une granularité modifiés entraînent une nouvelle version majeure. Un ajout facultatif compatible peut changer la version mineure. Une modification de résultats sans changement de forme produit au minimum une nouvelle génération avec sa version de calcul.

Le client supporte explicitement la majeure 1 et vérifie les champs qu’il utilise ; le validateur Python vérifie tout le document et ses invariants. Les schémas et fixtures générées depuis la même définition sont livrés dans une modification coordonnée. Copier des JSON fictifs dans les pages produit pour contourner un export manquant n’est pas un mode de fonctionnement.

## Alternative et coût assumé

Un fichier par jeu serait plus petit mais divergerait du flux POC et multiplierait les requêtes. Une unique saison JSON imposerait de charger toutes les trajectoires à tous les visiteurs. Le bundle match garde une sélection de jeu immédiate après ouverture du match ; la mémoire frontend est bornée à deux bundles, et le build mesure la taille des ressources plutôt que promettre une latence sans mesure.
