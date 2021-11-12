def plagiarism(state_sequence):
    plagiarized = 0
    for i in range(len(state_sequence) - 1):
        if state_sequence[i]['id'] == state_sequence[i + 1]['id'] - 1:
            plagiarized += 1
    return plagiarized / len(state_sequence)

__all__ = ['plagiarism']