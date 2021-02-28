import os
import pickle
import pandas as pd
import turicreate as tc
import sys
import numpy
from sklearn.linear_model import LinearRegression
from flask import Flask, request, jsonify
# # from flask_cors import CORS, cross_origin
import json

# app.py
app = Flask(__name__)

@app.route('/rec', methods=['POST'])
def rec():
    jsdata = request.get_json()
    print(jsdata['user_id'])
    user_id = jsdata['user_id']

    item_sim_model_open = tc.load_model('finalized_recommender_model')
    item_sim_recomm = item_sim_model_open.recommend(users=[user_id],k=5)
    recs = item_sim_recomm['dish_id']

    rec_list = []
    for rec in recs:
        rec_list.append(rec)

    return jsonify(rec)

# A welcome message to test our server
@app.route('/')
def index():
    
    return "<t>bee boop this is a dummy server</t>"

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=7000)
