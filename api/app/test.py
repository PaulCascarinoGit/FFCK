
from pymongo import MongoClient
import time
import pandas as pd


mongo_ready = False
while not mongo_ready:
    try:
        # Try to connect to MongoDB
        client = MongoClient('mongo:27017', serverSelectionTimeoutMS=30000, socketTimeoutMS=30000, connectTimeoutMS=30000)
        db = client['FFCK_BDD']
        collection = db['ffck_collection']
        mongo_ready = True
        print('cest ok')
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        print("Retrying in 5 seconds...")
        time.sleep(5)

result = collection.find()
df = pd.DataFrame(list(result))
print('Result : ')
print(str(df))

print(f"Number of documents in 'ffck_collection': {collection.count_documents({})}")