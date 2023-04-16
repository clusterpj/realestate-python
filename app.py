from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, render_template
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from flask_login import logout_user
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
from flask_mail import Message
from config import Config
import os
import pdb

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = "dTLma3M6KkGrDf"

app.config["MONGO_URI"] = "mongodb://localhost:27017/cluster_main"
mongo = PyMongo(app)

# the toolbar is only enabled in debug mode:
app.debug = True

# set a 'SECRET_KEY' to enable the Flask session cookies
app.config['SECRET_KEY'] = 'PC9D2GAZGXwSz6'

toolbar = DebugToolbarExtension(app)

# Set up Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']

@login_manager.user_loader
def load_user(user_id):
    # Load user from the database or user data store
    user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    if user_data:
        user = User(user_data)
        return user

class Listing:
    def __init__(self, title, image, price, bedrooms, bathrooms, size, featured=False):
        self.title = title
        self.image = image
        self.price = price
        self.bedrooms = bedrooms
        self.bathrooms = bathrooms
        self.size = size
        self.featured = featured

    def to_dict(self):
        return {
            "title": self.title,
            "image": self.image,
            "price": self.price,
            "bedrooms": self.bedrooms,
            "bathrooms": self.bathrooms,
            "size": self.size,
            "featured": self.featured
        }

@app.route('/')
def home():

    # Get featured listings from database
    featured_listings = list(mongo.db.listings.find({'featured': True}))

    # Format the price of each featured listing
    for listing in featured_listings:
        listing['price'] = '{:,.0f}'.format(int(listing['price']))
        
    return render_template('home.html', featured_listings=featured_listings)

@app.route('/listings')
def listings():
    # Fetch listings from the database
    listings_cursor = mongo.db.listings.find()

    # Convert the cursor to a list of dictionaries
    listings = [listing for listing in listings_cursor]

    # Format the price and size of each listing
    for listing in listings:
        listing['price'] = format_number(listing['price'])
        listing['size'] = format_number(listing['size'])

    return render_template('listings.html', listings=listings)

@app.route('/listings/<listing_id>')
def property_details(listing_id):
    # Code to fetch data for a specific listing and render the property details page
    listing = mongo.db.listings.find_one({"_id": ObjectId(listing_id)})
    return render_template('listing_details.html', listing=listing, title='Real Estate App')

@app.route('/about')
def about():
    return render_template('about.html', title='Real Estate App')

@app.route('/news')
def news():
    return render_template('news.html', title='Real Estate App')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        msg = Message(subject='New message from Real Estate App',
                      recipients=['jisgore@gmail.com'],  # replace with your email address
                      body=f'Name: {name}\nEmail: {email}\nMessage: {message}')

        mail.send(msg)

        return render_template('success.html')

    return render_template('contact.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']

    # Do something with the form data, e.g. send an email

    flash('Your message has been sent!')
    return redirect(url_for('contact'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_data = mongo.db.users.find_one({'username': username})

        if user_data and check_password_hash(user_data['password'], password):
            user = User(user_data)
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home'))

        flash('Invalid username or password.', 'danger')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check if the username already exists
        existing_user = mongo.db.users.find_one({'username': username})

        if existing_user is None:
            # Hash the password
            hashed_password = generate_password_hash(password)
            # Add the new user to the database
            mongo.db.users.insert_one({'username': username, 'password': hashed_password})
            flash('Account created successfully. Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('A user with that username already exists.', 'danger')

    return render_template('signup.html', title='Real Estate App')

@app.route('/logout')
@login_required
def logout():
    # Clear flashed messages
    session.pop('_flashes', None)

    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/admin')
@login_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/admin/all_properties')
@login_required
def all_properties():
    listings = mongo.db.listings.find()
    return render_template('/admin/all_properties.html', listings=listings)

@app.route('/admin/delete_property/<listing_id>', methods=['POST'])
@login_required
def delete_property(listing_id):
    mongo.db.listings.delete_one({'_id': ObjectId(listing_id)})
    flash('Property deleted successfully', 'success')
    return redirect(url_for('all_properties'))

@app.route('/admin/property_types')
@login_required
def property_types():
    # Fetch all property types and render the property_types page
    return render_template('admin/property_types.html')

@app.route('/admin/property_amenities')
@login_required
def property_amenities():
    # Fetch all property amenities and render the property_amenities page
    return render_template('admin/property_amenities.html')

@app.route('/admin/property_locations')
@login_required
def property_locations():
    # Fetch all property locations and render the property_locations page
    return render_template('admin/property_locations.html')

@app.route('/toggle_featured', methods=['POST'])
@login_required
def toggle_featured():
    listing_id = request.form.get('listing_id')
    featured = request.form.get('featured') == 'true'
    mongo.db.listings.update_one({"_id": ObjectId(listing_id)}, {"$set": {"featured": featured}})
    return {"success": True}

@app.route('/admin/create_property', methods=['GET', 'POST'])
@login_required
def create_property():
    if request.method == 'POST':

        featured = request.form.get('featured') == 'on'

        # Assign the values of the form inputs to variables
        title = request.form.get('title')
        price = request.form.get('price')
        bedrooms = request.form.get('bedrooms')
        bathrooms = request.form.get('bathrooms')
        size = request.form.get('size')
        image = request.files['image']

        # Save the main image
        image_filename = secure_filename(image.filename).replace('\\', '/')
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        # Create the new listing
        new_listing = Listing(
            title,
            'uploads/' + image_filename,
            float(price),
            int(bedrooms),
            float(bathrooms),
            float(size),
            featured
        )

        # Insert the new listing into the database
        mongo.db.listings.insert_one(new_listing.to_dict())

        flash('New listing created successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/create_property.html')


def format_number(value):
    return "{:,}".format(value)

if __name__ == '__main__':
    app.run(debug=True)
