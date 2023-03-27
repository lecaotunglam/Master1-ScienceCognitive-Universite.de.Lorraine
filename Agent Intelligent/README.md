# Essai rapide pour faire un simulateur d'Agent Intelligent pour le cours
"Agent Intelligent" (UE803 EC1), en M1 SciCo, IDMC de l'Université de Lorraine

## Objectif
Ce programme est écrit dans un but **pédagogique**.

## Comment ça marche pour l'instant ?
- installer 'python3'
- installer Tk et Idle : (sous linux ```sudo apt install python3-tk idle3```)
- lancer par ```python3 simulation.py [options] <fichier_monde>```

Sous windows, je vous fait confiance...

### Les options du programme

- -h/--help : affiche une aide succinte sur les options
- -e/--env MazeGrid | MazeReal : choisi le type d'environnement utilisé. Par défaut, il s'agit de MazeGrid (voir ci-après)

Les autres options dépendent du type d'environnement choisi.

### MazeGrid
L'environnement est un monde **discret** (ou discontinu) décrit par des cases (appelées 'cells'). Le fichier ```<fichier_monde>``` à donner en fin de commande charge un monde particulier. Si on ne donne pas de fichier spécifique, le programme charge ```fourcell_maze.txt```

Les options qui fonctionnent dans cet environnemnt

- -o/--obs : l'agent ne perçoit pas l'**état** du système, mais l'observe, il obtient des données incomplètes => la position des murs autour de lui
- -m/--mem : l'agent dispose d'une mémoire interne rudimentaire et donc d'actions pour modifier cette mémoire interne
- --value_iteration : le simulateur peut utiliser l'algorithme *Value Iteration* pour que vous (étudiants) puissiez mieux comprendre comment cet algorithm pourrait aider à planier un déplacement dans le monde.


### MazeReal
L'environnement est monde **continu** où l'agent peut se trouver n'importe où, dans n'importe quelle direction. Le fichier ```<fichier_monde>``` à donner en fin de commande charge un monde particulier. Si on ne donne pas de fichier spécifique, le programme charge ```fourcell_maze.txt```. L'agent ne perçoit pas l'**état** du monde, mais il utilise des **capteurs** qui lui donnent une information partielle sur le monde.

Les options qui fonctionnent dans cet environnement
- -m/--mem : l'agent dispose d'une mémoire interne rudimentaire et donc d'actions pour modifier cette mémoire interne

## Oui, mais alors comment on utilise ce programme ?
Pour cela, le mieux est d'assister au cours où on vous parlera de tout ça, avec plein d'exemples.

## Documentation plus détaillée et développement
Voir le fichier "todo.org"
