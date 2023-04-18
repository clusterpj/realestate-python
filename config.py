import os

UPLOAD_FOLDER = 'static/uploads/'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# configure mail settings
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = 'jisgore@gmail.com'  # replace with your Gmail address
MAIL_PASSWORD = '#'  # replace with your Gmail password or app-specific password
MAIL_DEFAULT_SENDER = 'jisgore@gmail.com'  # replace with your Gmail address

class Config:
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads').rstrip(os.sep)
    SECRET_KEY = "dTLma3M6KkGrDf"
    MONGO_URI = "mongodb+srv://realestateadmin:C0rP0r4lJ1sG0re@clusterstate.ym3x1zp.mongodb.net/clusterestate"
    DEBUG = True
