import pretty_midi
from visual_midi import Plotter

def tempo_and_onset(midi_data, integer_tempo=True, steps_per_quarter=1):
    """
    Extracts tempo and onset(start time of first estimated beat) of the given midi data
        using functionality provided by pretty_midi

    Returns: tempo in qpm (float)
             onset in start time (seconds) of first estimated beat
    """
    tempo = midi_data.estimate_tempo()
    onset_beat = midi_data.estimate_beat_start()
    steps_per_second = steps_per_quarter*tempo/60
    onset_time = onset_beat/steps_per_second

    if integer_tempo:
        tempo = int(tempo)

    return tempo, onset_time

def main():
    path = "data/BillieJean.mid"
    midi_data = pretty_midi.PrettyMIDI(path)

    est_tp, est_onst = tempo_and_onset(midi_data)
    print(est_tp, est_onst)
    plotter = Plotter()
    plotter.show(midi_data,'tmp/example.html')


if __name__=="__main__":
    main()