import mido
from melodendron import MVVOMM, random_select, intersect_select, plagiarism
from melodendron import MidiFileParser, states_to_midi_track

# Select viewpoints, create model and choose a selector function
viewpoints = ['pitches', 'on_duration', 'dynamic']
model = MVVOMM(viewpoints)
selector = intersect_select

# Open a midi file
midi_file_parser = MidiFileParser('midi/chpn_op27_2.mid')
print(midi_file_parser)

# Merge track 1 and 2 (left and right piano) and convert them to a state sequence
state_sequence = midi_file_parser.get_states_from_tracks([1, 2])

# Feed the state sequence to the model
model.insert_sequence(state_sequence, max_order=8)

for i, state in enumerate(model.state_sequence):
    print(i, state)

# Generate a new sequence from model: 200 states with order 3
new_sequence = model.generate_n(200, selector=selector, order=1)

# Print the plagiarism proportion of the new_sequence
print('Plagiarism: {}%'.format(plagiarism(new_sequence) * 100))

# Export the sequence to a output.mid file in midi directory
new_file = mido.MidiFile()
new_file.tracks.append(mido.MidiTrack())
new_file.tracks[0].extend(midi_file_parser.midi_file.tracks[0][10:13])
new_track = states_to_midi_track(new_sequence)
new_file.tracks.append(new_track)
out_filepath = 'midi/output.mid'
new_file.save(out_filepath)
print('File was written to ' + out_filepath)
