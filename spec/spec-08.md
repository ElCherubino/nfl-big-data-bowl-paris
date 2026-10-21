# spec-08 — Exécution reproductible et validation de la livraison

## Problem Statement

L’environnement Python et le template web existent séparément. Un équipier ou évaluateur doit pouvoir obtenir les données, produire les résultats et lancer le site final, sans confondre installation réussie et analyse validée.

## Solution

Fournir un parcours documenté de clone neuf à site utilisable, des commandes de calcul/validation et des preuves de cohérence entre données, chiffres et rejeu. Livrer le site React comme rendu final.

## User Stories

1. En tant qu’équipier, je veux installer les dépendances déclarées pour reproduire l’environnement.
2. En tant qu’équipier, je veux initialiser le sous-module de données pour charger les fichiers attendus.
3. En tant qu’analyste, je veux une commande de génération pour refaire tous les résultats.
4. En tant que développeur web, je veux lancer le site connecté pour travailler sur le vrai parcours.
5. En tant qu’évaluateur, je veux compiler le site pour vérifier qu’il est livrable.
6. En tant qu’évaluateur, je veux une preuve visible sans exécuter les calculs pour comprendre l’insight.
7. En tant qu’analyste, je veux contrôler cinq actions à l’œil pour confronter règles et positions.
8. En tant qu’utilisateur, je veux connaître les biais pour juger la portée du produit.
9. En tant que mainteneur, je veux détecter un export manquant ou périmé pour éviter une démo incohérente.
10. En tant qu’équipier, je veux que les erreurs d’installation échouent clairement pour pouvoir les corriger.
11. En tant qu’utilisateur, je veux un rendu utilisable sans clé AWS pour accéder à l’analyse locale.
12. En tant qu’évaluateur, je veux distinguer résultats recalculés et chiffres scratch pour évaluer la preuve réelle.

## Implementation Decisions

- Conserver la préparation Python isolée existante ; déclarer toute dépendance supplémentaire justifiée. Node ≥ 22.12 et npm sont les prérequis du site existant, avec installation reproductible depuis le lockfile via npm ci.
- Documenter le clone récursif ou l’initialisation du sous-module. Le guide indique les tables attendues et comment diagnostiquer les fichiers absents ; aucune donnée synthétique substituée aux sources réelles en mode produit.
- Fournir une commande Python pour générer diagnostics, mesures, statistiques, classements et ressources web. Paramètres, graine et empreintes sont consignés ; la génération se termine avec statut non nul si les validations critiques échouent.
- Faire évoluer le lanceur du projet pour démarrer le site React final, avec modes de préparation/calcul et de lancement clairement documentés. Ne pas ouvrir silencieusement le starter Streamlit en présentant cela comme le produit RB Lifeline.
- Installer les dépendances seulement lorsque nécessaire, garder les installations dans les environnements locaux et ne lancer aucun calcul lourd sans message explicite. Au lancement, détecter exports absents ou incompatibles et indiquer la commande corrective.
- Les exports JSON et trajectoires doivent être copiés ou référencés par le build web pour être effectivement servis. Distinguer leur génération locale des fixtures de test ; ne pas committer node_modules, environnements, CSV bruts ou build par accident.
- Livraison : build statique du site et ressources dérivées nécessaires, dans les limites de partage des données. Aucun hébergement public ou service AWS n’est indispensable à la définition de terminé ; documenter le lancement local et ne pas prétendre avoir publié un site sans URL vérifiée.
- Validation réelle : recalculer les effectifs et le proxy de pression puis rapprocher des chiffres de référence. Documenter tout écart ; ne pas ajuster les seuils pour retrouver une meilleure différence de sack rate.
- Contrôle manuel d’au moins cinq jeux identifiés : snap, fin, première pression, sens, distances, angle et cinq conditions. Inclure au moins un disponible → complétion, un indisponible → sack, un jeu sans pression et un back au bloc ; couvrir aussi direction opposée et multi-back si présents.
- Documenter deux cas de revue vérifiés : disponible puis completion et indisponible puis sack, si ces cas existent après recalcul ; sinon documenter l’absence et choisir des exemples sans inventer leur résultat. Conserver une trace des contrôles ; GIF et exports d’images restent optionnels hors POC.
- Le README de livraison résume utilité, utilisateur principal, méthode, résultat effectivement calculé et limites, avec commandes reproductibles. Un détail de validation peut porter les effectifs, paramètres, contrôles et divergences.
- Limites obligatoires : sélection des RB gardés au bloc, association non causale, contrôle limité couverture/blitz, proxy de pression, orientation corporelle différente du regard, cibles inconnues, petits échantillons, plus proche défenseur différent du défenseur assigné, huit semaines d’une saison, tracking arrêté peu après lancer.

## Testing Decisions

- Vérifier les deux frontières validées : petit jeu d’entrée → exports attendus ; navigateur → match → jeu → animation et mesures cohérentes. Les diagnostics génériques d’environnement restent un prérequis, pas une preuve fonctionnelle.
- Sur un environnement neuf, exécuter installation, génération, contrôles métier, compilation et lancement selon le guide. Vérifier que le build sert réellement manifeste et trajectoires sans dépendre du serveur de développement.
- Vérifier erreurs pour données absentes, schéma incompatible, export périmé et installation échouée. Le résultat doit être explicite, sans fallback à des statistiques de démonstration.
- Contrôler automatiquement l’intégrité des références entre catalogue, bundles match, observations et classements. Exiger la conservation match → saison de la spec-09, l’égalité flags à la pression/verdict et l’accès à tous les dropbacks des 122 matchs annoncés ou expliquer explicitement tout écart de qualité. Vérifier que les métriques des cartes correspondent aux exports de la même génération.
- Les cinq contrôles visuels complètent les tests automatisés ; conserver la liste des jeux et observations plutôt que déclarer une validation sans preuve.

## Out of Scope

Déploiement cloud obligatoire, nouvelle infrastructure CI complète, publication automatique, soumission au formulaire de l’événement et réutilisation de slides préfabriquées.

## Further Notes

Critère d’acceptation : un tiers suit les instructions depuis un clone neuf et accède au site alimenté par les calculs, avec parcours coach, classement broadcaster saison seul, rejeu dynamique, cinq conditions, tableaux match/saison cohérents et exemples vérifiés. Dépendances : ensemble des specs.
