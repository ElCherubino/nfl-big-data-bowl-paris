# spec-03 — Cibles, résultats et solidité des comparaisons

## Problem Statement

Les utilisateurs veulent comparer les résultats quand une solution RB existe, mais une cible mal reconnue, un jeu compté plusieurs fois ou une différence brute peuvent produire une conclusion trompeuse.

## Solution

Associer prudemment les cibles aux joueurs, comparer les résultats au niveau jeu, publier les effectifs et intervalles à 95 %, et rendre visibles les comparaisons par couverture/blitz et les analyses de sensibilité.

## User Stories

1. En tant que coach, je veux comparer les sacks avec et sans solution pour repérer des jeux à revoir.
2. En tant que scout, je veux savoir si un back disponible a été ciblé pour distinguer opportunité et utilisation.
3. En tant qu’analyste, je veux les cibles inconnues à part pour éviter de les compter comme non ciblées.
4. En tant que coach, je veux le taux de complétion parmi les passes ciblant un RB pour connaître son dénominateur.
5. En tant qu’utilisateur, je veux voir les effectifs derrière chaque taux pour juger sa précision.
6. En tant qu’analyste, je veux un intervalle sur la différence pour évaluer l’incertitude.
7. En tant que coach, je veux comparer Man/Zone et blitz/non-blitz pour examiner l’effet du contexte.
8. En tant qu’analyste, je veux comparer la pression détectée aux labels PFF pour comprendre le proxy.
9. En tant qu’utilisateur, je veux voir les résultats sensibles aux seuils pour éviter une confiance excessive.
10. En tant qu’évaluateur, je veux reproduire les intervalles pour contrôler les chiffres publiés.
11. En tant qu’utilisateur, je veux une conclusion prudente quand les données sont rares pour ne pas lire une absence de preuve comme une équivalence.

## Implementation Decisions

- Population principale : jeux avec pression détectée, au moins un RB/FB en route et disponibilité collective déterminée. Les jeux indéterminés sont comptés à part. Chaque jeu contribue une seule fois aux résultats collectifs.
- Parser playDescription et faire correspondre initiale/nom, variantes de suffixes et équipe offensive à un joueur participant au jeu. Accepter seulement une correspondance unique ; ambiguïté ou texte inexploitable reste inconnu. Statuts : matched, unmatched, ambiguous, not_applicable.
- Sack rate : sacks / jeux éligibles ; différence définie comme taux indisponible moins taux disponible, en points de pourcentage. Afficher aussi les deux taux : un signe positif n’est pas une réduction causale.
- Target rate collectif principal : jeux où un RB/FB en route est ciblé / jeux éligibles dont le statut de cible est connu. Pour S et R sans passe, ciblage non applicable et absence de cible établie ; ils restent au dénominateur de ce taux par dropback avec numérateur zéro. Une passe dont la cible est inconnue est exclue de ce dénominateur et son compte affiché.
- Publier le taux de reconnaissance parmi les passes lancées séparément. Completion RB : jeux C ciblant un RB/FB en route / jeux lancés ciblant un tel back. Pour les colonnes individuelles, vérifier que le nflId ciblé est celui du back observé.
- Plusieurs backs : distinguer « un RB ciblé » et « un RB disponible ciblé » ; ne pas attribuer au back disponible la cible d’un autre. Le site utilise le premier comme comparaison collective et étiquette explicitement le second s’il est présenté.
- Intervalles bootstrap percentile à 95 %, 2 000 réplications par défaut, graine fixe publiée ; rééchantillonner les jeux, en conservant ensemble leurs observations RB. Recalculer taux et différences sur chaque réplication ; publier les réplications exploitables, et signaler un intervalle non estimable si le dénominateur est dégénéré.
- Comparaisons répétées par famille Man/Zone/Other et blitz ≥ 5 joueurs Pass Rush. Une valeur de contexte absente est un groupe inconnu, jamais convertie en non-blitz.
- Proposition de garde d’interprétation : texte directionnel collectif seulement si chaque groupe a ≥ 20 jeux dans son dénominateur pertinent et si l’intervalle de différence exclut zéro. Sinon « différence non concluante » ; les résultats descriptifs restent visibles avec n. Ce seuil est distinct du classement des joueurs.
- Validation du proxy sur les jeux dont le tracking et les labels PFF sont évaluables, y compris sans RB en route : matrice de confusion, précision, rappel, dénominateurs et temps médian à pression. PFF positif si un défenseur a hit/hurry/sack ; labels manquants ne valent pas faux.
- Sensibilités à un paramètre modifié à la fois : pression 1,5/2/2,5 yd, ouverture 2/2,5/3 yd, portée 12/15/18 yd, angle 90°/120°/sans filtre, plus 105°/135° pour rapprocher le prototype. Publier paramètres, populations et intervalles ; ne pas sélectionner le seuil selon la significativité.
- Ne pas promettre la reproduction exacte des chiffres scratch : la correction des cibles inconnues et des jeux multi-RB peut les modifier. Documenter les écarts et conserver les valeurs de référence comme telles.

## Testing Decisions

- Frontière résultats individuels + descriptions → statistiques exportées. Fixtures : cible unique, suffixe, homonyme, ambiguïté, sack, scramble, interception et description non reconnue.
- Sur un petit ensemble à résultats connus, vérifier numérateurs/dénominateurs de chaque taux, exclusions et signe de la différence ; ajouter deux backs sans doubler le nombre de jeux.
- Vérifier rééchantillonnage par jeu, reproductibilité à graine fixe, nuls de dénominateur et garde aux seuils 19/20. Un intervalle large doit empêcher le texte directionnel.
- Contrôler précision/rappel sur une matrice synthétique et les populations de validation différentes de la population RB.
- Pas de référence statistique existante dans le dépôt ; pytest sert aux tests de comportement, et une vérification manuelle indépendante couvre quelques agrégats réels.

## Out of Scope

Effet causal, prédiction d’EPA, yards après réception, trajectoire aérienne, attribution de faute et jointure nflverse obligatoire.

## Further Notes

Critère d’acceptation : tous les taux sont accompagnés de leur population, n et inconnues ; la comparaison globale, les strates et la robustesse sont exportées. Dépendances : specs 01 et 02.
