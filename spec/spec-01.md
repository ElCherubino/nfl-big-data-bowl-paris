# spec-01 — Données NFL et contrat de publication

## Problem Statement

Le template affiche des équipes, joueurs et statistiques fictifs. Sans données fiables et clés communes, les utilisateurs ne peuvent ni sélectionner un vrai jeu ni vérifier les chiffres sur le terrain.

## Solution

Construire un chargement Python reproductible des fichiers fournis et un contrat de publication partagé entre calculs et site. Chaque résultat conserve son origine, son état de validité et ses unités.

## User Stories

1. En tant que développeur, je veux charger les fichiers fournis pour exécuter le projet sans service externe.
2. En tant qu’analyste, je veux identifier chaque jeu sans ambiguïté pour éviter les jointures entre matchs.
3. En tant que coach, je veux sélectionner une équipe et ses vrais matchs pour retrouver les actions pertinentes.
4. En tant que scout, je veux retrouver un joueur par identifiant pour distinguer les homonymes.
5. En tant qu’analyste, je veux connaître les données manquantes pour comprendre les exclusions.
6. En tant qu’utilisateur, je veux distinguer indisponible et zéro pour interpréter correctement un résultat.
7. En tant que développeur frontend, je veux des objets documentés pour afficher les calculs sans les réimplémenter.
8. En tant que coach, je veux voir saison et semaines disponibles pour connaître la portée de l’analyse.
9. En tant que développeur, je veux charger les trajectoires d’un seul match pour limiter mémoire et téléchargement.
10. En tant qu’évaluateur, je veux connaître les paramètres et la version du calcul pour reproduire le rendu.

## Implementation Decisions

- Sources : tables matchs, jeux, joueurs, scouting PFF et tracking par match. Le répertoire de données est configurable ; son absence produit une instruction d’initialisation du sous-module, pas des données de remplacement.
- Clés uniques : gameId pour les matchs, gameId/playId pour les jeux, nflId pour les joueurs, gameId/playId/nflId pour le scouting, et ces trois identifiants plus frameId pour le tracking joueur. La balle est distinguée par son équipe et son identifiant joueur absent.
- Détecter doublons de clés et colonnes requises absentes avant le calcul. Ne pas supprimer silencieusement un doublon contradictoire. Contrôler les jointures pour éviter une multiplication de lignes.
- Conserver une ligne de diagnostic par jeu, y compris hors population du score : pas de RB en route, pas de pression détectée, événements absents, tracking incomplet ou valide. Une exclusion statistique n’efface pas le jeu source.
- Charger le tracking progressivement par match. Conserver les coordonnées sources pour audit et produire les coordonnées normalisées pour les mesures et le rendu.
- Le contrat publie un manifeste, un catalogue de matchs, les tables saison RB et équipes, puis un bundle par match contenant tous ses dropbacks, les observations RB, le tableau RB du match et leurs frames. Les noms de ressources, champs et versions sont définis par l’ADR du contrat de données. Les comparaisons et diagnostics sont référencés par le manifeste. Le contrat distingue ces objets. Les identifiants sont sérialisés de façon uniforme comme chaînes ; valeurs manquantes JSON null avec motif ; pas de NaN ou Infinity.
- Une trajectoire contient frameId, temps depuis snap, événements, balle et joueurs identifiés avec équipe, rôle, position, coordonnées et orientation o. Les positions publiées sont arrondies à 0,1 yd après les calculs. Chaque frame contient les quatre checks spatiaux du RB et leur résultat calculé ; le résumé référence les frames snap/pression/fin et les observations RB. Le navigateur consomme ces flags sans réévaluer les seuils sur les positions arrondies.
- Le manifeste contient version de schéma, date de génération, empreinte des sources, paramètres, saison, semaines, décomptes, motifs d’exclusion et références des exports. Toutes les ressources d’une publication partagent le même identifiant de génération.
- Un échec interrompt la publication ; publier le manifeste seulement après validation de tous les artefacts, pour empêcher le mélange de générations. Ne pas publier les CSV bruts avec le bundle JavaScript.

## Testing Decisions

- Frontière principale : chargement de petits fichiers d’entrée → objets et exports publics. Vérifier leur contenu, pas l’ordre des appels internes.
- Tester identifiants de jeu répétés entre matchs, balle sans nflId, joueur introuvable, colonne absente, doublons et jeu sans tracking. Les comptes avant/après jointure doivent être explicables.
- Vérifier la sérialisation des inconnues et le rejet d’un schéma incompatible par le consommateur.
- Sur les données fournies, rapprocher les 122 matchs et 8 557 jeux annoncés du chargement réel ; toute différence est signalée et expliquée.
- Le dépôt dispose de diagnostics génériques d’environnement, mais pas encore de tests métier ni de contrats frontend ; créer les fixtures minimales adaptées.

## Out of Scope

Téléchargement d’autres saisons, base cloud, pipeline temps réel, authentification, modification des données sources et métriques football.

## Further Notes

Critère d’acceptation : un export validé permet de parcourir matchs et jeux avec les mêmes identifiants côté calcul et côté site, et un rapport comptabilise chaque exclusion. Dépendance : aucune.
