########################################################################################################################
# Author: Aravindh Varadharaju
#
# For Task - II
#
# To categorize the review into one of the ratings based on the review text.
# 
# The code is used to generate data set according to the size specified in the calling function. The code reads the
# data from MongoDB. The RestaurantReviews collection has the reviews pertaining to Restaurant business. The number of
# reviews available are 49876. It finds the records of specified count and writes the "text" and "stars" rating into a
# file in JSON format.
#
########################################################################################################################
from pymongo import MongoClient
import json


class SampleEntry:
    """
    The class is used to represent a entry in the json with a review text and the rating of the text
    """
    def __init__(self, text, stars):
        self.text = text
        self.stars = stars


def get_sample_reviews(ratings=None,size=None):
    """
    Function used to query the Mongo Collection for a particular rating and number of records
    and write the review text and rating to a JSON file.

    :param ratings: Review rating in the Mongo Collection
    :param size: Number of records to be retrieved
    :return: None
    """
    combined_collection = MongoClient('localhost', 29017).yelp.RestaurantReviews
    file_name = "Ratings.json"
    ratings_file = open(file_name, 'a')
    if ratings and size:
        combined_cursor = combined_collection.find({"stars": ratings},{"text": 1, "stars": 1, "_id": 0}).limit(size)
        for entry in combined_cursor:
            text = entry["text"]
            stars = entry["stars"]
            tmp = ' '.join(text.split())
            obj = SampleEntry(tmp, stars)
            ratings_file.write(json.dumps(vars(obj)))
            ratings_file.write("\n")
    ratings_file.close()


def main():
    """
    Call the function get_sample_reviews with the rating to be fetched and the number of records
    :return: None
    """
    for i in range(1,6,1):
        get_sample_reviews(i,3000)