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

Pour rajouter une dépendance (si besoin) :

```bash
./venv/bin/python3 -m pip install <nom-du-module>
./venv/bin/python3 -m pip freeze > requirements.txt
```