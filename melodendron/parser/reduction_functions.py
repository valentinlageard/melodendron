import statistics


def add_viewpoint_for_all(sequence, viewpoint, value):
    for state in sequence:
        state[viewpoint] = value
    return sequence


def add_derived_viewpoint(sequence, viewpoint, reduction):
    for state in sequence:
        state[viewpoint] = reduction(state)
    return sequence


def reduce_dynamic(state):
    mean_velocity = statistics.mean([note_event['velocity'] for note_event in state['note_events']])
    if mean_velocity <= 16:
        return 'ppp'
    elif 16 < mean_velocity <= 32:
        return 'pp'
    elif 32 < mean_velocity <= 48:
        return 'p'
    elif 48 < mean_velocity <= 64:
        return 'mp'
    elif 64 < mean_velocity <= 80:
        return 'mf'
    elif 80 < mean_velocity <= 96:
        return 'f'
    elif 96 < mean_velocity <= 112:
        return 'ff'
    elif 112 < mean_velocity <= 127:
        return 'fff'


def reduce_density(state):
    return len(state['note_events']) / state['on_duration']


__all__ = ['add_viewpoint_for_all', 'add_derived_viewpoint', 'reduce_dynamic', 'reduce_density']
