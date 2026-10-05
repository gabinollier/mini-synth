import os
import numpy as np
import scipy.io.wavfile as wav

from sinusoid import Sinusoid, load_sinusoids_from_npz

def main():
    sinusoids, sample_rate = load_sinusoids_from_npz("parameters/sinusoids.npz")
    envelope = np.load("parameters/envelope.npz")["envelope"]

    # Reconstruction du signal à partir des sinusoïdes principales
    N = len(envelope) # même durée que le son original
    t = np.arange(N) / sample_rate  # axe temporel en secondes
    reconstructed_signal = np.zeros(N)
    for sinusoid in sinusoids:
        reconstructed_signal += sinusoid.amplitude * np.cos(2 * np.pi * sinusoid.frequency * t + sinusoid.phase)

     # Application de l'enveloppe temporelle
    reconstructed_signal *= envelope 

    os.makedirs("sounds/outputs", exist_ok=True)
    wav.write("sounds/outputs/test.wav", sample_rate, reconstructed_signal.astype(np.int16))

if __name__ == "__main__":
    main()