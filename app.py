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
from sentence_transformers import SentenceTransformer, util
from datetime import date, timedelta, datetime

# app.py
app = Flask(__name__)



def extract_average(json):
    try:
        return int(json['average_rating'])
    except KeyError:
        return 0

today = datetime.today()
margin = timedelta(days = 14)
lang_model = SentenceTransformer('paraphrase-distilroberta-base-v1')

@app.route('/rec', methods=['POST'])
def rec():
    jsdata = request.get_json()
    # print(jsdata['user_id'])
    user_id = jsdata['user_id']

    dish_rating_df = get_dish_ratings(user_id)

    if(len(dish_rating_df) >= 5):

        print("Recommend")
        model = tc.load_model("s3://paletterecommendermodel/finalized_recommender_model/")
        item_sim_recomm = model.recommend(users=[user_id],k=50)
        recs = item_sim_recomm['dish_id']

        df = get_dishes()
        new_dish_df = []

        #filter out all that were not added within the last two weeks
        for dish in df:
        
                pyth_date = datetime.strptime(dish['createdAt'], '%Y-%m-%dT%H:%M:%S.%fZ')
                if (today - margin) <= pyth_date <= today:
                    new_dish_df.append(dish)

        print(new_dish_df)

        rec_list = []
        for rec in recs:
            rec_list.append(rec)

        rec_dish_query = """query {
  		dishByIds (_ids:""" + json.dumps(rec_list) + """){
			description
            createdAt
            _id
  		}}"""

        url = 'https://palette-backend.herokuapp.com/graphql'
        r = requests.post(url, json={'query': rec_dish_query})
        # print(r.status_code)
        # print(r.text)
        json_data = json.loads(r.text)
        rec_dish_df = json_data['data']['dishByIds']
        max_score = 0
        max_dish = new_dish_df[0]['_id']

        for dish in new_dish_df:
            for rec in rec_dish_df:
                #Compute embedding for both descriptions
                embeddingsDish = lang_model.encode(dish['description'], convert_to_tensor=True, show_progress_bar=False)
                embeddingsRec = lang_model.encode(rec['description'], convert_to_tensor=True, show_progress_bar=False)
                
                #Compute cosine-similarits
                cosine_scores = util.pytorch_cos_sim(embeddingsDish, embeddingsRec)

                if max_score < cosine_scores:
                    max_dish = dish['_id']
                    max_score = cosine_scores
            
            
        print(max_dish, max_score)
        rec_list.append(max_dish)

        return jsonify(rec_list)

    else:

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
    app.run(threaded=True, port=7000)
