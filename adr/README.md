# Architecture et coordination — RB Lifeline

Ce dossier fixe les choix techniques à implémenter et les règles de travail communes. Il ne signifie pas que le pipeline ou les dashboards sont déjà développés. État observé le 21 octobre 2026 : environnement Python prêt, template React/Vite avec données fictives, aucun pipeline métier livré.

## Lire avant de développer

1. [Description du produit](../rb_lifeline.md) et [index des specs](../spec/README.md) : comportement attendu et périmètre POC.
2. [Vocabulaire](../GLOSSARY.md) : état courant, verdict à la pression, résumé match et classement saison.
3. [ADR-0001](0001-stack-et-calcul-hors-ligne.md) : stack et organisation du code.
4. [CONTRACTS](CONTRACTS.md) : interface commune des exports et du rejeu.
5. [IMPLEMENTATION](IMPLEMENTATION.md) : lots, responsabilités, séquence et preuves attendues.

## Décisions

| ADR | Décision | Conséquence pour l’équipe |
| --- | --- | --- |
| [0001](0001-stack-et-calcul-hors-ligne.md) | Python hors ligne + React/Vite statique | Une seule implémentation des métriques, aucun backend à coordonner |
| [0002](0002-contrat-json-et-publication.md) | Contrat JSON versionné, un bundle par match | Producteur et consommateurs avancent avec les mêmes fixtures |
| [0003](0003-unites-de-comptage-et-evaluateur.md) | Évaluateur commun, granularités explicites | Couleur à la pression = verdict ; sommes match = saison |
| [0004](0004-rejeu-et-etat-du-site.md) | Rejeu SVG, état isolé, deux entrées | Le classement Broadcaster ne dépend pas du rejeu |

Ces décisions constituent la référence technique du POC. Les commandes et fichiers annoncés dans le plan sont **à créer**, sauf ceux signalés comme existants. Les tests de documentation ne valent pas validation du produit.

## Maintenir la synchronisation

Le besoin courant est défini par la description produit ; les specs doivent le refléter. Les ADR expliquent les choix, et CONTRACTS fixe les noms/types utilisés entre développeurs. En cas de divergence, ouvrir un changement explicite et mettre à jour les documents et tests concernés dans la même modification, au lieu de corriger un seul consommateur.

Avant d’implémenter ou modifier une interface, lire CONTRACTS ; avant de répartir ou intégrer du travail, lire IMPLEMENTATION. Un changement de métrique touche l’évaluateur, ses fixtures et les agrégats ; un changement de contrat touche producteur, client et fixtures partagées ensemble. Un changement de périmètre touche d’abord les specs.
