import mido
from melodendron import MVVOMM, random_select, intersect_select
from melodendron import print_plagiarism_infos
from melodendron import MidiFileParser, states_to_midi_track

# Select viewpoints, create model and choose a selector function
viewpoints = ['pitches', 'dynamic']
model = MVVOMM(viewpoints)
selector = intersect_select

# Open a midi file
midi_file_parser = MidiFileParser('midi/gnossienne_3.mid')
print(midi_file_parser)

# Merge track 1 and 2 and convert them to a state sequence
state_sequence = midi_file_parser.get_states_from_tracks([1, 2])

# Feed the state sequence to the model
model.insert_sequence(state_sequence, max_order=8)

# Generate a new sequence from model: 50 states with order 1
new_sequence = model.generate_n(50, selector=selector, order=1)

print_plagiarism_infos(new_sequence)

# Export the sequence to a output.mid file in midi directory
new_file = mido.MidiFile()
new_file.ticks_per_beat = midi_file_parser.midi_file.ticks_per_beat
new_file.tracks.append(mido.MidiTrack())
new_file.tracks[0].extend(midi_file_parser.midi_file.tracks[0][3:6])
new_track = states_to_midi_track(new_sequence)
new_file.tracks.append(new_track)
new_file.save("midi/output.mid")
