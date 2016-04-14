from Util.Import import load_new_file, load_original_file, get_files
import unicodedata as ud
import json
import math
from stop_words import safe_get_stop_words
import re

class Vectoriser:
    """
    Class for building vectors from tweets
    """
    def __init__(self):
        self.dictionary = {}
        self.id_reference = {}
        # self.idf = {}
        # self.n_dt = {}
        # self.document_count = 0
        self._id = 0

    def generate_id(self):
        """
        :return: numbers incrementing by 1 each time function is called
        """
        self._id += 1
        return self._id

    def vectorise(self, string):
        """
        convert string into a bag of words vector
        :param string: text sentence
        :return: sparse vector in dictionary format
        """
        sentence = self.tokeniser(string)
        vector = {}

        for word in sentence:
            try:
                id = self.dictionary[word]
            except KeyError:
                id = self.generate_id()
                self.dictionary[word] = id
                self.id_reference[id] = word

            try:
                vector[id] += 1
            except KeyError:
                vector[id] = 1

        return vector

    def add_vector(self, df):
        """
        add vector to dataframe
        :param df: dataframe with no vector
        :return: dataframe with vector
        """
        df['vector'] = df['text'].map(lambda text: self.vectorise(text))
        return df

    def tokeniser(self, string):
        """
        split full sentence into list of tokens
        :param string: text sentence
        :return: list of tokens
        """
        # TODO: develop tokeniser
        string = string.lower()
        list = re.split("[, \-!?()]+", string)

        stop_words = safe_get_stop_words("en")
        numsPunc = [str(i) for i in range(10)] + ["@", "...", ":", "'", '"', '…', '.', ',']

        for i in range(len(list)):

            if list[i] in stop_words:
                list[i] = list[i].replace(list[i], "")

            if "#" in list[i]:
                list[i] = list[i].replace("#", "")

            if "https://" in list[i]:
                list[i] = list[i].replace(list[i], "")

            for num in numsPunc:
                list[i] = list[i].replace(num, "")

        list = [word for word in list if len(word) > 2]
        return list

# get filenames for original data and new processed data
files = get_files('../Twitter')
new_files = get_files('../data')

# initialise vectoriser tool
vec = Vectoriser()
no_files = len(files)

# add vector to data, drop unnecessary columns and save data to new path
for i, file in enumerate(files):
    if i % 20 == 0:
        print("Adding vector to data: {}/{} files\r".format(i+1, no_files), end='\r')
    data = load_original_file(file)
    data = data[['username', 'date', 'text', 'profileLocation', 'latitude', 'longitude']]
    data = vec.add_vector(data)
    if i == no_files - 1:
        print("Vectorising: Complete")
    data.to_json(new_files[i], orient='index')

# save id/term dictionaries in json format
with open('term_to_id_dictionary.txt', 'w') as fp:
    json.dump(vec.dictionary, fp)

with open('id_to_term_dictionary.txt', 'w') as fp:
    json.dump(vec.id_reference, fp)


