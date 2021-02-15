from collections import Counter
from utils import read_classification_from_file
from corpus import Corpus
from quality import compute_quality_for_corpus
from trainingcorpus import TrainingCorpus
import re
import math


def purify(raw_html):
    """
    Clean email from html tags and punctuation marks
    :param raw_html: message from email in string format
    """
    tags = re.compile('<[^>]+>')
    comments = re.compile('<!--(?:<[^>]+>|[^<>]+)*-->')
    useless_chars = re.compile('[,?.:_"!/()=;-]')
    raw_html = re.sub(tags, '', raw_html)
    raw_html = re.sub(comments, '', raw_html)
    return re.sub(useless_chars, '', raw_html)


def convert_words_starting_with_upper_case(list_of_words):
    """
    Lowercase first char in words where only first char is uppercase, to easier detect spam words with uppercase chars.
    :param list_of_words: list of words
    """
    result = []
    for word in list_of_words:
        if len(word) > 1 and word[0].isupper() and word[1].islower():
            result.append(word.lower())
        else:
            result.append(word)
    return result


def join_spam_and_ham_words(spam_words, ham_words):
    """
    Join all spam and ham words
    :param spam_words: list of spam words
    :param ham_words: list of ham words
    """
    all_words = spam_words
    for word in ham_words:
        all_words.append(word)
    return all_words


def raw_email_to_list_of_words(message):
    """
    Split message to the list of words
    :param message: cleaned message in string format
    """
    message = purify(message)
    words = message.split()
    return convert_words_starting_with_upper_case(words)


def underflow_overflow_exception_handler(email_probability, underflow_overflow):
    """
    Avoid numbers too small or too big for float in calculations outside this function.
    :param email_probability: int, email probability if it is spam or not
    :param underflow_overflow: int variable to count how many overflows are there
    """
    if email_probability == math.inf:
        underflow_overflow += 1
        email_probability = 1.0
    if email_probability == 0:
        underflow_overflow -= 1
        email_probability = 1.0
    return email_probability, underflow_overflow


def decision(spam_overflow, spam_probability, ham_overflow, ham_probability):
    """
    Make decision if email is (SPAM - True) or it is (HAM - False)
    :param spam_overflow: int, how many overflow it has
    :param spam_probability: int, probability of being SPAM
    :param ham_overflow: int, how many overflow it has
    :param ham_probability: int, probability of being HAM
    """
    if spam_overflow > ham_overflow:
        return True
    if spam_overflow < ham_overflow:
        return False
    if spam_overflow == ham_overflow:
        return True if spam_probability > ham_probability else False


