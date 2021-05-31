import os
import pickle
import pandas as pd
import turicreate as tc
import sys
from sklearn.linear_model import LinearRegression
from flask import Flask, request, jsonify
import requests
import json
from datetime import date, timedelta, datetime
import numpy as np
import random

# app.py
app = Flask(__name__)


today = datetime.today()
margin = timedelta(days = 14)


def extract_average(json):
    try:
        return int(json['average_rating'])
    except KeyError:
        return 0


@app.route('/rec', methods=['POST'])
def rec():

    jsdata = request.get_json()
    user_id = jsdata['user_id']
    dish_rating_df = get_dish_ratings(user_id)

    # if a user has reviewed greater than or equal to 5 dishes, they are not a new user, and will be given recommendations
    if(len(dish_rating_df) >= 5):

        print("Recommend")
        model = tc.load_model("s3://paletterecommendermodel/finalized_recommender_model/")
        item_sim_recomm = model.recommend(users=[user_id],k=50)
        recs = item_sim_recomm['dish_id']

        df = get_dishes()
        new_dish_df = []

        #filter out all that were not added within the last two weeks, add new dishes to the new_dish_df
        for dish in df:
        
                pyth_date = datetime.strptime(dish['createdAt'], '%Y-%m-%dT%H:%M:%S.%fZ')
                if (today - margin) <= pyth_date <= today:
                    new_dish_df.append(dish)


        # append recommendation ids to the rec list
        rec_list = []
        for rec in recs:
            rec_list.append(rec)

        # query the database for the recommended dishes using recommendation ids
        rec_dish_query = """query {
  		dishByIds (_ids:""" + json.dumps(rec_list) + """){
			description
            createdAt
            _id
  		}}"""

        url = 'https://palette-backend.herokuapp.com/graphql'
        r = requests.post(url, json={'query': rec_dish_query})
        json_data = json.loads(r.text)
        rec_dish_df = json_data['data']['dishByIds']

        # if there are any new_dishes, figure out which is most similar to a dish on the recommended list using semantic similarity
        # then add this dish to the list returned to the user
        print(new_dish_df)
        if len(new_dish_df) > 0:
            
            rand_dish = random.choice(new_dish_df)
            
            # add the most similar dish to the recommendation list
            rec_list.append(rand_dish["_id"])
        
        # return the recommended dishes
        return jsonify(rec_list)

    # this is a new user, which means we need to reutrn the 20 most popular dishes
    else:

        # 
        print("Popular")
        dish_df = get_dishes()
        dish_df.sort(key=extract_average, reverse=True)
        dish_df = dish_df[0:19]

        rec_list = []
        for rec in dish_df:
            rec_list.append(rec['_id'])

        return jsonify(rec_list)




    
def get_dish_ratings(user_id):
    user_id = "\""+user_id+"\""

    # with user id, query database and determine if user is 'still new'
    # can determine if user is new based on how many dishes they've rated 
    # if the user has rated 5 or more dishes, we have enough data to start sending recommendations 

    dish_rating_query = """query  {
		dishRatingMany (filter: {user_id: """ + user_id +  """}) {
			_id
			dish_id
			user { name }
			rating
			review
			createdAt
			dish { 
				dish_name 
				restaurant { name }
				}
		}
	}"""

    # print(dish_rating_query)
    
    url = 'https://palette-backend.herokuapp.com/graphql'
    r = requests.post(url, json={'query': dish_rating_query})
    # print(r.status_code)
    # print(r.text)

    json_data = json.loads(r.text)
    return json_data['data']['dishRatingMany']

def get_dishes():
     #pick a new dish, most similar to the recommended ones
    dish_query = """query {
    dishMany {
        description
        average_rating
        createdAt
        _id
    }}"""

    url = 'https://palette-backend.herokuapp.com/graphql'
    r = requests.post(url, json={'query': dish_query})
    # print(r.status_code)
    # print(r.text)
    json_data = json.loads(r.text)
    return json_data['data']['dishMany']

# A welcome message to test our server
@app.route('/')
def index():
    
    return "<t>bee boop this is a dummy server</t>"

if __name__ == '__main__':

    # Threaded option to enable multiple instances for multiple user access support
    port = int(os.environ.get('PORT', 5000))
    app.run(port=port)

    print("starting to load model")
    # Load the model: this is a big file, can take a while to download and open
    glove = api.load("glove-wiki-gigaword-50")    
    similarity_index = WordEmbeddingSimilarityIndex(glove)
    print("load_model")

