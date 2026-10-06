"""
Génère les figures utilisées dans le rapport à partir des fichiers audio et
des paramètres extraits par main_analyse.py et main_synthese.py.

Usage (depuis la racine du projet) :
    ./venv/bin/python3 src/main_figures_rapport.py
"""

import os

import numpy as np
import matplotlib
matplotlib.use("Agg")  # rendu sans écran (les figures sont sauvegardées en tant que fichiers png)
import matplotlib.pyplot as plt
import scipy.io.wavfile as wav

from note import Note
from sequencer import Sequencer
from sinusoid import load_sinusoids_from_npz
from synthetiser import Synthetiser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # racine du projet python
FIG_DIR = os.path.normpath(os.path.join(ROOT, "figures"))    


def set_style():
    """Style commun à toutes les figures du rapport."""
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Liberation Serif", "Nimbus Roman", "DejaVu Serif"],
        "font.size": 9,
        "axes.labelsize": 9,
        "axes.titlesize": 9.5,
        "legend.fontsize": 8,
        "xtick.labelsize": 8.5,
        "ytick.labelsize": 8.5,
        "axes.grid": True,
        "grid.alpha": 0.25,
        "grid.linewidth": 0.6,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.dpi": 200,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
    })


def compute_spectrum(signal, sample_rate):
    """Calcule le spectre d'amplitude (TFD) d'un signal fenêtré par une fenêtre de Hanning."""
    N = len(signal)
    windowed = signal * np.hanning(N)
    spectrum = np.fft.rfft(windowed)
    freqs = np.fft.rfftfreq(N, d=1 / sample_rate)
    return freqs, np.abs(spectrum)


def to_db(magnitude, reference):
    """Convertit une amplitude en dB par rapport à une référence (20*log10)."""
    return 20 * np.log10(np.maximum(magnitude, 1e-12) / reference)


def figure_spectres(freqs, orig_db, synth_db, sinusoids, fmax=8000):
    """Trace le spectre original (avec harmoniques retenues) et la superposition
    du spectre original et du spectre synthétisé."""
    # Spectre du signal original, avec les harmoniques retenues identifiées
    fig, ax = plt.subplots(figsize=(6, 2.2))
    mask = freqs <= fmax
    ax.plot(freqs[mask], orig_db[mask], color="0.35", linewidth=0.6)
    harmoniques = [s for s in sinusoids if s.frequency > 0]
    for s in harmoniques:
        idx = np.argmin(np.abs(freqs - s.frequency))
        ax.plot(s.frequency, orig_db[idx], marker="o", markersize=2.4,
                color="tab:red", zorder=3)
    ax.set_xlim(0, fmax)
    ax.set_ylim(-80, 5)
    ax.set_xlabel("Fréquence (Hz)")
    ax.set_ylabel("Amplitude (dB)")
    fig.savefig(os.path.join(FIG_DIR, "spectre_lad_original.png"))
    plt.close(fig)

    # Superposition des deux spectres pour évaluer la qualité de la synthèse
    fig, ax = plt.subplots(figsize=(6, 2.4))
    ax.plot(freqs[mask], orig_db[mask], color="0.45", linewidth=0.7, label="Signal original")
    ax.plot(freqs[mask], synth_db[mask], color="tab:red", linewidth=0.7,
            alpha=0.8, label="Signal synthétisé")
    ax.set_xlim(0, fmax)
    ax.set_ylim(-80, 5)
    ax.set_xlabel("Fréquence (Hz)")
    ax.set_ylabel("Amplitude (dB)")
    ax.legend(loc="upper right", framealpha=0.95)
    fig.savefig(os.path.join(FIG_DIR, "spectres_lad_comparaison.png"))
    plt.close(fig)


def figure_enveloppe(t, signal, envelope):
    """Trace le signal redressé et l'enveloppe temporelle extraite."""
    echelle = np.max(np.abs(signal))
    fig, ax = plt.subplots(figsize=(6, 2.3))
    ax.plot(t, np.abs(signal) / echelle, color="0.75", linewidth=0.35,
            label="Signal redressé $|x[n]|$")
    ax.plot(t, envelope / echelle, color="tab:red", linewidth=1.1,
            label="Enveloppe temporelle $e[n]$")
    ax.set_xlim(0, t[-1])
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("Temps (s)")
    ax.set_ylabel("Amplitude normalisée")
    ax.legend(loc="upper right", framealpha=0.95)
    fig.savefig(os.path.join(FIG_DIR, "enveloppe_lad.png"))
    plt.close(fig)


def figure_melodie(t, melodie, debuts, attack_delay):
    """Trace la forme d'onde de la mélodie synthétisée ainsi que les attaques des notes.

    `debuts` contient l'instant de départ de chaque note dans la mélodie et
    `attack_delay` le délai entre ce départ et l'attaque audible (l'enveloppe de
    la note analysée commence par un court silence avant l'attaque de la corde).
    """
    labels = [
        ("SOL (x3)", (debuts[0] + debuts[2]) / 2 + attack_delay),
        ("Mib", debuts[3] + attack_delay),
        ("FA (x3)", (debuts[4] + debuts[6]) / 2 + attack_delay),
        ("RÉ", debuts[7] + attack_delay),
    ]
    fig, ax = plt.subplots(figsize=(6, 1.9))
    ax.plot(t, melodie, color="tab:blue", linewidth=0.4)
    for debut in debuts:
        ax.axvline(debut + attack_delay, color="tab:red", linewidth=0.6, linestyle="--", alpha=0.7)
    for nom, position in labels:
        ax.annotate(nom, (position, 1.12), ha="center", va="bottom", fontsize=8, color="tab:red")
    ax.set_xlim(0, t[-1])
    ax.set_ylim(-1.2, 1.45)
    ax.set_xlabel("Temps (s)")
    ax.set_ylabel("Amplitude")
    fig.savefig(os.path.join(FIG_DIR, "melodie_beethoven.png"))
    plt.close(fig)


