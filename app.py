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
import os
UPLOAD_FOLDER = 'static/uploads/'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

import os
os.environ['FLASK_ENV'] = 'development'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads').rstrip(os.sep)
app.run(debug=True)
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
    def __init__(self, title, image, gallery_images, price, bedrooms, bathrooms, size):
        self.title = title
        self.image = image
        self.gallery_images = gallery_images
        self.price = price
        self.bedrooms = bedrooms
        self.bathrooms = bathrooms
        self.size = size

    def to_dict(self):
        return {
            "title": self.title,
            "image": self.image,
            "gallery_images": self.gallery_images,
            "price": self.price,
            "bedrooms": self.bedrooms,
            "bathrooms": self.bathrooms,
            "size": self.size,
        }

@app.route('/')
def home(): 
    return render_template('home.html', title='Real Estate App')

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
def logout():
    logout_user()
    return redirect(url_for('home'))

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

@app.route('/admin/create_property', methods=['GET', 'POST'])
@login_required
def create_property():
    if request.method == 'POST':
        title = request.form.get('title')
        image = request.files['image']
        image_gallery = request.files.getlist('image_gallery[]')
        price = request.form.get('price')
        bedrooms = request.form.get('bedrooms')
        bathrooms = request.form.get('bathrooms')
        size = request.form.get('size')


        # Save the main image
        image_filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        # Save the image gallery files
        gallery_filenames = []
        for gallery_image in image_gallery:
            gallery_filename = secure_filename(gallery_image.filename)
            gallery_image.save(os.path.join(app.config['UPLOAD_FOLDER'], gallery_filename))
            gallery_filenames.append(os.path.join('uploads', gallery_filename))

        # Create the new listing
        new_listing = Listing(
            title,
            os.path.join('uploads', image_filename),
            gallery_filenames,
            float(price),
            int(bedrooms),
            float(bathrooms),
            float(size)
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
