# spec-06 — Site connecté et parcours coach

## Problem Statement

Le template contient des données synthétiques et des actions non reliées aux calculs. Le coach doit passer d’un match à ses jeux et à ses tableaux, sans confondre échantillon du match et saison.

## Solution

Livrer un site statique avec deux entrées Coach / Broadcaster. Le coach ouvre un match puis consulte ses dropbacks, son tableau RB et les tableaux saison. L’entrée broadcaster suit la spec-07.

## User Stories

1. En tant que coach, je veux choisir un match par semaine et équipes pour retrouver mon contexte.
2. En tant que coach, je veux revoir chaque dropback du match pour ne pas perdre les jeux hors métrique.
3. En tant que coach, je veux un filtre initial limité aux jeux pressurés avec RB en route pour revoir le dénominateur principal.
4. En tant que coach, je veux retirer ce filtre pour voir les jeux sans pression et les backs au bloc.
5. En tant que coach, je veux quart-temps, horloge, down/distance et description pour identifier le jeu.
6. En tant que coach, je veux un badge pression/disponibilité/bloc et un résultat sack/complétion/incomplétion/cible RB pour sélectionner une action.
7. En tant que coach, je veux ouvrir le rejeu d’une ligne pour vérifier les checks.
8. En tant que coach, je veux le tableau de chaque RB/FB des deux équipes pour lire les comptes du match.
9. En tant que coach, je veux cliquer un back de ce tableau pour filtrer ses jeux.
10. En tant que coach ou scout, je veux le tableau saison des RB et celui des attaques pour situer les performances observées.
11. En tant qu’utilisateur, je veux voir « 2021 · semaines 1–8 » pour connaître la portée de saison.
12. En tant qu’utilisateur, je veux des erreurs et des états vides explicites plutôt que des chiffres de démonstration.
13. En tant qu’utilisateur mobile, je veux des tableaux et commandes utilisables au clavier et sur petit écran.
14. En tant qu’évaluateur, je veux comprendre les biais et l’usage propre à chaque entrée.

## Implementation Decisions

- Étendre le site React/Vite existant. Deux entrées uniquement : Coach et Broadcaster ; pas de compte ni d’entrée scout dédiée. Les scouts utilisent le tableau saison du coach.
- Parcours coach : choix match → trois vues « Play by play », « RB — ce match », « RB — saison ». Le tableau saison est global à la période, sans réduction implicite au match sélectionné ; il inclut le tableau des attaques.
- Catalogue des matchs : semaine, équipes et score seulement si fourni par une source vérifiée ; sinon valeur indisponible, jamais score déduit des plays ou inventé.
- Liste de tous les dropbacks : métadonnées, description originale, résultat et badges. Filtre initial : pression détectée avec au moins un RB/FB route runner ; le retirer rend visibles sans pression, bloc et diagnostics. Un RB individuel indéterminé n’est pas affiché comme indisponible certain.
- Résumés individuels de match selon spec-09. Tableau saison triable et filtrable par équipe selon spec-04 : tous les RB, sous-minimum grisés sans rang, n, disponibles, brut, régularisé, intervalle, ciblage lorsque disponible et complétion lorsqu’il est ciblé.
- Client de données unique : manifeste, tables saison et catalogue, puis bundle du match ouvert. Les calculs Python font foi ; le site affiche les lignes et flags publiés sans recalcul de taux, rang, percentile ou géométrie.
- Respecter les chemins relatifs du déploiement statique et la génération commune. Refuser un schéma incompatible ou un mélange de générations ; conserver des états chargement/vide/erreur/réessayer.
- Synchroniser entrée, match, jeu et back sélectionnés dans l’URL ; précédent/suivant restaure le choix. Une sélection invalide offre un retour à un catalogue valide sans jouer silencieusement une autre action.
- Retirer KPI, roster, routes, tendances et saison fictifs. Garder uniquement les écrans réellement implémentés ; aucun chiffre synthétique ne reste dans le produit livré.
- Aide obligatoire : définition et dénominateur de disponibilité avec n, proxy de pression, orientation corporelle, sélection au bloc, inconnues des cibles, petits échantillons, association non causale et huit semaines historiques.
- Interface cohérente en français ; noms propres et codes source inchangés. Un résultat absent reste indisponible. Couleur jamais seul support du sens.

## Testing Decisions

- Parcours principal validé : site → match → jeu → animation ; vérifier les identifiants, métadonnées et mesures contre les exports, puis les tableaux match/saison.
- Fixture comportant pression, sans pression, bloc et données manquantes : vérifier filtre initial puis accès à tous les dropbacks.
- Clic RB du tableau match filtre ses jeux ; changement match réinitialise les sélections incompatibles. La table saison conserve sa portée.
- Vérifier deux entrées, navigation URL, tri/filtre de lignes sans modification des taux publiés, schéma incompatible, erreur réseau et réponse tardive.
- Test mobile/clavier et build statique avec ressources réellement servies. Les diagnostics d’environnement ne remplacent pas ce parcours.

## Out of Scope

Vue scout dédiée, comparateur de joueurs, dashboard football généraliste, filtrage recalculant les statistiques dans le navigateur, authentification et classement au match.

## Further Notes

Acceptation : tout match disponible ouvre ses dropbacks et son tableau RB ; les deux entrées ont leur usage documenté et ne montrent que des chiffres calculés. Dépendances : specs 03, 04, 05, 07 et 09.
