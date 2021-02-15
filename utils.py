def read_classification_from_file(truth):
    right_answers = {}

    f = open(truth, 'r', encoding='utf-8')
    for line in f.readlines():
        words = line.split()
        right_answers[words[0]] = (words[1])

    f.close()
    return right_answers

