# spec-04 — Classements RB/FB et attaques

## Problem Statement

Un pourcentage élevé sur quelques actions peut dominer un classement sans représenter une capacité stable. Scouts et coaches ont besoin de comparaisons lisibles et de liens vers les jeux sous-jacents.

## Solution

Proposer un classement individuel pour sélectionner les joueurs à revoir et un classement des attaques pour examiner le design des solutions de secours. Afficher valeurs brutes, shrinkage, effectifs, incertitude et preuves.

## User Stories

1. En tant que scout, je veux trier les backs par disponibilité régularisée pour limiter l’influence des petits échantillons.
2. En tant que scout, je veux le taux brut à côté du taux régularisé pour comprendre le classement.
3. En tant que scout, je veux voir n et l’intervalle pour estimer la confiance.
4. En tant que scout, je veux repérer un joueur souvent disponible mais peu ciblé pour orienter ma revue vidéo.
5. En tant que front office, je veux lire plusieurs lignes du tableau saison sur le même périmètre pour préparer une shortlist.
6. En tant que coach, je veux classer les attaques pour comparer des situations collectives.
7. En tant que coach, je veux ouvrir les jeux d’un taux d’équipe pour comprendre ce qu’il recouvre.
8. En tant que scout, je veux rechercher un joueur réel pour retrouver ses observations.
9. En tant qu’utilisateur, je veux voir les joueurs sous le minimum comme non classés pour ne pas les confondre avec les derniers.
10. En tant que commentateur, je veux un percentile traçable pour vérifier une phrase de classement.
11. En tant qu’analyste, je veux changer le minimum et l’inclusion FB dans une variante identifiée pour mesurer la stabilité.

## Implementation Decisions

- Observation individuelle : un back en route sur un jeu pressuré et évaluable ; n compte les jeux distincts de ce joueur. Les exclusions pour qualité sont visibles. Un joueur est identifié par nflId, jamais par son numéro de maillot.
- Disponibilité individuelle brute = jeux disponibles / jeux évaluables du joueur. Shrinkage = (disponibles + 20 × moyenne de référence) / (n + 20).
- Moyenne de référence des joueurs : disponibilité sur l’ensemble des observations joueur-jeu éligibles. Celle des équipes utilise les jeux collectifs uniques. Les distinguer explicitement lorsque plusieurs backs apparaissent sur un même jeu ; ne pas réutiliser mécaniquement le 15 % du prototype.
- Rang individuel par taux régularisé décroissant, puis n décroissant, puis identifiant stable. Classement principal à n ≥ 20. Variantes n ≥ 15/30 et RB seul séparées du classement par défaut.
- Intervalle à 95 % sur le taux brut par bootstrap des jeux, avec méthode, graine et dénominateur affichés. L’étiquette précise qu’il ne s’agit pas d’un intervalle sur le rang ni sur le taux régularisé.
- Colonnes : identité, poste, équipe(s) observée(s), n, disponibles, brut, régularisé, intervalle, ciblage lorsque disponible avec effectif connu, complétion lorsqu’il est ciblé et jeux consultables. Un dénominateur nul donne indisponible.
- Équipes : agréger selon possessionTeam du jeu. Un joueur présent dans plusieurs équipes conserve son identité et une seule ligne saison regroupant tous ses jeux de la période. Le filtre équipe sélectionne cette ligne si l’équipe figure parmi ses équipes observées ; ses comptes restent ceux de toute la période et son rang reste ligue. Ce filtre ne crée pas une statistique propre à son passage dans cette équipe.
- Classement attaque : disponibilité collective sur jeux uniques, même minimum de 20, valeurs brutes/régularisées et n. Les 32 équipes annoncées par le prototype ne sont pas imposées si la qualité réduit la population.
- Périmètre de saison fixe affiché partout : « 2021 · semaines 1–8 ». Le filtre équipe de la table coach sélectionne les lignes précomputées ; le tri affiche les scores publiés. Il ne recalcule ni shrinkage, ni rang, ni percentile. Les variantes et strates sont calculées hors navigateur et publiées séparément si exposées. Le classement broadcaster reste ligue entière.
- Percentile : au sein des joueurs éligibles de la cohorte, 100 × (joueurs avec score inférieur + moitié des autres joueurs à égalité) / (nombre de joueurs moins 1). Non calculable pour un seul joueur ; égalités et taille de cohorte affichées. Une phrase « top 10 % » exige percentile ≥ 90 et cohorte ligue explicitement définie.
- Tous les RB/FB observés dans la population saison restent consultables. Sous n = 20 : ligne grisée, « n insuffisant », sans rang ni percentile. La vue coach montre aussi le tableau saison des attaques ; les tableaux par match suivent la spec-09 et ne sont jamais des classements.

## Testing Decisions

- Frontière observations → classements : contrôler formule à la main, référence individuelle vs collective, multi-RB, multi-équipe, égalités et seuils 19/20/21.
- Vérifier qu’un joueur avec n insuffisant reste consultable sans rang ni percentile, et que le filtre équipe ne change ni sa valeur ni le rang de référence ligue.
- Vérifier les colonnes de ciblage avec inconnues et l’intervalle correctement étiqueté.
- Parcours site : tri, recherche et ouverture d’un jeu conservent le périmètre. Pas de tests d’implémentation de composants ; aucune suite frontend existante.

## Out of Scope

Comparateur dédié de deux joueurs, vue scout dédiée, draft grades, valorisation contractuelle, ajustement complet QB/ligne offensive/adversaire, classement tous postes et généralisation hors saison observée.

## Further Notes

Critère d’acceptation : un scout peut choisir un joueur à revoir et ouvrir une preuve ; un coach peut faire la même démarche sur une attaque. Dépendances : specs 02 et 03.
