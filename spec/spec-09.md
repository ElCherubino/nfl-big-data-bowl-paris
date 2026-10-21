# spec-09 — Comptes RB par match et conservation saison

## Problem Statement

Quelques jeux par back ne permettent pas un classement fiable sur un match. Le coach doit lire des comptes, retrouver leurs actions et vérifier qu’ils correspondent aux totaux saison.

## Solution

Publier dans chaque bundle match un tableau non classé de tous les RB/FB des deux équipes ayant couru une route sur au moins un jeu pressuré, puis contrôler la conservation des comptes du match à la saison.

## User Stories

1. En tant que coach, je veux voir les backs des deux équipes pour revoir leurs solutions de secours.
2. En tant que coach RB, je veux disponibles / routes pressurées et taux brut pour lire le compte exact.
3. En tant que coach, je veux savoir combien de fois un back disponible a été ciblé pour distinguer occasion et utilisation.
4. En tant que coach, je veux cliquer une ligne pour retrouver les jeux de ce back.
5. En tant qu’utilisateur, je veux un avertissement petit échantillon pour ne pas transformer un compte en classement.
6. En tant qu’analyste, je veux identifier les observations inconnues pour expliquer un dénominateur réduit.
7. En tant que développeur, je veux que la somme des comptes par match égale les comptes saison du joueur.
8. En tant qu’analyste, je veux des comptes équipe distincts des observations joueur pour ne pas compter deux fois un jeu multi-back.
9. En tant qu’évaluateur, je veux qu’un écart de conservation bloque la publication pour détecter une régression.
10. En tant que coach, je veux qu’un taux indéterminé ne soit jamais remplacé par zéro.

## Implementation Decisions

- Une ligne par couple équipe offensive/nflId dans le match pour tout RB/FB avec au moins une route sur jeu à pression détectée. Exposer effectif source, observations évaluables n, disponibles et exclusions inconnues ; si aucune observation n’est évaluable, conserver la ligne avec n = 0 et taux indisponible.
- Taux brut = disponibles / observations individuelles éligibles n. Présenter « disponibles / n · % » ; les routes pressurées indéterminées sont signalées à côté, sans les compter comme indisponibles. La même règle de qualité s’applique à la saison.
- Ciblage lorsque disponible : ciblages de ce back parmi ses jeux disponibles à statut de cible connu, avec numérateur/dénominateur et compte inconnu selon spec-03. Pas de copie du ciblage d’un autre back.
- Aucun rang, shrinkage, intervalle ou percentile au match. Ordre neutre stable par équipe puis nom/identifiant ; légende « petit échantillon, utiliser les jeux comme références vidéo ».
- Le clic sur une ligne sélectionne le back et filtre la liste aux jeux auxquels il participe ; les contrôles permettent de retirer le filtre. Son identité est conservée dans l’URL du parcours coach.
- Publication statique : tableau et liens de jeux inclus dans le bundle match, taux calculés en Python. Le navigateur n’agrège pas les frames ou jeux pour reconstruire ce tableau.
- Conservation individuelle sur le même périmètre/paramétrage : somme des n, disponibles, ciblages connus, dénominateurs de ciblage et exclusions par match = ligne saison correspondante. Pour un joueur multi-équipe, les composantes équipe se réconcilient avec son total global.
- Conservation équipe : chaque jeu contribue au plus une fois à la disponibilité collective ; n’équipe et disponibles-équipe saison = somme des comptes collectifs des matchs de cette attaque. Ne jamais exiger égalité entre somme des observations RB et jeux équipe lorsque deux backs courent une route.
- Bloquer la publication en cas d’écart ; rapporter identifiant, champ et valeurs attendue/observée. Les zéros de numérateur restent distingués des taux sans dénominateur.

## Testing Decisions

- Frontière observations → bundle match et tables saison : fixture sur deux matchs, deux équipes, plusieurs backs dont deux sur un même jeu, et un joueur multi-équipe. Calculer les comptes attendus à la main.
- Vérifier faibles n, n = 0 dû à inconnues, absent au match et cible inconnue ; aucune ligne ne reçoit de rang, intervalle ou shrinkage.
- Injecter un écart de compte pour vérifier le refus de publication et le diagnostic ; vérifier conservation des exclusions et dénominateurs de cibles, pas seulement des pourcentages arrondis.
- Parcours navigateur : cliquer la ligne sélectionne le bon joueur et les bons jeux ; retirer le filtre restaure la liste sans modifier le tableau saison.
- Tests par exports publics et parcours site déjà validés ; aucun test du découpage interne des fonctions.

## Out of Scope

Classement de match, inférence sur la performance du match, shrinkage de petits échantillons au match et calcul d’agrégats dans le navigateur.

## Further Notes

Acceptation : les tableaux match sont lisibles comme des comptes et tous leurs champs s’additionnent vers les exports saison à granularité identique. Dépendances : specs 01, 02, 03 et 04 ; alimente spec-06 et contrôle final spec-08.
