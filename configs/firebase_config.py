import firebase_admin
from firebase_admin import credentials
import os
# Get firebasePrivateKey.json path
current_file_path = os.path.abspath(__file__)
parent_of_parent_path = os.path.abspath(os.path.join(current_file_path, "../../"))
firebase_private_key_path = os.path.join(parent_of_parent_path, "firebasePrivateKey.json")

# Config
cred = credentials.Certificate(firebase_private_key_path)
firebase_admin.initialize_app(cred, {
    'storageBucket': 'embedded-2fcfe.appspot.com'
})