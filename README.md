# README: Machine Learning 

## app.y

App.py is the heart of the machine learning used to make recommendations for the recommendation page of our app. This is a flask server written in python that is being hosted on heroku. 

When a user logs in and navigates to the recommendation page, they are presented with personalized dish recommendations for them. 

**How it works**

When a user navigates to the recommendation page, the front end makes a post call to the ml server with the user's mongodb _id. 

If the user has made 5 or more reviews (dish_ratings) on different dishes, then the ml server uses turicreate to load the recommendation model from the amazon s3 bucket where it is stored. We then get the top 20 (at most) recommendations for the current user. 

After getting the top 20 recommended dishes for the current user, we consider how to present new dishes to the user, dishes that were added within the last 14 days. 

We originally solved this problem the following way: We query all new dishes, then check the semantic similarity of the descriptions of the new dishes to the descriptions of the recommended dishes. The new dish with the greatest semantic similarity is inserted into the list of recommended dishes which is then sent to back to the front end as a list of dish_ids.  


## recommender_script.py



