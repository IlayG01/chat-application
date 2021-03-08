from user import User
from pymongo import MongoClient
from werkzeug.security import generate_password_hash

client = MongoClient("ConnectionString")
chat_db = client.get_database("ChatDB")
user_collection = chat_db.get_collection("users")


def save_user(username, email, password):
    user_collection.insert_one({
        '_id': username,
        'email': email,
        'password': generate_password_hash(password)
    })


def get_user(username):
    user = user_collection.find_one({
        "_id": username
    })
    return User(user['_id'], user['email'], user['password']) or None

# save_user("Josh", "josh@gmail.com", "josh")
