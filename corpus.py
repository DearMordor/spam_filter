import os

class Corpus():
    def __init__(self, path):
        self.directory = path

    def emails(self):
        for files in os.listdir(self.directory):
            if files[0] != '!':
                with open(os.path.join(self.directory, files), 'r', encoding='utf-8') as f:
                    yield files, f.read()
