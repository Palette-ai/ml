# README: Machine Learning 

## app.py

App.py is the heart of the machine learning used to make recommendations for the recommendation page of our app. This is a flask server written in python that is being hosted on Heroku.

When a user logs in and navigates to the recommendation page, they are presented with personalized dish recommendations for them.

**How it works**

When a user navigates to the recommendation page, the front end makes a post call to the ml server with the user's mongodb _id.

If the user has made 5 or more reviews (dish_ratings) on different dishes, then the ml server uses turicreate to load the recommendation model from the amazon s3 bucket where it is stored. We then get the top 20 (at most) recommendations for the current user.

After getting the top 20 recommended dishes for the current user, we consider how to present new dishes to the user, dishes that were added within the last 14 days.

**We originally solved this problem the following way:** We query all new dishes, then check the semantic similarity of the descriptions of the new dishes to the descriptions of the recommended dishes. The new dish with the greatest semantic similarity is inserted into the list of recommended dishes which is then sent to back to the front end as a list of dish_ids. The idea here being that the most relevant new dishes would be shown to the user. However, we soon realized this method would bury new dishes that have very dissimilar descriptions to the dishes currently in the database. For example, for the first Ethiopian restaurant to enter dishes into the database, their dishes would be very unlikely to ever be shown to users using this semantic similarity method.

**How we currently solve this problem:** When we initially discussed solving the cold start problem with Joe, he suggested both semantic similarity and random choice as viable options, so now instead of semantic similarity we go with random choice. We query all new dishes, then randomly select a new dish to add to the list of recommended dishes and send to the user. This way, each new dish has a theoretically equal chance of being clicked on, and we do not penalize restaurants for having dishes that are different from the current set of dishes in the database, which could result in algorithmic racism. They trade off is a random dish could be less relevant to a user, but across the whole body of users this will be better for the restaurant and result in far greater data collection for more unique restaurants in comparison with the semantic similarity method. By showing our users the occasional random dish, we also expect to learn more useful information about them that helps us further develop our recommendation model.


## recommender_script.py


The recommender script is triggered once a day at 12am. This script does two things.

**First:** The script loads the recommendation model from the amazon s3 bucket and then trains the model on all the dish ratings, accounting for new dish ratings entered that day. After retraining the model, the model is loaded back into the amazon s3 bucket. 

**Second:** The script recalculates all the average rating values for the dishes, accounting for the new dish ratings to come in that day.
