class BinaryConfusionMatrix:
    def __init__(self, pos_tag, neg_tag):
        super().__init__()
        self.tp = 0
        self.tn = 0
        self.fp = 0
        self.fn = 0
        self.pos_tag = pos_tag
        self.neg_tag = neg_tag

    def as_dict(self):
        """Return the conf. mat. as a dictionary"""
        return {'tp': self.tp, 'tn': self.tn, 'fp': self.fp, 'fn': self.fn}

    def update(self, truth, prediction):
        """Compare the truth with the prediction and increment the related counter."""

        if truth not in (self.pos_tag, self.neg_tag):
            raise ValueError('The "truth" parameter can be either %s or %s.' \
                             % (self.pos_tag, self.neg_tag))
        if prediction not in (self.pos_tag, self.neg_tag):
            raise ValueError('The "prediction" parameter can be either %s or %s.' \
                             % (self.pos_tag, self.neg_tag))
        if prediction == self.pos_tag:
            if truth == prediction:
                self.tp += 1
            else:
                self.fp += 1
        elif prediction == self.neg_tag:
            if truth == prediction:
                self.tn += 1
            else:
                self.fn += 1

    def compute_from_dicts(self, truth_dict, pred_dict):
        """Update the matrix using the corresponding values from both dictionaries.
        It is assumed that both dicts have the same keys.
        """
        for key in truth_dict:
            self.update(truth_dict[key], pred_dict[key])

    def check_value_of(self, value):
        """Raise ValueError if var does not contain either positive or negative tag."""
        if value not in (self.pos_tag, self.neg_tag):
            raise ValueError('The arguments may be either %s or %s.' \
                             % (self.pos_tag, self.neg_tag))


if __name__ == '__main__':
    cm1 = BinaryConfusionMatrix(pos_tag=True, neg_tag=False)
    cm1.as_dict()

    cm1.update(True, True)
    cm1.as_dict()

    truth_dict = {'em1': 'SPAM', 'em2': 'SPAM', 'em3': 'OK', 'em4': 'OK'}
    pred_dict = {'em1': 'SPAM', 'em2': 'OK', 'em3': 'OK', 'em4': 'SPAM'}
    cm2 = BinaryConfusionMatrix(pos_tag='SPAM', neg_tag='OK')
    cm2.compute_from_dicts(truth_dict, pred_dict)
    cm2.as_dict()