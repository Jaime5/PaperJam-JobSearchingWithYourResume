from os import makedirs, path

# Enable debug mode.
DEBUG = True

# Secret key for session management. You can generate random strings here:
# https://randomkeygen.com/
SECRET_KEY = 'my precious'

BASE_PATH = path.dirname(path.abspath(__file__))
UPLOAD_FOLDER = path.join(BASE_PATH, "uploads")

# MAKE SURE TO CREATE UPLOADS FOLDER
if not path.exists(UPLOAD_FOLDER):
    makedirs(UPLOAD_FOLDER)
