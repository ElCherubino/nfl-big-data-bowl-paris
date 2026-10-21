# Contrat technique v1 — Producteur Python et consommateurs web

Ce document fixe les noms, types et invariants du contrat à implémenter. Les formes JSON Schema correspondantes et les fixtures communes sont le premier livrable du lot A, relu par B et C avant de brancher leurs modules. Tout changement de forme passe par cette interface commune. Voir [ADR-0002](0002-contrat-json-et-publication.md).

## 1. Conventions

| Élément | Convention |
| --- | --- |
| Champs JSON | camelCase ; noms et états indépendants de la langue affichée |
| Identifiants | gameId, playId, nflId : chaînes ; frameId : entier source |
| Clé d’un jeu | gameId + playId ; aucune jointure sur playId seul |
| Équipes | Codes des sources normalisés, jamais noms saisis à la main |
| Valeur absente | null avec motif dans reason ou diagnostics ; jamais 0 par défaut |
| Distances / temps / angles | Yards / secondes depuis snap / degrés ; orientation [0,360[ |
| Taux | Nombres [0,1], affichés en pourcentages par le site |
| Écart de taux | Fraction signée ; multiplier par 100 pour afficher des points de pourcentage |
| Percentile | [0,100], pas une fraction ; null si non calculable |
| Intervalles | {low, high, level: 0.95, method: "bootstrap_percentile", replicates}, ou null |
| Ordre | Frames croissantes ; identités stables ; rangs calculés dans le pipeline |
| Champs supplémentaires | Ajouts optionnels compatibles autorisés ; le client ignore ce qu’il ne consomme pas |

Les métriques utilisent la forme `{value, numerator, denominator, unknownCount}` : value vaut numerator/denominator si denominator > 0, sinon null. numerator, denominator et unknownCount sont des entiers ≥ 0. Une valeur nulle a un reason explicite dans l’objet porteur. `unknownCount` représente les opportunités retirées de ce dénominateur, pas toutes les lignes manquantes du jeu.

## 2. Publication et catalogue

### Manifeste public : manifest.json

| Champ requis | Type / sens |
| --- | --- |
| schemaVersion | "1.0.0" pour le premier contrat |
| generationId | Identifiant stable de la publication cohérente |
| generatedAt | Date ISO 8601 UTC |
| calculationVersion | Version de la logique de calcul, distincte du schéma |
| sourceFingerprint | Empreinte des fichiers fournis et de leurs identifiants de version |
| period | {season: 2021, weeks: [1,2,3,4,5,6,7,8], label} |
| parameters | pressureRadiusYd, openDistanceYd, maxQbDistanceYd, minLosProgressYd, maxFacingAngleDeg, includeFb, minSeasonN, shrinkageK, bootstrapReplicates, randomSeed |
| resources | {games, seasonRb, seasonTeam, analysis, quality} : chemins relatifs depuis ce manifeste, vers la même génération |
| counts | gameCount, playCount, replayablePlayCount, pressuredPlayCount, rbObservationCount, excludedObservationCount |

Valeurs initiales de parameters : 2 ; 2.5 ; 15 ; −1 ; 90 ; true ; 20 ; 20 ; 2000 ; 20261021. Les opérateurs inclusif/strict sont ceux de la définition métier, pas déduits des noms de paramètres.

Tous les autres documents ont l’enveloppe `{schemaVersion, generationId, data}`. Chaque référence de ressource est relative au manifeste, même lorsqu’elle vient du catalogue. Le client résout les chemins avec l’URL du manifeste et refuse les URL externes ou les chemins sortant de la racine de données.

### games.json : data = tableau de matchs

Ligne : gameId, season, week, gameDate, homeTeam, awayTeam, score, playCount, pressuredRoutePlayCount, gameResource. `score` vaut `{home, away}` seulement si un résultat final fiable est disponible, sinon null avec scoreReason. Ne pas extrapoler le score final du dernier score avant snap. gameResource désigne `generations/<generationId>/game_<gameId>.json`.

## 3. Bundle de match : game_<gameId>.json

`data` contient gameId, players, plays, rbSummary. players est un dictionnaire par nflId : displayName, officialPosition et team. Une appartenance variable ou manquante est résolue depuis le jeu/tracking, sans annuaire d’effectif actuel.

### Jeu : élément de plays

| Champ requis | Type / sens |
| --- | --- |
| playId | Chaîne, unique dans le match |
| possessionTeam, defensiveTeam | Codes d’équipe |
| quarter, gameClock, down, yardsToGo | Contexte source ; null si absent |
| description, passResult, playResult | Description et résultats fournis ; pas de YAC inventé |
| context | coverageFamily, coverageScheme, blitz : bool ou null, passRusherCount |
| participants | Tableau {nflId, role} ; les rôles sont normalisés par Python |
| events | snapFrameId, pressureFrameId, endFrameId : entiers ou null ; endKind : throw/sack/scramble/unknown |
| pressure | {status, timeS, defenderId, distanceYd, reason}, status = detected/none/unknown |
| losX | Coordonnée x normalisée de la balle au snap, ou null |
| collectiveVerdict | available/unavailable/not_applicable/unknown |
| target | {status, nflId, reason}, status = matched/unmatched/ambiguous/not_applicable |
| observations | Tableau des observations fixes des RB/FB du jeu |
| frames | Tableau de frames du snap à la fin ; vide si non rejouable |
| quality | {replayable, countable, reasons} ; reasons est un tableau de codes |

Un jeu sans pression conserve frames et états courants, mais pressureFrameId est null et ses observations ne sont pas comptées. Le badge du jeu est une présentation de ces champs, pas un nouveau résultat calculé dans React.

### Frame et participants mobiles

Frame : `{frameId, timeS, entities, rbStates}`. `entities` contient `{nflId, team, x, y, o}` pour les positions réellement observées. La balle porte nflId null, team "football" et o null. Le QB est identifié par participants et le rôle passer ; la balle n’est pas un joueur fictif ajouté à players. x/y sont normalisés et arrondis à 0,1 yd à l’export ; o est normalisée en degrés. Un participant absent de la frame est absent du tableau, sans report de sa dernière position.

`rbStates` contient un objet par back concerné : `{nflId, status, checks}`. status vaut available/unavailable/blocking/unknown. Il vient du calcul Python à cette frame. Les quatre conditions spatiales sont évaluées même sans pression ; le rôle de route est la cinquième condition du verdict. Un back au bloc est toujours blocking, indépendamment de l’ouverture géométrique.

### Checks et observation à la pression

`checks` contient cinq champs : routeRunner, open, inRange, pastLine, facingQb. Chaque champ est `{passed, value, reason}` ; passed est bool ou null, value est bool pour routeRunner, yards pour open/inRange/pastLine, degrés d’écart absolu pour facingQb. Les seuils et unités sont définis par le manifeste et ce contrat ; l’interface les affiche sans les deviner.

Observation : `{nflId, status, counted, exclusionReason, pressureFrameId, checks, targetStatus, targeted, completedWhenTargeted}`. status reprend l’état du back à la pression, ou unknown si cet instant manque ; les backs au bloc restent blocking. counted est vrai seulement pour un back en route, pression identifiée, verdict déterminé et qualité suffisante. targeted est bool ou null ; completedWhenTargeted est bool uniquement si le joueur est effectivement ciblé sur une passe, sinon null. Les motifs distinguent absence d’opportunité et donnée inconnue.

Les valeurs de checks à la pression gardent la précision de calcul ; l’UI choisit les décimales de présentation. Le consommateur doit utiliser passed et status, même si des coordonnées arrondies suggèrent une valeur proche d’un seuil.

## 4. Comptes match et saison

### Objet de comptes commun

| Champ | Invariant |
| --- | --- |
| pressuredRoutePlays | Toutes les opportunités pressurées du joueur ou de l’attaque |
| evaluatedPlays | Opportunités avec verdict déterminé, ≤ pressuredRoutePlays |
| excludedUnknownPlays | pressuredRoutePlays − evaluatedPlays |
| availablePlays | ≤ evaluatedPlays ; état available au moment de pression |
| availability | Métrique avec numerator = availablePlays, denominator = evaluatedPlays, unknownCount = excludedUnknownPlays |
| targetedWhenAvailable | Métrique de ciblage parmi les opportunités disponibles dont la cible est connue ; inclut les non-passes connues à zéro |
| completionWhenTargeted | Métrique parmi les passes reconnues vers ce joueur/back |

Dans un résumé individuel, un jeu à deux backs compte pour chacun dans ses propres comptes. Dans un résumé d’attaque, un jeu compte une fois. Les métriques de cible collective et individuelle sont distinctes, conformément aux specs statistiques.

### rbSummary d’un match

Tableau de lignes : nflId, team, counts, playIds. Inclure les RB/FB des deux équipes ayant au moins une opportunité de route pressurée, même si toutes leurs observations sont inconnues. Dans ce cas evaluatedPlays vaut 0, availability.value vaut null et les exclusions sont visibles. Aucun champ rank, shrunkRate, percentile ou interval n’est autorisé sur ces lignes.

### season_rb.json

`data = {period, reference, rows}`. reference contient metricUnit "player_play", leagueAvailability, shrinkageK, minN et cohortSize. Ligne : nflId, displayName, position, teams (tableau des équipes observées), counts, rawRate, shrunkRate, interval, eligible, rank, percentile, gameIds.

rawRate est la valeur de counts.availability. eligible signifie evaluatedPlays ≥ minN. shrunkRate est calculé pour les lignes évaluables, mais rank et percentile restent null sous le minimum ; la vue coach grise ces lignes et Broadcaster les exclut. `interval` porte sur le taux brut et est étiqueté comme tel. La référence et les rangs portent sur la cohorte ligue, même quand l’utilisateur masque des lignes par équipe.

Les comptes d’un joueur transféré sont regroupés par identité : teams contient toutes ses équipes de la période. Le filtre équipe sélectionne cette ligne saison complète, dont le périmètre reste étiqueté ; il ne simule pas un sous-classement recalculé.

### season_team.json

Même enveloppe de data ; référence metricUnit "team_play". Ligne : team, counts, rawRate, shrunkRate, interval, eligible, rank et gameIds. Ne pas construire cette ligne en additionnant les comptes de joueurs sur les jeux multi-RB.

### analysis.json et quality.json

analysis.data contient comparisonRows et sensitivityRows. Une comparisonRow contient id, scope (league ou stratum), coverageFamily et blitz (null si non applicables), populationLabel, availableGroup et unavailableGroup. Chaque groupe contient playCount, sackRate, rbTargetRate et rbCompletionRate, avec la forme métrique commune. differences contient sackRate, rbTargetRate et rbCompletionRate ; chaque entrée porte value, interval, interpretation (descriptive/inconclusive/directional) et reason. La différence de sack rate est indisponible moins disponible ; les deux autres différences sont disponible moins indisponible. Une sensitivityRow contient variantId, changedParameter, parameterValue et comparisonRows de la variante. Aucun libellé affiché ne change le sens d’un écart.

quality.data contient inputCounts, exclusions, targetMatching, pressureProxy et prototypeDifferences. inputCounts reprend les comptes par table ; exclusions est une liste {reason, playCount, observationCount}. targetMatching donne thrownPassCount, matchedCount, unmatchedCount, ambiguousCount et matchRate (métrique commune). pressureProxy contient evaluatedPlayCount, truePositive, falsePositive, trueNegative, falseNegative, precision, recall et medianTimeToPressureS ; precision/recall utilisent la forme métrique, avec null si non estimables. prototypeDifferences est une liste {metric, referenceValue, recalculatedValue, explanation}, où une explication encore inconnue est signalée explicitement. Les schémas matérialisent ces formes au jalon J0 sans que chaque consommateur les réinvente.

## 5. Invariants de validation communs

1. Chaque fichier est de la génération et de la majeure attendues ; chaque ressource et référence de joueur/jeu se résout.
2. Tous les dropbacks chargés apparaissent dans leur match ; un échec de calcul ne supprime pas l’action du catalogue.
3. Les frames sont ordonnées ; la pression détectée se situe après snap et au plus tard à la fin ; son temps correspond à la frame source.
4. Pour toute observation counted, le flag à pressureFrameId égale le status de l’observation fixe, et ses checks portent sur le même joueur.
5. Les comptes match individuels sommés reproduisent la saison par nflId pour disponibles, évaluables, opportunités, inconnues et cibles. Les comptes équipe se conservent depuis les jeux uniques.
6. Le classement ne change pas lorsqu’on filtre visuellement les lignes. Un joueur sous minN n’obtient pas de rang Broadcaster.
7. Aucune valeur non finie ; null explicites et raisons exploitables ; fractions dans leur domaine ; identifiants uniques à leur granularité.

## 6. Erreurs du client de données

Le module renvoie une erreur avec code, message utilisateur et ressource concernée : NETWORK_ERROR, NOT_FOUND, UNSUPPORTED_SCHEMA, GENERATION_MISMATCH, INVALID_DOCUMENT. Aucune erreur n’est convertie en tableaux fictifs. Le client accepte AbortSignal pour ignorer les sélections abandonnées et ne met en cache que les documents validés.

Résultats des méthodes publiques : loadCatalog retourne {manifest, games}, loadSeason retourne {manifest, rb, teams, analysis}, loadGame retourne le data du bundle vérifié. La dernière méthode exige un gameId présent dans le catalogue chargé. Les objets rb/teams/analysis sont les data déballés de leurs documents, pas leurs enveloppes ; manifest conserve la génération pour l’affichage. Le client partage une instance de manifeste et borne le cache à deux bundles de match.

## 7. Fixtures communes à créer au jalon J0

Une publication de test minimale contient : un jeu disponible avec complétion RB, un jeu indisponible avec sack, un jeu sans pression, un back au bloc, un jeu multi-back, une cible inconnue, une observation indéterminée et une attaque vers la gauche. Elle couvre deux matchs pour tester la conservation et une cohorte incluant un joueur sous le minimum.

Ces fixtures sont nommées et identifiées comme synthétiques et restent dans les tests, sans fallback du site. Une petite publication réelle vérifiée sert ensuite au test d’intégration et à la démo. Les schémas valident les deux publications avec les mêmes règles.
