import turicreate as tc
import pickle
import json
import numpy as np
import pandas as pd
import pymongo
from dotenv import load_dotenv

load_dotenv()
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')

client = pymongo.MongoClient('mongodb+srv://'+USERNAME+':'+PASSWORD+'@cluster0.zwmnc.mongodb.net/myFirstDatabase')

db = client.myFirstDatabase
dishratings_col = db.dishratings
cursor = dishratings_col.find()
list_cur = list(cursor)
df = pd.DataFrame(list_cur)
df = df.drop(['_id','rating_id_num','review'], axis=1)

rec_data = tc.SFrame(df)
item_sim_model = tc.item_similarity_recommender.create(rec_data, user_id='user_id', item_id='dish_id', target='rating', similarity_type='cosine')

filename = 'finalized_recommender_model'
item_sim_model.save('finalized_recommender_model')