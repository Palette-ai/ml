import turicreate as tc
import pickle
import json
import numpy as np
import pandas as pd
import pymongo
from dotenv import load_dotenv
import os
from bson.objectid import ObjectId

# get authentication credentials
USERNAME = os.environ["USERNAME_DB"]
PASSWORD = os.environ["PASSWORD_DB"]

# connect to mongo
auth_string = 'mongodb+srv://'+USERNAME+':'+PASSWORD+'@cluster0.zwmnc.mongodb.net/myFirstDatabase'
client = pymongo.MongoClient(auth_string)

# recommender script, updates the recommendation model stored in an amazon s3 bucket
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

# average rating script, updates the average ratings for each dish using the ratings that were added during the day 
dishes = db.dishes
dish_cursor = dishes.find()
list_cur_dish = list(dish_cursor)
dish_df = pd.DataFrame(list_cur_dish)
dish_df = dish_df.drop(['dish_id_num', 'dish_name','restaurant_id', 'features', 'description', 'tags', 'rating_ids', 'createdAt', 'price', 'img'], axis=1)

for row in dish_df.iterrows():
    dish_id = row[1]['_id']
    
    ratings_cursor = dishratings_col.find({'dish_id': str(dish_id)})
    ratings_cursor_list = list(ratings_cursor)
    
    total = 0
    rating_sum = 0
    
    if(len(ratings_cursor_list) > 0):
        
        for rating in ratings_cursor_list:
   
            total+=1
            rating_sum+=rating['rating']
            
        avg = rating_sum/total
        
        res = dishes.update_one({'_id': ObjectId(str(dish_id))}, {"$set": {'average_rating': round(avg, 1)}})
