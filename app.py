import os
import pickle
import pandas as pd
import sys
import numpy
from sklearn.linear_model import LinearRegression
from flask import Flask, request, jsonify
# # from flask_cors import CORS, cross_origin
import json

# app.py
app = Flask(__name__)


@app.route('/hello/', methods=['POST'])
def hello():
    jsdata = request.get_json()
    return jsonify(jsdata)

# A welcome message to test our server
@app.route('/')
def index():
    return "<h1>beep boop I am a dummy server</h1>"

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=7000)
