# spec-05 — Rejeu dynamique et contrôles par frame

## Problem Statement

Le terrain illustratif ne montre ni le déplacement réel ni la différence entre disponibilité à un instant quelconque et verdict à la pression. Le coach doit revoir tous les dropbacks, y compris ceux sans pression.

## Solution

Animer les frames calculées du snap au lancer ou sack, avec trajectoires, orientation corporelle, couleur du RB à chaque frame et arrêt automatique à la première pression.

## User Stories

1. En tant que coach, je veux voir les 22 joueurs et la balle bouger à l’échelle pour comprendre l’action.
2. En tant que coach, je veux lire, mettre en pause et déplacer le curseur pour inspecter une frame.
3. En tant que coach RB, je veux les traces passées du RB et du QB pour suivre leurs routes.
4. En tant que coach, je veux des traces courtes estompées des autres joueurs pour lire leur déplacement.
5. En tant que coach, je veux une flèche d’orientation sur le QB et le RB pour distinguer orientation et mouvement.
6. En tant que coach, je veux voir le RB vert ou rouge selon les checks à l’instant affiché.
7. En tant qu’utilisateur daltonien, je veux un signe ✓/✗ en plus de la couleur pour comprendre le statut.
8. En tant que coach, je veux que la lecture s’arrête à la pression pour vérifier le verdict officiel.
9. En tant que coach, je veux identifier le défenseur le plus proche du QB à la pression pour comprendre son déclenchement.
10. En tant que coach, je veux revoir un dropback sans pression sans le confondre avec un jeu compté.
11. En tant que coach, je veux sélectionner chacun des backs présents pour vérifier ses conditions.
12. En tant qu’utilisateur, je veux une alternative textuelle et des commandes clavier pour accéder aux mesures.

## Implementation Decisions

- Terrain normalisé : attaque gauche → droite, proportions 120 × 53,3 yd, ligne de scrimmage au snap, échelle identique sur les deux axes. Afficher joueurs, équipes, QB, RB/FB et balle selon les données présentes.
- Frames sources à 10 Hz ; lecture/pause, curseur, précédent/suivant et vitesses 0,5×/1×. Une horloge commune pilote points, curseur, traces et annotations. La fin arrête la lecture ; changer de jeu annule l’ancienne lecture.
- Ouverture en pause au snap. La première traversée de la frame de pression arrête exactement à cette frame ; une reprise explicite permet d’aller jusqu’à la fin sans boucle d’arrêt. Un marqueur et un accès direct à la pression demeurent disponibles.
- Dessiner la trajectoire passée du QB et du RB sélectionné et une trace courte estompée des autres joueurs. Aucune trace ne montre des positions futures ni ne traverse un trou de tracking.
- Flèches QB et RB issues de o normalisé ; légende « orientation corporelle », jamais regard ou direction de déplacement. L’orientation ne sert pas à inventer un mouvement.
- À chaque frame, consommer les états publiés : vert + ✓ lorsque les quatre checks spatiaux passent pour un route runner, rouge + ✗ lorsqu’un échoue, gris + mention « au bloc », et état distinct « indéterminé » si les données ne permettent pas de conclure. Aucun seuil n’est recalculé côté site.
- Le panneau « mesures à la pression » conserve cinq conditions, valeurs, seuils et verdict fixé à la pression ; afficher séparément le temps courant et le statut de la frame courante. Mettre en évidence le défenseur le plus proche du QB à la pression et expliquer les distances sans attribution de couverture.
- Sans pression, le replay reste accessible et montre les checks par frame avec « aucune pression détectée → non compté ». Tracking incomplet : motif explicite, aucune interpolation métier ou extrapolation après la fin observée.
- Le match déjà chargé contient tous ses dropbacks et frames ; changer de jeu dans ce match ne déclenche pas un téléchargement par jeu. Un changement rapide de match ne laisse pas une réponse tardive remplacer la sélection courante.
- Plusieurs backs : sélection stable par identifiant ; couleur et checks propres à chaque back. Le verdict collectif ne remplace pas le verdict individuel.
- Contrôles accessibles au clavier, focus visible, pas de lecture automatique, respect des préférences de réduction des animations. Aucun catch, YAC ou trajet aérien n’est déduit du texte de résultat.

## Testing Decisions

- Frontière navigateur → bundle match → rejeu : une fixture multiframe prouve que positions et curseur évoluent, que pause les fige et que reprise conserve le bon temps.
- Tester trajectoires limitées au passé, flèches QB/RB et les états vert/rouge/gris/inconnu avec signes textuels. Inclure un passage rouge → vert → rouge pour vérifier que la couleur suit les frames et que le verdict reste fixé.
- Vérifier arrêt exact à la pression puis reprise, marqueur et panneau concordants, deux sens d’attaque, vitesse 0,5×/1×, fin et changement rapide de match.
- Vérifier jeu sans pression animé sans dénominateur, sack sans lancer, données manquantes et plusieurs backs. À la pression, couleur et verdict exporté doivent coïncider.
- Aucun test navigateur métier existant : vérifier les comportements via le navigateur ; une compilation Vite seule ne prouve pas le mouvement.

## Out of Scope

GIF/PNG exportés obligatoires, vidéo NFL, rejeu 3D, direct, catch/YAC et calcul géométrique dans le navigateur.

## Further Notes

Acceptation : tout dropback évaluable d’un match peut être animé ; mouvement, traces, orientation et statut sont synchronisés, le panneau officiel correspond à la pression. Dépendances : specs 01 et 02 ; ADR du rejeu et contrat de données.
