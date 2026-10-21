# Spécifications — RB Lifeline

**Implémentation livrée :** [état par spec et preuves](IMPLEMENTATION_STATUS.md), [validation du produit](../docs/validation.md). Les sections ci-dessous conservent le découpage de conception ; les exports et tests constituent la preuve d’implémentation.

Source fonctionnelle : [rb_lifeline.md](../rb_lifeline.md). Point de départ visuel : [website](../website/README.md). Décisions techniques et répartition du travail : [adr/](../adr/).
Ces spécifications suivent le format du skill `to-spec` et décrivent du travail à réaliser, sans prétendre qu’il est déjà livré.
L’audit de la description mise à jour est dans [ALIGNMENT.md](ALIGNMENT.md).

## Découpage et ordre de réalisation

| Spec | Périmètre | Dépendances |
| --- | --- | --- |
| [spec-01](spec-01.md) | Chargement, qualité et contrat de publication par match | Aucune |
| [spec-02](spec-02.md) | Pression, checks à chaque frame et verdict fixé à la pression | 01 |
| [spec-03](spec-03.md) | Cibles, résultats, intervalles et robustesse | 01, 02 |
| [spec-04](spec-04.md) | Tables saison RB/FB et attaques | 02, 03 |
| [spec-05](spec-05.md) | Rejeu : points mobiles, traces, orientation, couleurs et arrêt à la pression | 01, 02 |
| [spec-09](spec-09.md) | Comptes RB par match et conservation vers la saison | 01, 02, 03, 04 |
| [spec-06](spec-06.md) | Site connecté et trois vues du parcours coach | 03, 04, 05, 07, 09 |
| [spec-07](spec-07.md) | Broadcaster : classement saison « Best safety valves » | 01, 04 |
| [spec-08](spec-08.md) | Exécution, validation finale et livraison | Ensemble |

L’ordre des numéros conserve les références existantes ; réaliser les dépendances avant le consommateur. Les trois flux peuvent avancer avec des fixtures partagées : pipeline/contrat/statistiques, site/tableaux, rejeu/intégration navigateur. Voir la répartition et les critères d’intégration dans les ADR.

## Décisions communes

- Un site statique, deux entrées : Coach et Broadcaster. Le coach a les vues play by play, RB du match et RB/attaques saison. Le scout utilise la table saison ; aucune entrée scout dédiée au POC.
- Saison affichée « 2021 · semaines 1–8 », jamais saison entière. Les chiffres scratch sont à reproduire ou corriger, jamais des constantes du site.
- Seuils par défaut : pression ≤ 2 yd ; séparation > 2,5 yd ; distance QB–RB < 15 yd ; progression ≥ −1 yd ; angle < 90°. RB et FB inclus ; rang saison à partir de n = 20 ; shrinkage k = 20. Variantes calculées séparément, pas sélectionnées selon le résultat.
- Jeu = couple gameId/playId ; observation individuelle = jeu/nflId. Plusieurs backs ne multiplient pas les jeux collectifs. Les comptes individuels et collectifs ont des dénominateurs distincts explicités dans les ADR.
- La disponibilité officielle est évaluée à la première pression. Les couleurs du replay suivent les checks spatiaux de chaque frame et ne changent pas ce verdict. Le Python publie mesures et flags autoritaires avant arrondi ; le site n’en refait aucun calcul.
- Publication commune : manifeste, tables saison RB/équipes, catalogue des matchs, bundle par match avec tous ses dropbacks, frames et tableau RB. Le match est chargé à son ouverture ; aucun téléchargement par jeu. Les ressources partagent une génération et un schéma.
- Tableau match : disponibles / n, brut et ciblage lorsque disponible ; aucun rang, shrinkage ou intervalle. Conservation des comptes match → saison obligatoire.
- Broadcaster : classement ligue saison seul, n ≥ 20, taux régularisé/brut, percentile, moyenne ligue et limite non causale ; aucun rejeu, vue par jeu ou texte de modèle.
- Pas d’authentification, de direct ou de données inventées. GIF, commentaire par jeu, comparateur et vue scout dédiée sont optionnels hors POC.
- Deux parcours de vérification déjà validés : données → résultats exportés ; site → match → action → rejeu animé. Tests synthétiques ciblés sur géométrie, règles statistiques et conservation.

## Validation globale

Les neuf specs sont terminées lorsque les fichiers calculés alimentent tout le site, que chaque dropback évaluable est consultable, que le replay montre traces/orientation/couleur par frame et s’arrête à la pression, que les comptes match et saison concordent et que les deux entrées répondent à leur usage. Au moins cinq jeux identifiés sont contrôlés à l’œil, dont disponible → complétion et indisponible → sack. Les limitations et écarts aux chiffres scratch sont documentés. Le parcours de clone neuf est vérifié selon spec-08.
