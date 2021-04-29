import os
import pickle
import pandas as pd
import turicreate as tc
import sys
import numpy
from sklearn.linear_model import LinearRegression
from flask import Flask, request, jsonify
import requests
# # from flask_cors import CORS, cross_origin
import json

# app.py
app = Flask(__name__)

os.environ["AWS_ACCESS_KEY_ID"] = 'AKIAJ2AEWRGCKALCBIKQ'
os.environ["AWS_SECRET_ACCESS_KEY"] = "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"

def extract_average(json):
    try:
        return int(json['average_rating'])
    except KeyError:
        return 0

@app.route('/rec', methods=['POST'])
def rec():
    jsdata = request.get_json()
    print(jsdata['user_id'])
    user_id = jsdata['user_id']

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

    print(dish_rating_query)
    
    url = 'https://palette-backend.herokuapp.com/graphql'
    r = requests.post(url, json={'query': dish_rating_query})
    print(r.status_code)
    print(r.text)

    json_data = json.loads(r.text)
    dish_rating_df = json_data['data']['dishRatingMany']

    if(len(dish_rating_df) >= 5):

        model = tc.load_model("s3://paletterecommendermodel/finalized_recommender_model/")
        item_sim_recomm = model.recommend(users=[user_id],k=50)
        recs = item_sim_recomm['dish_id']


        rec_list = []
        for rec in recs:
            rec_list.append(rec)

        return jsonify(rec_list)

    else:

        popular_dish_query = """query {
  		dishMany {
            average_rating
			_id
  		}}"""

        url = 'https://palette-backend.herokuapp.com/graphql'
        r = requests.post(url, json={'query': popular_dish_query})
        print(r.status_code)
        print(r.text)

        json_data = json.loads(r.text)
        dish_df = json_data['data']['dishMany']
        dish_df.sort(key=extract_average, reverse=True)
        dish_df = dish_df[0:19]

        rec_list = []
        for rec in dish_df:
            rec_list.append(rec['_id'])

        return jsonify(rec_list)


        # query dishes for the 10 most popular

    # if more than 5 recommends -> recommendations


    # if less than 5 recommends -> top 10 most popular dishes

        # query for all dishes
        # sort based on rating
        # return top 10 



    # open the model, and get recommendations
    # item_sim_model_open = tc.load_model('finalized_recommender_model')
    # item_sim_recomm = item_sim_model_open.recommend(users=[user_id],k=5)
    # recs = item_sim_recomm['dish_id']

    

    

# A welcome message to test our server
@app.route('/')
def index():
    
    return "<t>bee boop this is a dummy server</t>"

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=7000)
