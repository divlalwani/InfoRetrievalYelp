from __future__ import division
########################################################################################################################
#
# Author: Aravindh Varadharaju
#
# For Task II
#
# This file has small utility functions to do the following:
#
# 1. combine_files(): This is used to combine data from two collections - restaurants (subset of business JSON file )
#                     and reviews. The output is written to RestaurantCombinedReviews.json
# 2. get_reviews(): This utility is used to write the business_id and reviews from reviews collection to the file
#                   BusinessReviews.json
# 3. get_training_reviews(): This utility function is used to generate a subset of training reviews from the main
#                            reviews collection. Set the size_of_training_review to the required count.
# 4. gen_review_coll_with_id(): This utility function is used to add a new counter field (record id) to a collection
# 5. get_restaurant_reviews(): This utility function is used to generate a subset of reviews corresponding to
#                              restaurants business
# 6. compare_ratings(): This utility function is used to compare the ratings estimated by our code with the ratings in
#                       the file. It calculates the percentage match and the Root Mean Square Error
########################################################################################################################

from pymongo import MongoClient
import json
import math

# Run the command given below to load the JSON files provided as part of the Yelp Dataset
#
# mongoimport --db yelp --collection business --type json yelp_academic_dataset_business.json --port 29017
# mongoimport --db yelp --collection checkin --type json yelp_academic_dataset_checkin.json --port 29017
# mongoimport --db yelp --collection review --type json yelp_academic_dataset_review.json --port 29017
# mongoimport --db yelp --collection tip --type json yelp_academic_dataset_tip.json --port 29017
# mongoimport --db yelp --collection user --type json yelp_academic_dataset_user.json --port 29017

# Run the command given below to get the details about restaurant business and create a restaurants collection
# 14303 businesses
# db.business.find({"categories":{$regex:".*Restaurants.*"}}).forEach(function(doc){db.restaurants.insert(doc)})

# Run the command given below to get the reviews which has the useful rating greater than 3 and create a review2
# collection
# 86579 reviews
# db.review.find({"votes.useful":{$gt: 3}}).forEach(function(doc){db.review2.insert(doc)})


class Business:
    """
    Class is used to simulate an object with the review text, review category and the business id to which the
    review is linked
    """
    def __init__(self, business_id, text, category):
        self.text = text
        self.category = category
        self.business_id = business_id


def combine_files():
    """
    The function is used to combine all the reviews for a business and write the business_id, the combined text of
    all the reviews and the category into a JSON file
    :return: None
    """
    restaurant_collection = MongoClient('localhost', 29017).yelp.restaurants
    review2_collection = MongoClient('localhost', 29017).yelp.review2
    output_file = open("RestaurantCombinedReviews.json", 'w')
    cursor = restaurant_collection.find()
    line = 0
    for entry in cursor:
        business_id = entry["business_id"]
        category = entry["categories"]
        review2_cursor = review2_collection.find({"business_id": business_id})
        review_text = ""
        for business_entry in review2_cursor:
            review_text = review_text + business_entry["text"]
            # print json.dumps(vars(obj))
        if review_text:
            line += 1
            obj = Business(business_id, review_text, category)
            output_file.write(json.dumps(vars(obj)))
            output_file.write("\n")
        if line % 100 == 0:
            print line
    output_file.close()


class Review:
    """
    The class is used to simulate the object which has the business id, the review text and the corresponding rating
    of the review
    """
    def __init__(self, business_id, text, stars):
        self.business_id = business_id
        self.text = text
        self.stars = stars


def get_reviews():
    """
    Function is used to get the individual reviews and their ratings from the review2 collection (This collection
    contains reviews with the useful rating > 3). The reviews are written to a JSON file

    :return: None
    """
    review_collection = MongoClient('localhost', 29017).yelp.review2
    review_cursor = review_collection.find()
    output_file = open("BusinessReviews.json", "w")
    line = 0
    for entry in review_cursor:
        business_id = entry["business_id"]
        text = entry["text"]
        if text:
            line += 1
            obj = Review(business_id, text)
            output_file.write(json.dumps(vars(obj)))
            output_file.write("\n")
        if line % 100 == 0:
            print line


def get_restaurant_reviews():
    """
    The function is used to get the reviews that corresponds to the restaurants business. The number of reviews would be
    49876. The details are written to a JSON file.
    :return: None
    """
    restaurant_collection = MongoClient('localhost', 29017).yelp.restaurants
    review_collection = MongoClient('localhost', 29017).yelp.review2
    restaurant_cursor = restaurant_collection.find({},{"business_id": 1, "_id": 0})
    output_file = open("RestaurantReviews.json", "w")
    line = 0
    for res_entry in restaurant_cursor:
        business_id = res_entry["business_id"]
        review_cursor = review_collection.find({"business_id": business_id})
        for review_entry in review_cursor:
            business_id = review_entry["business_id"]
            text = review_entry["text"]
            stars = review_entry["stars"]
            if text:
                line += 1
                obj = Review(business_id, text, stars)
                output_file.write(json.dumps(vars(obj)))
                output_file.write("\n")
            if line % 100 == 0:
                print line


