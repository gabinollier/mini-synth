import os

import numpy as np
import scipy.io.wavfile as wav

from sinusoid import load_sinusoids_from_npz
from sequencer import Sequencer
from synthetiser import Synthetiser
from note import Note

def main():
    sinusoids_lad466, sample_rate = load_sinusoids_from_npz("parameters/sinusoids_lad466.npz")
    envelope = np.load("parameters/envelope.npz")["envelope"]
    synthetiser = Synthetiser(sample_rate, sinusoids_lad466, envelope)

    sequencer = Sequencer(bpm=108)
    sequencer.add_note(Note.Sol, octave=3, position=0.0)
    sequencer.add_note(Note.Sol, octave=3, position=0.5)
    sequencer.add_note(Note.Sol, octave=3, position=1.0)
    sequencer.add_note(Note.Mib, octave=3, position=1.5)
    sequencer.add_note(Note.Sol, octave=3, position=4.0)
    sequencer.add_note(Note.Sol, octave=3, position=4.5)
    sequencer.add_note(Note.Sol, octave=3, position=5.0)
    sequencer.add_note(Note.Re, octave=3, position=5.5)

    synthetised_signal = synthetiser.synthesize(sequencer.cells)
    os.makedirs("sounds/outputs", exist_ok=True)
    wav.write("sounds/outputs/5ème_synphonie_beethoven.wav", synthetiser.sample_rate, synthetised_signal.astype(np.int16))  
    print(f"Mélodie sauvegardée.")

if __name__ == "__main__":
    main()