import os
import numpy as np

from dataclasses import dataclass

@dataclass
class Sinusoid:
    frequency: float
    amplitude: float
    phase: float

def save_sinusoids_to_npz(sinusoids: list[Sinusoid], sample_rate: int, filename="parameters/sinusoids.npz"):
    """
    Sauvegarde les sinusoïdes dans un fichier numpy .npz
    """

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    np.savez(filename, 
            frequencies=np.array([s.frequency for s in sinusoids]),
            amplitudes=np.array([s.amplitude for s in sinusoids]),
            phases=np.array([s.phase for s in sinusoids]),
            sample_rate=sample_rate)

def load_sinusoids_from_npz(filename="parameters/sinusoids.npz") -> tuple[list[Sinusoid], int]:
    """
    Charge les sinusoïdes depuis un fichier numpy .npz
    """

    data = np.load(filename)
    frequencies = data["frequencies"]
    amplitudes = data["amplitudes"]
    phases = data["phases"]
    sample_rate = int(data["sample_rate"])

    sinusoids = [Sinusoid(frequency=f, amplitude=a, phase=p) for f, a, p in zip(frequencies, amplitudes, phases)]
    return sinusoids, sample_rate