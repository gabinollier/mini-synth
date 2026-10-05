import os
from typing import List

import numpy as np
import scipy.io.wavfile as wav

from note import Note
from cell import Cell

class Synthetiser:
    """
    Le synthétiseur gère la synthèse sonore d'un signal à partir des paralètres sauvegardées pendant l'analyse
    de la note d'origine.
    """

    def __init__(self, sample_rate, sinusoids_lad466, envelope):
        self.sample_rate = sample_rate
        self.sinusoids_lad466 = sinusoids_lad466
        self.envelope = envelope
        self.note_lenght = len(self.envelope) / self.sample_rate # durée d'une note en secondes

    def synthetize(self, note: Note, octave: int):
        """ 
        Synthétise une note unique et renvoie le signal audio discrétisé.
        """
        # Reconstruction du signal à partir des sinusoïdes principales
        N = len(self.envelope) # même durée que le son original
        t = np.arange(N) / self.sample_rate  # axe temporel en secondes
        synthetised_signal = np.zeros(N)
        for sinusoid in self.sinusoids_lad466:
            # Ici on considère que le La# d'origine est à la 4ème octave (système international). En système français c'est plutôt la 3ème mais ça change pas grand chose.
            note_index_delta = (note.value + octave*12) - (Note.LaD.value + 4*12) 
            frequency = sinusoid.frequency * 2**(note_index_delta/12)
            synthetised_signal += sinusoid.amplitude * np.cos(2 * np.pi * frequency * t + sinusoid.phase)
    
        # Application de l'enveloppe temporelle
        synthetised_signal *= self.envelope 

        return synthetised_signal

    def synthesize(self, cells: List[Cell]):
        """
        Synthétise une liste de notes et renvoie le signal audio discrétisé.
        """
        total_duration = max([c.start for c in cells]) + self.note_lenght
        N = int(total_duration * self.sample_rate) # nombre d'échantillons total
        synthetised_signal = np.zeros(N)

        for cell in cells:
            start_sample = int(cell.start * self.sample_rate)
            end_sample = start_sample + int(self.note_lenght * self.sample_rate)
            synthetised_signal[start_sample:end_sample] += self.synthetize(cell.note, cell.octave)

        return synthetised_signal



    
