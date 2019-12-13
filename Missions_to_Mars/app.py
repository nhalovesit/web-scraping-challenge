
from flask import Flask, render_template #return real html post processed
import pymongo
import scrape_mars

#connect to MongoDB, mars_db
client = pymongo.MongoClient('mongodb://localhost:27017')
mongo = client.mars_db

app = Flask(__name__) # to get Flask working

@app.route("/") # for Flask
def index():
    mars = mongo.db.mars.find_one()
    return render_template("index.html",mars=mars)

@app.route("/scrape")
def scrape():
    mars = mongo.db.mars
    # Run the scrape function
    mars_data = scrape_mars.scrape()

    # Update the Mongo db using update and upsert=True
    # mongo.db.collection.update({}, mars_data, upsert=True)
    mars.update({}, mars_data, upsert=True)
    return "Scraping completed"
    
if __name__== "__main__":
    app.run(debug=True)

        #comment use #
    ''' triple quote to do a block comment'''