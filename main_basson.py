import os

import matplotlib.pyplot as plt
import numpy as np
import scipy.io.wavfile as wav

def computeBandStopFilter(f0, f1, N, fe):
    w1 = 2*np.pi*f1/fe
    n = np.arange(-N//2, N//2+1)

    # Réponse impulsionnelle du filtre passe-bas
    h_pb = np.empty(N+1)
    h_pb[:N//2] = np.sin(n[:N//2] * w1) / (n[:N//2] * np.pi)
    h_pb[-N//2:] = np.sin(n[-N//2:] * w1) / (n[-N//2:] * np.pi)
    h_pb[N//2] = w1 / np.pi

    # Fenêtre de hamming
    window = np.hamming(N+1)

    # Filtre passe-base
    h = h_pb * window
    h /= np.sum(h) # Normalisation du filtre

    # Transformation vers filtre coupe-bande
    dirac = np.zeros(N+1)
    dirac[N//2] = 1
    w0 = 2*np.pi*f0/fe

    h_cb = dirac - 2*h*np.cos(w0*n)
    return h_cb

def show_graphs(f0, f1, N, fe):
    h = computeBandStopFilter(f0, f1, N, fe)

    n = np.arange(-N//2, N//2+1)

    # Réponse impulsionnelle
    plt.stem(n, h)
    plt.xlabel("n")
    plt.ylabel("h[n]")
    plt.title("Réponse impulsionnelle du filtre coupe-bande")
    plt.grid()
    plt.show()

    # Réponse en fréquence
    nb_points = 4096
    H = np.fft.fft(h, nb_points)
    freqs = np.fft.fftfreq(nb_points, d=1/fe)

    plt.plot(freqs[:nb_points//2], np.abs(H)[:nb_points//2])
    plt.xlabel("Fréquence (Hz)")
    plt.ylabel("Amplitude de la réponse en fréquence")
    plt.loglog()
    plt.grid()
    plt.show()

    plt.plot(freqs[:nb_points//2], np.angle(H)[:nb_points//2])
    plt.xlabel("Fréquence (Hz)")
    plt.ylabel("Phase de la réponse en fréquence (rad)")
    plt.grid()
    plt.show()

    # Sinusoide de 1000 Hz
    duration = 2
    t = np.arange(0, duration, 1/fe)
    sinusoid = np.sin(2*np.pi*f0*t)

    response = np.convolve(sinusoid, h, mode="same")

    plt.figure()
    plt.plot(t, sinusoid, label="Sinusoïde en entrée")
    plt.plot(t, response, label="Réponse")
    plt.legend()
    plt.grid()
    plt.show()

def bassoon_treatment(temporal_signal, fe, h):
    N = len(temporal_signal)
    t = np.arange(N) / fe
    spectral_signal = np.fft.fft(temporal_signal, N)
    freqs = np.fft.fftfreq(N, d=1/fe)

    plt.subplot(2, 2, 1)
    plt.plot(t, temporal_signal)
    plt.title("Signal audio")
    plt.xlabel("Temps (s)")
    plt.ylabel("Amplitude")

    plt.subplot(2, 2, 2)
    plt.plot(freqs[1:N//2], np.abs(spectral_signal[1:N//2]))
    plt.loglog()
    plt.title("Transformée de Fourier")
    plt.xlabel("Fréquence (Hz)")
    plt.ylabel("Amplitude")

    treated_signal = np.convolve(temporal_signal, h, mode="same")
    treated_spectral_signal = np.fft.fft(treated_signal, N)

    plt.subplot(2, 2, 3)
    plt.plot(t, treated_signal)
    plt.title("Signal audio filtré")
    plt.xlabel("Temps (s)")
    plt.ylabel("Amplitude")

    plt.subplot(2, 2, 4)
    plt.plot(freqs[1:N//2], np.abs(treated_spectral_signal[1:N//2]))
    plt.loglog()
    plt.title("Transformée de Fourier du signal filtré")
    plt.xlabel("Fréquence (Hz)")
    plt.ylabel("Amplitude")

    plt.show()

    # Enregistrement de la note filtrée
    os.makedirs("sounds/outputs", exist_ok=True)
    output_path = "sounds/outputs/note_basson_filtre.wav"

    output_signal = treated_signal.astype(np.float64)

    # Normalisation du signal en float32
    peak = np.max(np.abs(output_signal))
    if peak > 0:
        output_signal /= peak

    wav.write(output_path, fe, output_signal.astype(np.float32))
    print(f"Signal filtré sauvegardé dans {output_path}.")

    return treated_signal

def main():
    sample_rate, temporal_signal = wav.read("sounds/note_basson_plus_sinus_1000_hz.wav")
    f0 = 1000
    f1 = 40
    N = 6000
    show_graphs(f0, f1, N, sample_rate)
    h = computeBandStopFilter(f0, f1, N, sample_rate)
    bassoon_treatment(temporal_signal, sample_rate, h)

if __name__ == "__main__":
    main()
