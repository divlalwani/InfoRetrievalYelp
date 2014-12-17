########################################################################################################################
# Author: Aravindh Varadharaju
#
# The code is used to classify the review into one of the five review categories. The input to this code is a JSON file
# that contains the review text and rating from the data set. The JSON file is produced using "GenerateTrainingData.py".
# Reviews are then classified into categories using MultinomialBayes, LinearSVC and SVR classifiers. These classifiers
# are available with SciKit
#
# The steps followed in the code is given below:
# 1. Load the data from JSON file into a list
# 2. Call the functions with the data which in turn call the classifiers
# 3. Within each function, the following activities are taken care of:
#    a. Generate TF-IDF vectors, once the data is pre-processed
#    b. Split the data into training and test data set in the ration of 80:20
#    c. Call the "fit_transform" on the training documents to return the term document matrix
#    d. Call the "transform" on the testing documents to transform the documents to document term matrix
#    e. Train the classifier with training data
#    f. Run the classifier against the test data and get the accuracy score
########################################################################################################################

import json
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC, SVR
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk import sent_tokenize, word_tokenize, WordNetLemmatizer
from nltk.corpus import stopwords
from sklearn.cross_validation import train_test_split


def read_json():
    with open("Ratings.json") as json_data:
        json_list = []
        for line in json_data:
            json_dict = json.loads(line)
            json_list.append(json_dict)
    return json_list


def pre_process(text):

    # replace (,.'") with ''
    text = text.replace(',', '')
    text = text.replace('.', '')
    text = text.replace("'", '')
    text = text.replace("\"", '')

    # tokenize into words
    tokens = [word for sent in sent_tokenize(text) for word in word_tokenize(sent)]

    # remove stopwords
    stop = stopwords.words('english')
    tokens = [token for token in tokens if token not in stop]

    # remove words less than three letters
    tokens = [word for word in tokens if len(word) >= 3]

    # lower capitalization
    tokens = [word.lower() for word in tokens]

    # lemmatize
    lmtzr = WordNetLemmatizer()
    tokens = [lmtzr.lemmatize(word) for word in tokens]

    return tokens


def CalculateSVM(data=None):
    vectorizer = TfidfVectorizer(tokenizer=pre_process)
    classifier = LinearSVC()
    train, test = train_test_split([(i['text'], i['stars']) for i in data],
                                   test_size=.2,
                                   random_state=10)
    x_train = vectorizer.fit_transform(i[0] for i in train)
    x_test = vectorizer.transform(i[0] for i in test)
    classifier.fit(x_train, [i[1] for i in train])
    score = classifier.score(x_test, [i[1] for i in test])
    print score


def CalculateMNB(data=None):
    vectorizer = TfidfVectorizer(tokenizer=pre_process)
    classifier = MultinomialNB()
    train, test = train_test_split([(i['text'], i['stars']) for i in data],
                                   test_size=.2,
                                   random_state=10)
    x_train = vectorizer.fit_transform(i[0] for i in train)
    x_test = vectorizer.transform(i[0] for i in test)
    classifier.fit(x_train, [i[1] for i in train])
    score = classifier.score(x_test, [i[1] for i in test])
    print score


def CalculateSVR(data=None):
    vectorizer = TfidfVectorizer(tokenizer=pre_process)
    classifier = SVR(kernel='linear')
    train, test = train_test_split([(i['text'], i['stars']) for i in data],
                                   test_size=.2,
                                   random_state=10)
    x_train = vectorizer.fit_transform(i[0] for i in train)
    x_test = vectorizer.transform(i[0] for i in test)
    classifier.fit(x_train, [i[1] for i in train])
    score = classifier.score(x_test, [i[1] for i in test])
    print score


def main():
    data = read_json()
    if data:
        CalculateMNB(data)
        CalculateSVM(data)
        CalculateSVR(data)
    else:
        print "Missing Source Data"


main()