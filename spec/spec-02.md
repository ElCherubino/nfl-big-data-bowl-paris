# spec-02 — Pression et disponibilité du running back

## Problem Statement

Un RB éloigné de son défenseur n’est pas automatiquement une solution pour le QB. Le coach doit savoir si le back est ouvert, proche, assez avancé et tourné vers le QB au premier instant de pression.

## Solution

Calculer un instant de pression unique par jeu et évaluer les cinq conditions pour chaque RB/FB en route. Publier les distances, l’angle et les raisons d’échec, avec une disponibilité collective sans double comptage.

## User Stories

1. En tant que coach, je veux retrouver le premier instant de pression pour évaluer le même moment sur chaque jeu.
2. En tant que coach RB, je veux exclure les backs affectés au bloc pour ne pas les pénaliser comme receveurs.
3. En tant que coach, je veux voir la séparation au défenseur le plus proche pour vérifier l’ouverture.
4. En tant que coach, je veux mesurer la distance au QB pour distinguer une solution proche d’une route profonde.
5. En tant que coach, je veux situer le RB par rapport à la ligne pour identifier une solution utilisable.
6. En tant que scout, je veux voir l’angle vers le QB pour comprendre le filtre d’orientation.
7. En tant qu’analyste, je veux obtenir le même résultat dans les deux sens de jeu pour comparer équitablement.
8. En tant que coach, je veux inspecter chaque back d’un jeu à plusieurs RB pour ne pas masquer une option.
9. En tant qu’utilisateur, je veux voir un état indéterminé si une mesure manque pour éviter une conclusion fausse.
10. En tant qu’analyste, je veux distinguer absence de pression et absence de solution pour calculer le bon dénominateur.
11. En tant que commentateur, je veux le temps depuis le snap pour ancrer mon explication dans l’action.

## Implementation Decisions

- QB identifié par le rôle PFF Pass ; back admissible si officialPosition vaut RB ou FB et rôle Pass Route. Normaliser espaces/casse des libellés sans modifier leur sens. Un rôle inconnu reste inconnu.
- Snap : première frame ball_snap ou autoevent_ballsnap. Fin : premier événement de passe ou sack après le snap, avec alias automatiques ; pour un scramble, événement run s’il existe. Ne pas prolonger la recherche après le lancer. Sans fin identifiable, conserver le diagnostic et exclure le jeu du score par défaut.
- Pression : première frame strictement après le snap et au plus tard à la fin, avec un défenseur Pass Rush ou Coverage à distance euclidienne ≤ 2 yd du QB. Chercher sur tous ces défenseurs, pas uniquement les rushers. Publier frame, défenseur, distance et temps en secondes à 10 Hz.
- Normalisation : attaque vers +x ; pour une attaque à gauche, rotation de 180° sur le terrain 120 × 53,3 yd et rotation correspondante de l’orientation. Toutes les distances restent en yards.
- Ligne : x de la balle au snap normalisé. Progression du back = x du back moins x de la ligne.
- Conditions au même pressure frame : route admissible ; distance au défenseur le plus proche > 2,5 yd ; distance au QB < 15 yd ; progression ≥ −1 yd ; angle absolu minimal vers le QB < 90°.
- Bearing RB→QB : atan2 de la différence x et de la différence y, en degrés, avec 0° vers +y et 90° vers +x. Réduire l’écart d’orientation dans [0°, 180°]. Utiliser o, jamais la direction de déplacement dir comme substitut.
- Chaque condition possède valeur, unité, seuil et statut. Disponibilité individuelle vraie si tout passe ; fausse si au moins une condition connue échoue ; sinon indéterminée. Ne pas transformer une orientation manquante en échec certain.
- Plusieurs backs : jeu disponible si au moins un back admissible est disponible ; indisponible si tous sont évaluables et indisponibles ; sinon indéterminé. Conserver chaque observation individuelle et les comptes de backs en route et au bloc.
- Absence de défenseur, balle au snap ou coordonnées nécessaires : mesure indéterminée. Un trou de tracking avant la première pression observée empêche de garantir qu’il s’agit de la première : signaler et exclure le jeu des statistiques principales, sans interpolation métier.
- Évaluer les quatre checks spatiaux à chaque frame du snap à la fin pour chaque RB/FB, y compris sur les jeux sans pression. Publier valeurs et flags avant arrondi des positions. Le rôle reste fixe : un back au bloc est gris et exclu du score. La disponibilité officielle du jeu reste celle à la frame de pression ; les couleurs des autres frames n’altèrent jamais ce verdict. À la frame de pression, flags et verdict individuel doivent coïncider.
- Seuils paramétrables et versionnés ; seuils par défaut figés avant lecture des résultats. Le navigateur affiche les checks prépubliés et ne recalcule aucune mesure métier.

## Testing Decisions

- Tester la frontière tracking/scouting → observations exportées avec positions synthétiques à résultat calculable à la main.
- Couvrir chaque frontière exacte : 2 yd, 2,5 yd, 15 yd, −1 yd et 90°, ainsi que leurs voisins. Vérifier le passage 359°/1°, les deux sens et la rotation des orientations.
- Couvrir pression avant/après lancer, événements dupliqués sur les joueurs, alias, sack sans lancer, scramble, snap absent et absence de pression.
- Couvrir plusieurs backs, back au bloc, défenseur Coverage le plus proche et donnée manquante. Vérifier une seule observation collective par jeu.
- Vérifier l’égalité entre les flags de la frame de pression et le verdict, avec une trajectoire rouge → verte → rouge ; un jeu sans pression conserve des checks par frame sans entrer au dénominateur.
- Aucun test métier existant ; utiliser pytest déjà disponible. Les diagnostics d’environnement ne remplacent pas ces assertions.

## Out of Scope

Ligne de passe non obstruée, probabilité de réception, regard réel du joueur, attribution du défenseur assigné et interprétation causale de la disponibilité.

## Further Notes

Critère d’acceptation : chaque observation évaluable est justifiée par cinq conditions vérifiables sur la même frame ; les autres états ont un motif. Dépendance : spec-01.
