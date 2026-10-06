import os

import numpy as np
import scipy.io.wavfile as wav

from sinusoid import load_sinusoids_from_npz
from sequencer import Sequencer
from synthetiser import Synthetiser
from note import Note


def save_signal(output_path: str, signal: np.ndarray, sample_rate: int):
    """
    Sauvegarde un signal audio dans un fichier WAV en s'assurant que le signal n'overflow pas 
    (normalisation par le plus grand pic si besoin).
    """
    crete = np.max(np.abs(signal))
    if crete > 0:
        signal = signal / crete * (0.95 * 32767)

    os.makedirs("sounds/outputs", exist_ok=True)
    wav.write(output_path, sample_rate, signal.astype(np.int16))
    print(f"Signal sauvegardé dans {output_path}.")


def main():

    # Création du synthétiseur et du séquenceur 
    sinusoids, sample_rate = load_sinusoids_from_npz("parameters/sinusoids_lad466.npz")
    envelope = np.load("parameters/envelope.npz")["envelope"]
    synthetiser = Synthetiser(sample_rate, sinusoids, envelope)

    sequencer = Sequencer()



    # Création de la mélodie de la 5ème symphonie de Beethoven
    sequencer.bpm = 108
    sequencer.add_note(Note.Sol, octave=3, position=0.0)
    sequencer.add_note(Note.Sol, octave=3, position=0.5)
    sequencer.add_note(Note.Sol, octave=3, position=1.0)
    sequencer.add_note(Note.Mib, octave=3, position=1.5)
    sequencer.add_note(Note.Fa, octave=3, position=4.0)
    sequencer.add_note(Note.Fa, octave=3, position=4.5)
    sequencer.add_note(Note.Fa, octave=3, position=5.0)
    sequencer.add_note(Note.Re, octave=3, position=5.5)

    # Synthèse et sauvegarde de la 5ème symphonie de Beethoven
    symphonie = synthetiser.synthesize(sequencer.cells)
    save_signal("sounds/outputs/5e_symphonie_beethoven.wav", symphonie, sample_rate)



    # Création de la mélodie de La Marseillaise (lue depuis un fichier MIDI)
    sequencer.clear()
    sequencer.bpm = 112
    sequencer.add_notes_from_midi("midi/marseillaise.midi")

    # Synthèse et sauvegarde de La Marseillaise
    marseillaise = synthetiser.synthesize(sequencer.cells)
    save_signal("sounds/outputs/marseillaise.wav", marseillaise, sample_rate)



    # Création de Hotel California (mélodie et accords lus depuis un fichier MIDI) : 
    sequencer.clear()
    sequencer.bpm = 85
    sequencer.add_notes_from_midi("midi/hotel_california.midi", piste=5) # mélodie
    sequencer.add_notes_from_midi("midi/hotel_california.midi", piste=8) # accords
    sequencer.add_notes_from_midi("midi/hotel_california.midi", piste=10) # basse

    # Synthèse et sauvegarde de Hotel California
    hotel_california = synthetiser.synthesize(sequencer.cells)
    save_signal("sounds/outputs/hotel_california.wav", hotel_california, sample_rate)


if __name__ == "__main__":
    main()
