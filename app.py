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

#small change


@app.route('/rec/', methods=['POST'])
def rec():

    # could rerun and train model 
    # OR 
    # heroku dyno -> rerun script based on triggers, set up in proc file 

    jsdata = request.get_json()
    # would be an id in JSDATA
    # call jsonify on whatever object made 

    return jsonify(jsdata)

@app.route('/rec', methods=['POST'])
def rec():
    jsdata = request.get_json()
    print(jsdata['user_id'])
    user_id = jsdata['user_id']
    return jsonify(jsdata)

# A welcome message to test our server
@app.route('/')
def index():
    return "<h1>beep boop I am a dummy server</h1>"

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=7000)
