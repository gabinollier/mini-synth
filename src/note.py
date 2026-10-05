from dataclasses import dataclass
from enum import Enum

class Note(Enum):
    """
    Un enum qui représente les 12 notes de musique.
    "D" signifie Dièse et "b" signifie bémol.
    """
    Do = 0
    DoD = Reb = 1
    Re = 2
    ReD = Mib = 3
    Mi = 4
    Fa = 5
    FaD = Solb = 6
    Sol = 7
    SolD = Lab = 8
    La = 9
    LaD = Sib = 10
    Si = 11



