
from typing import List

import numpy as np
import matplotlib.pyplot as plt
import scipy.io.wavfile as wav

from sinusoid import Sinusoid, save_sinusoids_to_npz 

def find_temporal_envelope(temporal_signal):
    """
    Cette fonction prend un signal temporel et renvoie son enveloppe temporelle
    (signal redressé et filtré par un filtre passe-bas). 
    """
    
    order = 884 # Ordre tel que le gain est de -3 dB à une fréquence normalisée de pi/1000, cf rapport.
    h = np.ones(order) / order  # Réponse impulsionnelle d'un filtre passe-bas RIF et de gain DC = 0 dB
    envelope = np.convolve(np.abs(temporal_signal), h, mode="same")

    # Correction du gain pour matcher avec le signal
    envelope *= np.max(np.abs(temporal_signal)) / np.max(envelope)

    return envelope


def find_peak_sinusoids(spectral_signal, fft_freqs, sample_rate, amplitude_threshold_ratio=0.003, deduping_threshold=3) -> list[Sinusoid]:
    """
    Cette fonction prend un signal spectral et renvoie les sinusoïdes principales
    sous forme d'objets {frequency, amplitude, phase}.
    Le signal reconstruit à partir de ces sinusoïdes est un signal normalisé en amplitude dans [-1, 1].

    Paramètres:
    spectral_signal : la TDF du signal audio
    fft_freqs : les fréquences correspondantes à chaque indice m (np.fft.fftfreq)
    sample_rate : la fréquence d'échantillonnage (Hz)
    amplitude_threshold_ratio : fraction de l'amplitude max pour retenir une raie
    deduping_threshold : le seuil de déduplication en Hz pour éviter les raies trop proches
    """

    N = len(spectral_signal)

    # D'abord on prend les raies dont l'amplitude est supérieur à un seuil
    max_amp = np.max(np.abs(spectral_signal))
    amplitude_threshold = amplitude_threshold_ratio * max_amp
    most_important_m = []
    for m in range(N//2):
        if np.abs(spectral_signal[m]) > amplitude_threshold:
            most_important_m.append(m)

    # Ensuite on déduplique les raies trop proches
    deduped_m = []
    for m in sorted(most_important_m, key=lambda m: np.abs(spectral_signal[m]), reverse=True):
        if not any(abs(fft_freqs[m] - fft_freqs[n]) < deduping_threshold for n in deduped_m):
            deduped_m.append(m)

    # Puis on crée les objets Sinusoid correspondants
    sinusoids: List[Sinusoid] = []
    for m in deduped_m:
        sinusoids.append(Sinusoid(
            frequency=fft_freqs[m],
            amplitude=2 * np.abs(spectral_signal[m]) / np.sum(np.hanning(N)),
            phase=np.angle(spectral_signal[m]),
        ))

    sinusoids.sort(key=lambda s: s.frequency)

    # On reconstruit le signal pour pouvoir normaliser en amplitude dans [-1, 1]
    t = np.arange(N) / sample_rate
    reconstructed_spectral_signal = np.zeros(N)
    for s in sinusoids:
        reconstructed_spectral_signal += s.amplitude * np.cos(2 * np.pi * s.frequency * t + s.phase)
    peak = np.max(np.abs(reconstructed_spectral_signal))
    for s in sinusoids:
        s.amplitude /= peak

    return sinusoids

def main():
    sample_rate, temporal_signal = wav.read("sounds/note_guitare_lad.wav")
    N = len(temporal_signal)

    # Fenêtrage du signal
    windowed_signal = temporal_signal * np.hanning(N)

    # Calcul de la transformée de Fourier
    spectral_signal = np.fft.fft(windowed_signal)
    fft_freqs = np.fft.fftfreq(N, d=1/sample_rate)

    # Affichage du signal audio et de sa transformée
    # plt.subplot(2, 1, 1)
    # plt.plot(np.linspace(0, N / sample_rate, N), temporal_signal)
    # plt.title("Signal audio")
    # plt.xlabel("Temps (s)")
    # plt.ylabel("Amplitude")

    # plt.subplot(2, 1, 2)
    # plt.plot(fft_freqs[:N//2], np.abs(spectral_signal[:N//2]))
    # plt.loglog()
    # plt.title("Transformée de Fourier")
    # plt.xlabel("Fréquence (Hz)")
    # plt.ylabel("Amplitude")

    # Récupération des sinusoïdes principales
    sinusoids = find_peak_sinusoids(spectral_signal, fft_freqs, sample_rate)
    print(f"Il y a {len(sinusoids)} sinusoïdes principales.")

    # Sauvegarde des sinusoïdes principales dans un fichier numpy .npz
    save_sinusoids_to_npz(sinusoids, sample_rate)

    # Récupération de l'enveloppe temporelle du signal audio
    envelope = find_temporal_envelope(temporal_signal)

    # Sauvegarde de l'enveloppe temporelle dans un fichier numpy .npz
    np.savez("parameters/envelope.npz", envelope=envelope)

if __name__ == "__main__":
    main()
