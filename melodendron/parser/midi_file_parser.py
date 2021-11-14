import mido
import itertools
import queue
from .utils import add_dynamic


def simultaneous_msgs(track: mido.MidiTrack):
    """A generator yielding all simultaneous midi messages."""
    delta = None
    msgs = list()
    for msg in track:
        if delta is None:
            delta = msg.time
            msgs.append(msg)
        elif msg.time == 0:
            msgs.append(msg)
        else:
            yield msgs
            delta = msg.time
            msgs = [msg]
    yield msgs


def drop_non_note_messages(track: mido.MidiTrack) -> mido.MidiTrack:
    """Returns a new midi track with only note on/off messages while keeping timing intact."""
    new_track = mido.MidiTrack()
    delta_accum = 0
    for msg in track:
        if msg.type in ['note_on', 'note_off']:
            msg.time += delta_accum
            new_track.append(msg)
            delta_accum = 0
        else:
            delta_accum += msg.time
    return new_track


def convert_zero_velocity_messages_to_note_off(track: mido.MidiTrack) -> mido.MidiTrack:
    """Returns a new midi track with 0 velocity note on message converted to note off."""
    new_track = mido.MidiTrack()
    for msg in track:
        if msg.type == 'note_on' and msg.velocity == 0:
            new_msg = mido.Message('note_off', channel=msg.channel, note=msg.note, velocity=0, time=msg.time)
            new_track.append(new_msg)
        else:
            new_track.append(msg)
    return new_track


def prioritize_note_offs(track):
    """Returns a new midi track where note offs are placed first. This is needed for the parsing."""
    new_track = mido.MidiTrack()
    for msgs in simultaneous_msgs(track):
        delta = msgs[0].time
        msgs[0].time = 0
        note_offs = [msg for msg in msgs if msg.type == 'note_off']
        note_ons = [msg for msg in msgs if msg.type == 'note_on']
        if note_offs:
            note_offs[0].time = delta
        else:
            note_ons[0].time = delta
        new_track.extend(note_offs + note_ons)
    return new_track


def midi_track_to_states(track: mido.MidiTrack):
    """Converts a mido Miditrack into a state sequence usable by the MVVOMM."""

    # "Clean" the midi track
    track = drop_non_note_messages(track)
    track = convert_zero_velocity_messages_to_note_off(track)
    track = prioritize_note_offs(track)

    sequence = list()

    delta_accum = 0
    state = dict(pitches=set(), note_events=list(), on_duration=None, off_duration=None, total_duration=None)

    for i, msg in enumerate(track):
        delta_accum += msg.time
        if msg.type == 'note_on':
            # If the current state has all note events finished, finish completing it, append it to the sequence and
            # generate a new empty state.
            if all(note_event['end_delta'] is not None for note_event in state['note_events']) and i != 0:
                state["off_duration"] = delta_accum - state['on_duration']
                state['total_duration'] = delta_accum
                sequence.append(state)
                delta_accum = 0
                state = dict(pitches=set(), note_events=list(),
                             on_duration=None, off_duration=None, total_duration=None)
            # Create a new note event and add it to the current state
            note_event = dict(pitch=msg.note, velocity=msg.velocity, start_delta=delta_accum, end_delta=None)
            state['pitches'].add(msg.note)
            state['note_events'].append(note_event)
        if msg.type == 'note_off':
            # Find first occurence of note_event with same pitch but no end_delta and set its delta
            matching_note_event = next((note_event for note_event in state['note_events']
                                        if note_event['pitch'] == msg.note and note_event['end_delta'] is None), None)
            if matching_note_event is not None:
                matching_note_event['end_delta'] = delta_accum
            # If all note_events have finished, set the on_duration of the current state
            if all(note_event['end_delta'] is not None for note_event in state['note_events']):
                state['on_duration'] = delta_accum
    state['off_duration'] = 0
    state['total_duration'] = state['on_duration']
    sequence.append(state)
    return sequence
    #TODO: Add support for a legato delay.
    #TODO: Rewrite as a generator function


def states_to_midi_track(states):
    midi_track = mido.MidiTrack()
    last_end_delta = 0
    for state in states:
        priority_queue = queue.PriorityQueue()
        unique = itertools.count()
        for i, note_event in enumerate(state['note_events']):
            pitch = note_event['pitch']
            velocity = note_event['velocity']
            start_delta = note_event['start_delta']
            end_delta = note_event['end_delta']
            on_message = mido.Message('note_on', note=pitch, velocity=velocity, time=start_delta)
            off_message = mido.Message('note_off', note=pitch, velocity=0, time=end_delta)
            priority_queue.put((start_delta, next(unique), on_message))
            priority_queue.put((end_delta, next(unique), off_message))
        priority, count, first_msg = priority_queue.get()
        previous_time = first_msg.time
        first_msg.time = last_end_delta
        midi_track.append(first_msg)
        while not priority_queue.empty():
            priority, count, msg = priority_queue.get()
            time_tmp = msg.time
            msg.time -= previous_time
            previous_time = time_tmp
            midi_track.append(msg)
        last_end_delta = state['off_duration']
    midi_track.append(mido.MetaMessage('end_of_track', time=0))
    return midi_track


class MidiFileParser():
    def __init__(self, filepath):
        self.filepath = filepath
        self.midi_file = mido.MidiFile(filepath)
        self.time_signature = self._find_time_signature()
        self.tempo = self._find_tempo()

    def _find_time_signature(self):
        """Search for a time signature in the file.
        Defaults to 4/4 if none found."""
        for track in self.midi_file.tracks:
            for msg in track:
                if msg.type == 'time_signature':
                    return msg.numerator, msg.denominator
        return 4, 4

    def _find_tempo(self):
        """Search for a tempo and returns it or none."""
        for track in self.midi_file.tracks:
            for msg in track:
                if msg.type == 'set_tempo':
                    return mido.bpm2tempo(msg.tempo)
        return None

    def get_states_from_tracks(self, track_idxs, with_dynamic=True):
        """Convert midi track to states.
        If several midi tracks are queried, they are merged before conversion."""
        tracks = [self.midi_file.tracks[idx] for idx in track_idxs]
        merged_track = mido.merge_tracks(tracks)
        sequence = midi_track_to_states(merged_track)
        if with_dynamic:
            add_dynamic(sequence)
        return sequence

    def __str__(self):
        first_line = 'File {}: ({}/{}, {} BPM)'.format(self.filepath,
                                                      self.time_signature[0], self.time_signature[1],
                                                      self.tempo)
        track_lines = ['\tTrack {}: {} ({} messages)'.format(i, track.name, len(track))
                       for i, track in enumerate(self.midi_file.tracks)]
        return '\n'.join((first_line, *track_lines))


__all__ = ['MidiFileParser', 'states_to_midi_track']
