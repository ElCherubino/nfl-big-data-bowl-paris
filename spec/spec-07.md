# spec-07 — Broadcaster : classement saison « Best safety valves »

## Problem Statement

Le commentateur a besoin d’un classement vérifié immédiatement citable, sans analyser un rejeu ni produire un récit à partir de données incomplètes.

## Solution

Une page unique affiche le classement ligue des RB/FB éligibles sur 2021 semaines 1–8, avec régularisation, n, percentile, moyenne ligue et limites fixes.

## User Stories

1. En tant que commentateur, je veux un classement ligue pour identifier les meilleurs points de sortie observés.
2. En tant que commentateur, je veux le taux régularisé et le taux brut pour citer la bonne mesure.
3. En tant que commentateur, je veux n pour qualifier mon propos.
4. En tant que commentateur, je veux un percentile calculé pour situer un joueur parmi les backs éligibles.
5. En tant que producteur, je veux une seule page lisible sans animation pour préparer l’antenne.
6. En tant que spectateur, je veux la période affichée pour ne pas lire huit semaines comme une saison entière.
7. En tant que commentateur, je veux une phrase construite depuis la table pour ne pas inventer une conclusion.
8. En tant qu’utilisateur, je veux la moyenne ligue et la définition du taux pour interpréter le classement.
9. En tant qu’évaluateur, je veux retrouver chaque chiffre dans la table saison publiée.
10. En tant que commentateur, je veux que les petits échantillons soient exclus pour éviter un superlatif fragile.

## Implementation Decisions

- Une page « Best safety valves », sans choix de jeu, rejeu, animation ou texte de modèle. Données issues de la même table saison RB que la vue coach ; aucune API ni génération LLM.
- Cohorte ligue entière, RB et FB inclus par défaut, n ≥ 20. Tri par taux régularisé décroissant avec ordre stable défini en spec-04. Les joueurs sous minimum ne figurent pas dans cette page.
- Colonnes : rang, joueur, équipe(s) observée(s), taux régularisé principal, brut secondaire, n, percentile publié. Période visible « 2021 · semaines 1–8 ».
- Afficher une référence visuelle à la moyenne ligue calculée et publiée. Ne coder en dur ni les 15,0 %, ni les 48 joueurs, ni les noms du prototype ; toute divergence du recalcul reste explicable.
- Légende fixe au sens suivant : « Part des snaps sous pression où le RB était ouvert, à portée, assez avancé et orienté vers le QB. Reflète le joueur et le design de son attaque ; ce n’est pas une note causale. » Rappeler le dénominateur : jeux pressurés où le RB court une route.
- Une phrase courte éventuelle utilise uniquement les champs publiés : joueur, classe percentile, n et période. « Top 10 % » exige percentile ≥ 90 sur la cohorte ligue éligible ; sinon utiliser le percentile exact ou une formulation sobre. Aucun récit sur une action individuelle.
- Ligne et phrase sont rattachées à la même génération ; données manquantes ou incompatibles donnent un état d’erreur/vide, jamais un classement de secours synthétique.

## Testing Decisions

- Frontière table saison → écran : vérifier valeurs et ordre avec des scores distincts, égalités, n = 19/20 et une cohorte vide.
- Vérifier qu’aucune ligne sous minimum ne figure au classement et que brut/régularisé restent distincts.
- Vérifier la phrase au seuil du percentile, son n et sa période ; refuser un top 10 % injustifié.
- Vérifier la concordance des chiffres coach/broadcaster, la moyenne issue de l’export et la présence des limites fixes.
- Parcours navigateur sans chargement de bundle match ni appel de modèle ; la page ne propose aucun contrôle de rejeu.

## Out of Scope

Commentaire par jeu, animation broadcaster, voix, GIF, flux en direct, texte généré par modèle et conclusion causale.

## Further Notes

Acceptation : un commentateur peut citer un rang, son taux, n et période depuis une page traçable aux calculs saison. Dépendances : specs 01 et 04. Remplace le périmètre antérieur de carte commentateur par jeu, désormais optionnel hors POC.
