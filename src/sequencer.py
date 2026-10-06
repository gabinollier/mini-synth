
from typing import List

from note import Note
from cell import Cell





class Sequencer:
    """
    Le séquenceur permet de créer une mélodie avec différentes notes suivant un certain rythme.
    Il appelle le synthétiseur pour synthétiser les notes et créer le fichier audio final.
    """
    def __init__(self, bpm: int = 120):
        self.bpm = bpm # beats par minute
        self.bps = bpm/60 # beats par seconde
        self.cells: List[Cell] = [] # représente la mélodie à synthétiser


    def clear(self):
        """
        Vide la mélodie.
        """
        self.cells = []

    def add_note(self, note: Note, octave: int, position: float):
        """
        Ajoute une note à la mélodie.
        `position` indique le début de la note en temps (=beats) depuis le début de la mélodie.
        """
        start = position / (self.bpm/60)
        cell = Cell(start=start, note=note, octave=octave)
        self.cells.append(cell)


    def add_notes_from_midi(self, chemin_midi: str, piste: int | None = None):
        """
        Ajoute à la mélodie toutes les notes d'un fichier MIDI.
        Les positions sont converties des ticks MIDI en temps (beats), donc le
        tempo utilisé reste celui du séquenceur (`bpm`).
        `piste` permet de ne lire qu'une seule piste du fichier (par exemple
        celle de la mélodie) ; par défaut, toutes les pistes sont lues.
        Les notes de percussion (canal 10) sont ignorées.
        """

        def _lire_entier_variable(donnees: bytes, position: int):
            """
            Lit un entier à longueur variable (codage MIDI) et renvoie sa valeur
            ainsi que la position suivante dans les données.
            """
            valeur = 0
            while True:
                octet = donnees[position]
                position += 1
                valeur = (valeur << 7) | (octet & 0x7F)
                if not octet & 0x80:
                    return valeur, position


        with open(chemin_midi, "rb") as fichier:
            donnees = fichier.read()

        if donnees[0:4] != b"MThd":
            raise ValueError(f"{chemin_midi} n'est pas un fichier MIDI valide.")

        nb_pistes = int.from_bytes(donnees[10:12], "big")
        ticks_par_temps = int.from_bytes(donnees[12:14], "big")
        if ticks_par_temps >= 0x8000: # division SMPTE non supportée
            raise ValueError(f"La division de {chemin_midi} n'est pas en ticks par temps.")

        notes = [] # (tick, numéro de note MIDI)
        position = 14
        for index_piste in range(nb_pistes):
            if donnees[position:position + 4] != b"MTrk":
                raise ValueError(f"Piste {index_piste} illisible dans {chemin_midi}.")
            taille = int.from_bytes(donnees[position + 4:position + 8], "big")
            position += 8

            fin_piste = position + taille
            if piste is not None and index_piste != piste:
                position = fin_piste
                continue

            tick = 0
            statut = 0
            
            while position < fin_piste:
                delta, position = _lire_entier_variable(donnees, position)
                tick += delta
                if donnees[position] >= 0x80: # nouveau statut
                    statut = donnees[position]
                    position += 1
                type_message = statut & 0xF0
                if statut == 0xFF: # méta-événement
                    position += 1
                    taille_meta, position = _lire_entier_variable(donnees, position)
                    position += taille_meta
                    statut = 0
                elif statut in (0xF0, 0xF7): # message exclusif
                    taille_sysex, position = _lire_entier_variable(donnees, position)
                    position += taille_sysex
                    statut = 0
                elif type_message == 0x90: # note jouée
                    numero, velocite = donnees[position], donnees[position + 1]
                    position += 2
                    if velocite > 0 and statut & 0x0F != 9: # ni relâchement ni percussion
                        notes.append((tick, numero))
                elif type_message in (0x80, 0xA0, 0xB0, 0xE0):
                    position += 2
                else: # 0xC0 ou 0xD0
                    position += 1

        for tick, numero in sorted(notes):
            self.add_note(Note(numero % 12), octave=numero // 12 - 1,
                          position=tick / ticks_par_temps)
