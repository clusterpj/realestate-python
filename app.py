from flask import Flask, render_template
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/realestate"
mongo = PyMongo(app)

@app.route('/')
def home(): 
    return render_template('home.html', title='Real Estate App')

@app.route('/listings')
def listings():
    # Code to fetch data and render the listings page
    listings = mongo.db.listings.find()
    return render_template('listings.html', listings=listings, title='Real Estate App')

@app.route('/listings/<listing_id>')
def listing_details(listing_id):
    # Code to fetch data for a specific listing and render the listing details page
    listing = mongo.db.listings.find_one({"_id": ObjectId(listing_id)})
    return render_template('listing_details.html', listing=listing, title='Real Estate App')

@app.route('/about')
def about():
    return render_template('about.html', title='Real Estate App')

@app.route('/news')
def news():
    return render_template('news.html', title='Real Estate App')

@app.route('/contact')
def contact():
    return render_template('contact.html', title='Real Estate App')

@app.route('/login')
def login():
    return render_template('login.html', title='Real Estate App')

@app.route('/signup')
def signup():
    return render_template('signup.html', title='Real Estate App')

if __name__ == '__main__':
    app.run(debug=True)
