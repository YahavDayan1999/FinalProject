from pymongo import MongoClient

conn_uri = "mongodb+srv://omriportal123:8Nktq5SjyM2ViWnt@cluster0.s4le1oe.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

db_client = MongoClient(conn_uri)
db_client = db_client["my_db"]
users_collection = db_client["users"]
shows_collection = db_client["shows"]
artists_collection = db_client["artists"]
venues_collection = db_client["venues"]
purchases_collection = db_client["purchases"]
