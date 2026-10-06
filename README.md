# Projet APP3

Pour créer un environnement virtuel et installer les dépendances :

```bash
python3 -m venv .venv
./venv/bin/python3 -m pip install -r requirements.txt
```

Puis, pour lancer le projet :

```bash
./venv/bin/python3 src/main_analyse.py      
./venv/bin/python3 src/main_synthese.py      
```

`main_analyse.py` analyse le signal audio et extrait les sinusoïdes principales et l'enveloppe temporelle dans les fichiers `.npz` dans le dossier `parameters`.
`main_synthese.py` permet de créer des mélodies et les enregistrer dans le dossier `sounds/outputs`.

Eventuellement, pour générer les figures du rapport :

```bash
./venv/bin/python3 src/main_figures_rapport.py
```