import statistics
import mido


def print_sequence_infos(state_sequence):
    print("Sequence length: {}".format(len(state_sequence)))
    note_events_numbers = [len(state['note_events']) for state in state_sequence]
    print("Highest number of note events: {}".format(max(note_events_numbers)))
    print("Mean number of note events per state: {}".format(round(statistics.mean(note_events_numbers), 2)))
    print("Median number of note events per state: {}".format(round(statistics.median(note_events_numbers), 2)))


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


def prioritize_note_offs(track: mido.MidiTrack) -> mido.MidiTrack:
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


__all__ = ['print_sequence_infos', 'simultaneous_msgs', 'drop_non_note_messages',
           'convert_zero_velocity_messages_to_note_off', 'prioritize_note_offs']