def figure_reponse_passe_bas(order=884, omega_c=np.pi / 1000):
    """Trace la réponse en fréquence du filtre passe-bas moyenne mobile d'ordre `order`."""
    from scipy import signal as sig

    h = np.ones(order) / order
    omegas, H = sig.freqz(h, worN=65536)
    gain_db = 20 * np.log10(np.maximum(np.abs(H), 1e-12))

    fig, ax = plt.subplots(figsize=(6, 2.6))
    ax.plot(omegas[:1500], gain_db[:1500], color="tab:blue", linewidth=1.0)
    ax.axhline(-3, color="0.5", linewidth=0.6, linestyle=":")
    ax.plot([omega_c], [-3], marker="o", markersize=4, color="tab:red", zorder=3)
    ax.annotate("$\\bar{\\omega}_c = \\pi/1000$ ($-3$ dB)",
                xy=(omega_c, -3), xytext=(omega_c + 0.004, -6.5),
                fontsize=8, color="tab:red",
                arrowprops=dict(arrowstyle="->", color="tab:red", lw=0.7))
    ax.set_xlim(0, 0.05)
    ax.set_ylim(-40, 2)
    ax.set_xlabel("Fréquence normalisée $\\bar{\\omega}$ (rad/échantillon)")
    ax.set_ylabel("Gain (dB)")
    fig.savefig(os.path.join(FIG_DIR, "Graphique_fonction_rep.png"))
    plt.close(fig)


def print_typst_table(sinusoids):
    """Affiche le tableau Typst des harmoniques retenues (hors composante continue)."""
    harmoniques = [s for s in sinusoids if s.frequency > 0]
    harmoniques.sort(key=lambda s: s.frequency)
    print("#let harmoniques = (")
    for s in harmoniques:
        f = f"{s.frequency:.2f}".replace(".", ",")
        a = f"{s.amplitude:.5f}".replace(".", ",")
        p = f"{s.phase:.3f}".replace(".", ",")
        print(f'  ("{f}", "{a}", "{p}"),')
    print(")")


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    set_style()

    # --- Analyse : signaux et paramètres ---
    sample_rate, temporal_signal = wav.read(os.path.join(ROOT, "sounds", "note_guitare_lad.wav"))
    sinusoids, _ = load_sinusoids_from_npz(os.path.join(ROOT, "parameters", "sinusoids_lad466.npz"))
    envelope = np.load(os.path.join(ROOT, "parameters", "envelope.npz"))["envelope"]

    # --- Signal synthétisé : la note seule, puis la mélodie ---
    synthetiser = Synthetiser(sample_rate, sinusoids, envelope)
    note_synthetisee = synthetiser.synthetize(Note.LaD, octave=4)

    sequencer = Sequencer(bpm=108)
    sequencer.add_note(Note.Sol, octave=3, position=0.0)
    sequencer.add_note(Note.Sol, octave=3, position=0.5)
    sequencer.add_note(Note.Sol, octave=3, position=1.0)
    sequencer.add_note(Note.Mib, octave=3, position=1.5)
    sequencer.add_note(Note.Fa, octave=3, position=4.0)
    sequencer.add_note(Note.Fa, octave=3, position=4.5)
    sequencer.add_note(Note.Fa, octave=3, position=5.0)
    sequencer.add_note(Note.Re, octave=3, position=5.5)
    melodie = synthetiser.synthesize(sequencer.cells)

    # --- Spectres (échelle commune : maximum du spectre original) ---
    freqs, orig_mag = compute_spectrum(temporal_signal.astype(float), sample_rate)
    _, synth_mag = compute_spectrum(note_synthetisee, sample_rate)
    reference = np.max(orig_mag)
    figure_spectres(freqs, to_db(orig_mag, reference), to_db(synth_mag, reference),
                    sinusoids, fmax=8000)

    # --- Enveloppe temporelle ---
    t = np.arange(len(temporal_signal)) / sample_rate
    figure_enveloppe(t, temporal_signal.astype(float), envelope)

    # --- Mélodie de la 5e symphonie ---
    t_melodie = np.arange(len(melodie)) / sample_rate
    # Délai entre le début d'une note et son attaque audible (silence initial de l'enveloppe)
    attack_delay = float(np.argmax(envelope >= 0.5 * np.max(envelope))) / sample_rate
    debuts = [cell.start for cell in sequencer.cells]
    figure_melodie(t_melodie, melodie / np.max(np.abs(melodie)), debuts, attack_delay)

    # --- Réponse du filtre passe-bas d'extraction de l'enveloppe ---
    figure_reponse_passe_bas(order=884)

    # --- Tableau Typst ---
    print_typst_table(sinusoids)
    print(f"\nFigures écrites dans {FIG_DIR}")


if __name__ == "__main__":
    main()
