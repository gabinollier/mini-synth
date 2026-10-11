# Mini Synth

Ce projet fait suite à un projet scolaire au sein de l'Université de Sherbrooke. Il permet d'analyser et stocker les caractéristiques d'un son (par exemple, la note de guitare `sounds/note_guitare_lad.wav` (sinusoïdes et enveloppe) et de re-synthétiser des notes à partir de ses paramètres.

Il comprend aussi une fonctionnalité d'import de fichiers MIDI pour rejouer n'importe quelle mélodie avec le synthétiseur.

## Structure du projet

`main_analyse.py` analyse le signal audio et extrait les sinusoïdes principales et l'enveloppe temporelle dans les fichiers `.npz` dans le dossier `parameters`.
`main_synthese.py` permet de créer des mélodies et les enregistrer dans le dossier `sounds/outputs`.
`main_figures_analyse_synthese.py` permet d'exporter les graphiques en lien avec l'analyse et la synthèse.
`main_basson.py` permet de filtrer le signal du basson et d'afficher les graphiques en lien avec ce filtrage (requis par le projet scolaire)

## Get started

Pour créer un environnement virtuel et installer les dépendances :

```bash
python3 -m venv .venv
./venv/bin/python3 -m pip install -r requirements.txt
```

Puis, pour lancer le projet :

```bash
./venv/bin/python3 src/main_analyse.py      
./venv/bin/python3 src/main_synthese.py    
./venv/bin/python3 src/main_figures_analyse_synthese.py
./venv/bin/python3 src/main_basson.py  
```
