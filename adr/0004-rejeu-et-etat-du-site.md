---
status: accepted
date: 2026-10-21
---

# ADR-0004 — Rejeu SVG et séparation de l’état de navigation

Le site a deux entrées : Coach et Broadcaster. Nous séparons le chargement des données, la sélection métier et l’horloge du rejeu pour que les filtres, les réponses asynchrones et la lecture ne puissent pas modifier le verdict calculé.

## Modules et interfaces

- **Données** : `loadCatalog(signal)`, `loadSeason(signal)`, `loadGame(gameId, signal)` renvoient des documents contrôlés, ou une erreur structurée. Le module possède manifeste, génération, chemins et cache ; les écrans n’appellent pas directement fetch.
- **Navigation** : possède dashboard, vue coach, gameId, playId, nflId et filtre de liste. L’URL en query parameters et l’historique du navigateur restaurent ces choix sur un hébergement statique sans réécriture de routes.
- **Rejeu** : reçoit un jeu du bundle et un back sélectionné ; possède seulement frame, état lecture et vitesse. Il émet un changement de frame, sans modifier les données métier.

Ces noms décrivent l’interface cible à implémenter ; les signatures JSDoc et les erreurs sont définies au lot de contrat. Les données d’un match précédent ne peuvent pas apparaître sous un nouveau gameId : annuler la requête précédente et vérifier l’identité de la réponse avant adoption.

## Terrain et lecture

Le SVG utilise un repère 120 × 53,3 yd avec attaque vers +x, puis inverse l’axe vertical pour le rendu écran. Pour une orientation o, le vecteur terrain est (sin(o), cos(o)) ; la projection applique l’inversion d’axe au vecteur comme aux positions. La balle et les joueurs absents restent absents ; la ligne de scrimmage vient du calcul.

L’ouverture d’un jeu affiche le snap en pause. Une horloge requestAnimationFrame avance selon le temps écoulé × vitesse, puis sélectionne une frame source à 10 Hz. La pause annule la boucle ; les vitesses obligatoires sont 0,5× et 1×. Les traces utilisent seulement les positions passées du jeu courant, longues pour QB/RB, courtes pour les autres. Le changement de jeu efface l’horloge et les traces.

Les états par frame pilotent vert/rouge/gris avec ✓/✗ et un libellé d’inconnue. Le panneau à la pression reste attaché à sa frame et à ses valeurs fixes. Lors d’une lecture qui franchit la pression depuis une frame antérieure, s’arrêter exactement dessus ; une reprise explicite peut poursuivre après cette pause jusqu’à la fin. Pas de nouvelle pause automatique en restant ou en repartant de la même frame ; un retour avant pression réarme l’arrêt.

Tous les dropbacks sont consultables, y compris sans pression ou avec RB au bloc. Le filtre initial retient les jeux pressurés avec RB en route ; le changement de filtre révèle les autres sans leur attribuer un n éligible.

## Navigation métier

Coach : match → play by play, résumé RB du match ou tableaux saison RB/attaque. Broadcaster : « Best safety valves », classement ligue saison uniquement, sans composant de rejeu ni carte par jeu. L’accès des scouts/front offices se fait par les tableaux saison du Coach ; il ne crée pas une troisième entrée à livrer.

Une bibliothèque globale d’état et un moteur de jeu ajouteraient des concepts à partager sans nécessité actuelle. État React local/reducer, SVG existant et un seul client de données suffisent ; la conservation des comportements sera testée sur le navigateur, indépendamment du découpage interne des composants.
