import turicreate as tc
import pickle
import json
import numpy as np
import pandas as pd
import pymongo
from dotenv import load_dotenv
import os
import boto3

load_dotenv()
AWSAccessKeyId = os.getenv('AWSAccessKeyId')
AWSSecretKey = os.getenv('AWSSecretKey')
REGION= os.getenv('REGION')

print(AWSAccessKeyId, AWSSecretKey, REGION)

os.environ["AWS_ACCESS_KEY_ID"] = AWSAccessKeyId
os.environ["AWS_SECRET_ACCESS_KEY"] = AWSSecretKey
model = tc.load_model("s3://paletterecommendermodel/finalized_recommender_model/")

item_sim_recomm = model.recommend(users=[1],k=5)
recs = item_sim_recomm['dish_id']
print(item_sim_recomm)
# print("HERE")
# for bucket in s3.buckets.all():
#     print(bucket.name)

# USERNAME = os.environ.get('USERNAME')
# PASSWORD = os.environ.get('PASSWORD')

# print(USERNAME)
# print(PASSWORD)

# USERNAME = 'paletteadmin'
# PASSWORD = 'Dartmouthgreen'

# auth_string = 'mongodb+srv://'+USERNAME+':'+PASSWORD+'@cluster0.zwmnc.mongodb.net/myFirstDatabase'
# print(auth_string)
# client = pymongo.MongoClient(auth_string)

# # client = pymongo.MongoClient('mongodb+srv://paletteadmin:Dartmouthgreen@cluster0.zwmnc.mongodb.net/myFirstDatabase')

# db = client.myFirstDatabase
# dishratings_col = db.dishratings
# cursor = dishratings_col.find()

# list_cur = list(cursor)
# df = pd.DataFrame(list_cur)
# df = df.drop(['_id','rating_id_num','review'], axis=1)
# print(df)

# rec_data = tc.SFrame(df)
# item_sim_model = tc.item_similarity_recommender.create(rec_data, user_id='user_id', item_id='dish_id', target='rating', similarity_type='cosine')

# filename = 'finalized_recommender_model'
# item_sim_model.save('finalized_recommender_model')