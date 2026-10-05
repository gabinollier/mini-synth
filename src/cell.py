from dataclasses import dataclass

from note import Note

@dataclass
class Cell:
    """
    Une cellule de mélodie, utilisée par le séquenceur et le synthétiseur pour représenter une note.
    `start` indique le début de la note en secondes depuis le début de la mélodie.
    """
    start: float
    note: Note
    octave: int