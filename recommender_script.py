import turicreate as tc
import pickle
import json
import numpy as np
import pandas as pd
import pymongo
from dotenv import load_dotenv
import os
import boto3

USERNAME = os.environ["USERNAME"]
PASSWORD = os.environ["PASSWORD"]

auth_string = 'mongodb+srv://'+USERNAME+':'+PASSWORD+'@cluster0.zwmnc.mongodb.net/myFirstDatabase'
client = pymongo.MongoClient(auth_string)

db = client.myFirstDatabase
dishratings_col = db.dishratings
cursor = dishratings_col.find()

list_cur = list(cursor)
df = pd.DataFrame(list_cur)
df = df.drop(['_id','rating_id_num','review'], axis=1)

rec_data = tc.SFrame(df)
item_sim_model = tc.item_similarity_recommender.create(rec_data, user_id='user_id', item_id='dish_id', target='rating', similarity_type='cosine')

filename = 's3://paletterecommendermodel/finalized_recommender_model/'
item_sim_model.save('s3://paletterecommendermodel/finalized_recommender_model/')