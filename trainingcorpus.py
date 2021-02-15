import os
from corpus import Corpus
from utils import read_classification_from_file


# class TrainingCorpus(Corpus):
#     def get_class(self, name):
#         right_answers = read_classification_from_file(self.directory)
#         return right_answers.get(name)

class TrainingCorpus(Corpus):
    def __init__(self, path):
        Corpus.__init__(self, path)
        self.path = path
        self.truth_dict = read_classification_from_file(self.path + "/!truth.txt")

    def get_class(self, filename):
        return self.truth_dict.get(filename)

    def is_ham(self, name):
        if self.truth_dict.get(name) == "OK":
            return True
        else:
            return False

    def is_spam(self, name):
        if self.truth_dict.get(name) == "SPAM":
            return True
        else:
            return False

    def spams(self):
        files = os.listdir(self.path)
        for email in files:
            if self.truth_dict.get(email) == "SPAM":
                with open(self.path+'/'+email, 'r', encoding="utf-8") as f:
                    yield email, f.read()

    def hams(self):
        files = os.listdir(self.path)
        for email in files:
            if self.truth_dict.get(email) == "OK":
                with open(self.path+'/'+email, 'r', encoding="utf-8") as f:
                    yield email, f.read()