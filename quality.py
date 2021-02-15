import os
from utils import read_classification_from_file
from confmat import BinaryConfusionMatrix


def quality_score(tp, tn, fp, fn):
    return (tp + tn) / (tp + tn + 10 * fp + fn)


def compute_quality_for_corpus(corpus_dir):
    dirs = os.listdir(corpus_dir)

    for file in dirs:
        if '!' in file:
            if file == "!truth.txt":
                truth_dict = read_classification_from_file(corpus_dir + '/' + file)
            elif file == "!prediction.txt":
                pred_dict = read_classification_from_file(corpus_dir + '/' + file)
            else:
                truth_dict = None
                pred_dict = None
        else:
            pass

    cm1 = BinaryConfusionMatrix(pos_tag="SPAM", neg_tag="OK")
    cm1.compute_from_dicts(truth_dict, pred_dict)
    final_dict = cm1.as_dict()
    return quality_score(final_dict['tp'], final_dict['tn'], final_dict['fp'], final_dict['fn'])