class MyFilter:
    """
    Filter uses Naive Bayes algorithm
    source: https://towardsdatascience.com/how-to-build-and-apply-naive-bayes-classification-for-spam-filtering-2b8d3308501
    """
    def __init__(self):
        self.truth_dict = {}
        self.pred_dict = {}
        self.all_words = {}
        self.spam_words = {}
        self.ham_words = {}
        self.num_of_spam_words = 0
        self.num_of_ham_words = 0
        self.num_of_all_words = 0
        self.portion_of_spam_emails = 1
        self.alpha = 1
        self.average_word_probability = 0

    def list_spam_ham_words(self, emails, is_spam):
        """
        Generates spam and ham words list
        :param emails: emails in a given directory
        :param is_spam: Boolean, defines if it is SPAM or NOT
        """
        if is_spam:
            email_generator = emails.spams()
        else:
            email_generator = emails.hams()
        num_of_emails = 0
        words = []
        for name, message in email_generator:
            num_of_emails += 1
            words += raw_email_to_list_of_words(message)
        if is_spam:
            self.spam_words = Counter(words)
        else:
            self.ham_words = Counter(words)
        return words, num_of_emails

    def train(self, path):
        """
        Trains the corpus on given emails dataset
        :param path: directory with emails
        """
        self.truth_dict = read_classification_from_file(path + "/!truth.txt")
        emails = TrainingCorpus(path)

        spam_words, num_of_spam_emails = self.list_spam_ham_words(emails, True)
        ham_words, num_of_ham_emails = self.list_spam_ham_words(emails, False)

        self.portion_of_spam_emails = num_of_spam_emails / (num_of_spam_emails + num_of_ham_emails)
        self.all_words = Counter(join_spam_and_ham_words(spam_words, ham_words))

        self.num_of_spam_words = len(spam_words)
        self.num_of_ham_words = len(ham_words)
        self.num_of_all_words = len(self.all_words)

    def test(self, path):
        """
        Tests given emails for being SPAM or HAM
        :param path: directory with emails
        """
        emails = Corpus(path)
        with open(path + "/!prediction.txt", 'w', encoding="utf-8") as f:
            self.alpha = self.calculate_alpha(emails)
            for filename, message in emails.emails():
                words = raw_email_to_list_of_words(message)
                spam_probability, spam_probability_overflow = self.calculate_email_probability(words, True)
                ham_probability, ham_probability_overflow = self.calculate_email_probability(words, False)
                if decision(spam_probability_overflow, spam_probability, ham_probability_overflow,
                            ham_probability):
                    f.write(filename + " SPAM\n")
                    self.pred_dict[filename] = "SPAM"
                else:
                    f.write(filename + " OK\n")
                    self.pred_dict[filename] = "OK"

    def calculate_alpha(self, emails):
        """
        Calculate alpha for Naive bayes algorithm. Alpha is the coefficient for
        the cases when a word in the message is absent in our dataset.
        :param emails: dir with emails
        """
        num_of_words_in_self_all_words = 0
        num_of_all_words_in_test_corpus = 0
        for filename, message in emails.emails():
            words = raw_email_to_list_of_words(message)
            for word in words:
                if word in self.all_words:
                    num_of_words_in_self_all_words += 1
            num_of_all_words_in_test_corpus += len(words)
        return num_of_words_in_self_all_words / num_of_all_words_in_test_corpus

    def calculate_email_probability(self, words, is_spam_calculation):
        """
        Calculates a number that is proportional to the probability of the email being SPAM or HAM
        :param words: list of words
        :param is_spam_calculation: Boolean, if it is SPAM calculation or NOT
        """
        underflow_overflow = 0
        spam_ham_dict = self.spam_words if is_spam_calculation else self.ham_words
        spam_ham_num_of_words = self.num_of_spam_words if is_spam_calculation else self.num_of_ham_words
        email_probability = 1.0
        for word in words:
            # Multiply by 1000 so there will not be so many unnecessary underflows
            email_probability *= 1000
            if word in self.all_words:
                if word in spam_ham_dict:
                    word_probability = (spam_ham_dict.get(word) + self.alpha) / (
                            spam_ham_num_of_words + self.alpha * self.num_of_all_words + self.alpha)
                else:
                    word_probability = self.alpha / (
                            spam_ham_num_of_words + self.alpha * self.num_of_all_words + self.alpha)
            else:
                word_probability = 1
            self.average_word_probability += word_probability
            email_probability *= word_probability
            email_probability, underflow_overflow = underflow_overflow_exception_handler(email_probability,
                                                                                         underflow_overflow)
        self.average_word_probability /= len(words)
        return email_probability, underflow_overflow


if __name__ == "__main__":
    my_filter1 = MyFilter()
    my_filter1.train("spam-data-12-s75-h25/1/")
    my_filter1.test("spam-data-12-s75-h25/2/")
    print("Quality of the spam filter for first folder with emails:")
    print(compute_quality_for_corpus("spam-data-12-s75-h25/2/"))

    my_filter2 = MyFilter()
    my_filter2.train("spam-data-12-s75-h25/2/")
    my_filter2.test("spam-data-12-s75-h25/1/")
    print("Quality of the spam filter for second folder with emails:")
    print(compute_quality_for_corpus("spam-data-12-s75-h25/1/"))
