# Audit d’alignement — description RB Lifeline mise à jour

Date : 2026-10-21. Audit documentaire de la description complète et des specs 01–08 ; ce document ne valide aucun code ni chiffre du prototype.

## Corrections apportées

| Exigence de la description | Couverture mise à jour |
| --- | --- |
| Un site statique, deux entrées Coach / Broadcaster | 06, 07 ; retrait du troisième profil obligatoire |
| Tous les dropbacks de chaque match, filtre initial pression + route RB | 01, 06, 08 |
| Catalogue semaine/équipes/score vérifié, aucune valeur inventée | 06 |
| Bundle par match, toutes ses frames chargées à son ouverture | 01, 05, 06 ; remplace le chargement par jeu |
| Positions arrondies à 0,1 yd, o et flags par frame ; aucune géométrie navigateur | 01, 02, 05 |
| Quatre checks spatiaux à chaque frame, rôle au bloc gris, verdict à la pression | 02, 05 |
| 22 joueurs + balle, traces RB/QB et courtes traces des autres, flèches RB/QB | 05 |
| 10 Hz, 0,5×/1×, curseur, arrêt à la pression, défenseur QB et panneau cinq checks | 05 |
| Jeux sans pression consultables, non comptés | 01, 02, 05, 06 |
| Tableau match des deux équipes, comptes/brut/cibles sans rang ni shrinkage/intervalle | **09 ajoutée**, 06 |
| Clic RB du tableau match → filtre ses jeux | 09, 06 |
| Table RB saison complète, sous-minimum grisé, tri/filtre équipe, table attaques | 04, 06 |
| Broadcaster saison ligue uniquement : régularisé, brut, n, percentile, moyenne et limite | 07 réécrite ; ancienne carte par jeu déplacée hors POC |
| Saison explicitement limitée à 2021 semaines 1–8 | 04, 06, 07, 08 et décisions communes |
| Pression proxy, cibles reconnues/inconnues, bootstrap par jeux, strates et sensibilité | 02, 03 ; couverture conservée |
| Comptes match → saison, flags pression = verdict, petits n et multi-back | 02, 05, **09**, 08 |
| Cinq jeux contrôlés visuellement, exemples completion/sack, absence de synthétique | 08 |
| GIF, commentaire par jeu et vues scout spécifiques optionnels | 05–08 et README ; exigences obligatoires supprimées |

## Clarifications d’intégration

- Les inconnues de cible restent exclues du dénominateur pertinent et comptées explicitement, comme l’exige la description pour la réimplémentation propre. Les résultats peuvent donc différer des valeurs scratch, qui comptaient parfois les inconnues comme non ciblées.
- Un jeu avec plusieurs backs produit des observations individuelles mais une seule observation collective. Les totaux joueur et équipe se conservent séparément ; leurs n ne sont pas nécessairement égaux. La moyenne ligue utilisée pour le shrinkage doit correspondre à la granularité publiée, et non à un 15,0 % figé.
- Les états inconnus dus à la qualité sont conservés et expliqués. Un back avec routes pressurées mais aucune observation évaluable peut avoir une ligne match avec n = 0, exclusions et taux indisponible.
- Filtrer des lignes de table équipe ne recalcule aucune statistique dans le navigateur. Toute variante statistique supplémentaire exige des résultats précomputés identifiés.
- Valeurs après arrondi et flags peuvent sembler proches d’un seuil ; les flags et mesures issus des valeurs de précision de calcul font foi.
- Les noms et schémas techniques, propriétaires des modules et points d’intégration sont définis dans les [ADR](../adr/). Cet audit vérifie la couverture fonctionnelle ; les contrats n’ont qu’une source technique dans les ADR.

## État et limites de cet audit

Aucune exigence POC supplémentaire non couverte n’a été identifiée après ajout de spec-09 et corrections ci-dessus. Les choix ouverts restent ceux de la source : variantes de seuils/minimum/FB, jointure externe facultative et éventuel hébergement selon règles. Les valeurs par défaut de la source permettent l’implémentation ; tout changement est versionné et régénère les exports. Les conditions d’événement restent prioritaires sur ces documents de préparation.