def gen_review_coll_with_id():
    """
    The function is used to add a sequential id to the records within the review2 collection. This id was required to
    process the records in parallel when calculating the sentiment. This collection will be used by the code
    "ParallelProcess.py". The column is added and the record is written to a new collection: review_counter
    :return: None
    """
    review2_collection = MongoClient('localhost', 29017).yelp.review2
    review2_cursor = review2_collection.find()
    client = MongoClient('localhost', 29017)
    db = client.yelp
    review_counter = db.review_counter
    counter = 1
    for entry in review2_cursor:
        business_id = entry["business_id"]
        text = entry["text"]
        stars = entry["stars"]
        review_id = entry["review_id"]
        user_id = entry["user_id"]

        _dict = {"business_id": business_id, "text": text, "stars": stars, "review_id": review_id, "user_id": user_id,
                 "counter": counter}
        review_counter.insert(_dict)
        counter += 1

        if counter % 100 == 0:
            print counter


def compare_ratings():
    """
    The function is used to compare the rating produced by the our code with the existing data in the data set.
    It counts the number of matches between the ratings and then calculates the percentage of match. Along with
    the match percentage, the code also calculates the Root Mean Square Error
    :return: None
    """
    combined_collection = MongoClient('localhost', 29017).yelp.CalRatings5000
    combined_cursor = combined_collection.find({},{"rating":1,"stars":1,"_id":0})
    total_cnt = combined_cursor.count()
    print total_cnt
    match_cnt = 0
    diff_sum = 0
    for entry in combined_cursor:
        rating = entry["rating"]
        stars = entry["stars"]
        diff_square = math.pow(abs(rating - stars),2)
        diff_sum += diff_square
        if rating == stars:
            match_cnt += 1
        elif abs(rating - stars) == 1:
            match_cnt += 1
    print "RMSE: {0}".format(str(math.sqrt(diff_sum / total_cnt)))
    print "Percentage of match: "+str((match_cnt/total_cnt)*100)


class TrainReview:
    """
    This Class is used to create an object with the training text and the corresponding rating which is stored as label.
    TextBlob requires the training data set strictly in the format of text:{}, label:{}
    """
    def __init__(self, text, label):
        self.text = text
        self.label = label


def get_training_reviews(size_of_training_review=None):
    """
    The function is used to read records from the review2 collection and then create a records in JSON format shown
    below:
        JSON format:
                    [
                        {"text": "Sample Text","label":"1"},
                        {"text": "Sample Text","label":"2"}
                    ]
        The JSON data is written to a file.
    :param size_of_training_review: example 1000, 2000 etc
    :return: None
    """
    review_collection = MongoClient('localhost', 29017).yelp.review2
    review_cursor = review_collection.find()
    training_file = open("TrainingReviews_2.json", "w")
    line = 0
    training_file.write("[\n")
    for entry in review_cursor:
        if line < size_of_training_review:
            text = entry["text"]
            rating = entry["stars"]
            if text:
                line += 1
                obj = TrainReview(text, rating)
                str_line = json.dumps(vars(obj))
                if line < size_of_training_review:
                    training_file.write("\t" + str_line + ",\n")
                else:
                    training_file.write(str_line)
            if line % 100 == 0:
                print line
        else:
            break
    training_file.write("]")


def sample_reviews():
    """
    Adhoc function to provide some data to a team-mate
    :return: None
    """
    review_collection = MongoClient('localhost', 29017).yelp.review2
    review_cursor = review_collection.find()
    output_file = open("GowriReviews.json", "w")
    line = 0
    for entry in review_cursor:
        review_id = entry["review_id"]
        text = entry["text"]
        text = text.replace('\n', ' ').replace('\r', '')
        stars = entry["stars"]
        if text:
            line += 1
            str_line=review_id+"\t"+str(stars)+"\t"+text
            output_file.write(str_line.encode('utf-8'))
        if line == 5000:
            break
        else:
            output_file.write("\n")
    output_file.close()



# Call the required function

# combine_files()
# get_reviews()
# get_training_reviews(size_of_training_review=4000)
# gen_review_coll_with_id()
# sample_reviews()
compare_ratings()
# get_restaurant_reviews()
