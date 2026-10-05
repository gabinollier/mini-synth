
from typing import List

from note import Note
from cell import Cell


class Sequencer:
    """
    Le séquenceur permet de créer une mélodie avec différentes notes suivant un certain rythme.
    Il appelle le synthétiseur pour synthétiser les notes et créer le fichier audio final.
    """
    def __init__(self, bpm: int):
        self.bpm = bpm # beats par minute
        self.bps = bpm/60 # beats par seconde
        self.cells: List[Cell] = [] # représente la mélodie à synthétiser


    def add_note(self, note: Note, octave: int, position: float):
        """
        Ajoute une note à la mélodie.
        `position` indique le début de la note en temps (=beats) depuis le début de la mélodie.
        """
        start = position / (self.bpm/60)
        cell = Cell(start=start, note=note, octave=octave)
        self.cells.append(cell)


