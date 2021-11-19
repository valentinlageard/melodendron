import mido
from melodendron import MVVOMM, exp_weighted_intersect_select
from melodendron import print_plagiarism_infos, print_sequence_infos
from melodendron import MidiFileParser, states_to_midi_track
from melodendron import add_derived_viewpoint, reduce_density
from functools import partial

# Select viewpoints used by the model and create the model
viewpoints = ['pitches', 'total_duration', 'on_duration', 'off_duration', 'dynamic', 'density']
model = MVVOMM(viewpoints)
selector = partial(exp_weighted_intersect_select, factor=1.2)  # Passed as a partial to set the exponential factor
order = 5

# Open a midi file
midi_file_parser = MidiFileParser('midi/chpn_op27_2.mid')
print(midi_file_parser)

# Merge track 1 and 2 (left and right piano) and convert them to a state sequence
state_sequence = midi_file_parser.get_states_from_tracks([1, 2])
add_derived_viewpoint(state_sequence, 'density', reduce_density)
print_sequence_infos(state_sequence)

# Feed the state sequence to the model
model.insert_sequence(state_sequence, max_order=order)

# Generate a new sequence from model: 200 states with order 5
new_sequence = model.generate_n(200, selector=selector, order=order)
print_plagiarism_infos(new_sequence)

# Export the sequence to a output.mid file in midi directory
new_file = mido.MidiFile()
new_file.tracks.append(mido.MidiTrack())
new_file.tracks[0].append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(midi_file_parser.tempo)))
new_track = states_to_midi_track(new_sequence, new_file.ticks_per_beat)
new_file.tracks.append(new_track)
out_filepath = 'midi/output.mid'
new_file.save(out_filepath)
print('File was written to ' + out_filepath)