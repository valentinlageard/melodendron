import statistics


def print_sequence_infos(state_sequence):
    print("Sequence length: {}".format(len(state_sequence)))
    note_events_numbers = [len(state['note_events']) for state in state_sequence]
    print("Highest number of note events: {}".format(max(note_events_numbers)))
    print("Mean number of note events per state: {}".format(round(statistics.mean(note_events_numbers), 2)))
    print("Median number of note events per state: {}".format(round(statistics.median(note_events_numbers), 2)))


__all__ = ['print_sequence_infos']