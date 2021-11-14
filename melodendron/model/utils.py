import statistics


def get_plagiarism_counts(state_sequence):
    counts = list()
    count = 0
    for i in range(len(state_sequence) - 1):
        if state_sequence[i]['id'] == state_sequence[i + 1]['id'] - 1:
            count += 1
        else:
            counts.append(count)
            count = 0
    return counts


def get_plagiarism_infos(state_sequence):
    plagiarism_counts = get_plagiarism_counts(state_sequence)
    plagiarism_proportion = sum(count for count in plagiarism_counts if count != 0) / len(state_sequence)
    longest_plagiarism = max(plagiarism_counts)
    mean_plagiarism_length_without_0 = statistics.mean(count for count in plagiarism_counts if count != 0)
    median_plagiarism_length_without_0 = statistics.median(count for count in plagiarism_counts if count != 0)
    infos = (plagiarism_proportion, longest_plagiarism, mean_plagiarism_length_without_0,
             median_plagiarism_length_without_0)
    return infos


def print_plagiarism_infos(state_sequence):
    infos = get_plagiarism_infos(state_sequence)
    print('Plagiarism proportion: {}%'.format(round(infos[0], 2) * 100))
    print('Longest plagiarism: {}'.format(round(infos[1], 2)))
    print('Mean plagiarism length: {}'.format(round(infos[2], 2)))
    print('Median plagiarism length: {}'.format(round(infos[3], 2)))

__all__ = ['get_plagiarism_infos', 'print_plagiarism_infos']
