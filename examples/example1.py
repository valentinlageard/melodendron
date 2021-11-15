import mido
from melodendron import MVVOMM, random_select, intersect_select, weighted_intersect_select, exp_weighted_intersect_select
from melodendron import print_plagiarism_infos, print_sequence_infos
from melodendron import MidiFileParser, states_to_midi_track
from functools import partial

# Select viewpoints used by the model and create the model
viewpoints = ['pitches', 'total_duration', 'dynamic']
model = MVVOMM(viewpoints)
# Uncomment to test various selectors
#selector = random_select
#selector = intersect_select
#selector = weighted_intersect_select
selector = partial(exp_weighted_intersect_select, factor=1.2)  # Passed as a partial to set the exponential factor

# Open a midi file
midi_file_parser = MidiFileParser('midi/chpn_op27_2.mid')
print(midi_file_parser)

# Merge track 1 and 2 (left and right piano) and convert them to a state sequence
state_sequence = midi_file_parser.get_states_from_tracks([1, 2])
print_sequence_infos(state_sequence)

# Feed the state sequence to the model
model.insert_sequence(state_sequence, max_order=8)

# Generate a new sequence from model: 200 states with order 5
new_sequence = model.generate_n(2000, selector=selector, order=5)
print_plagiarism_infos(new_sequence)

# Export the sequence to a output.mid file in midi directory
new_file = mido.MidiFile()
new_file.tracks.append(mido.MidiTrack())
new_file.tracks[0].extend(midi_file_parser.midi_file.tracks[0][10:13])
new_track = states_to_midi_track(new_sequence)
new_file.tracks.append(new_track)
out_filepath = 'midi/output.mid'
new_file.save(out_filepath)
print('File was written to ' + out_filepath)