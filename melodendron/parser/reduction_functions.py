import statistics

def add_dynamic(sequence):
    for state in sequence:
        mean_velocity = statistics.mean([note_event['velocity'] for note_event in state['note_events']])
        if mean_velocity <= 16:
            state['dynamic'] = 'ppp'
        elif 16 < mean_velocity <= 32:
            state['dynamic'] = 'pp'
        elif 32 < mean_velocity <= 48:
            state['dynamic'] = 'p'
        elif 48 < mean_velocity <= 64:
            state['dynamic'] = 'mp'
        elif 64 < mean_velocity <= 80:
            state['dynamic'] = 'mf'
        elif 80 < mean_velocity <= 96:
            state['dynamic'] = 'f'
        elif 96 < mean_velocity <= 112:
            state['dynamic'] = 'ff'
        elif 112 < mean_velocity <= 127:
            state['dynamic'] = 'fff'
    return sequence