from pymongo import MongoClient
from app.core.config import get_settings    

# MongoDB connection
# print(get_settings().MONGODB_URI)
client = MongoClient(get_settings().MONGODB_URI)
db = client[get_settings().DATABASE_NAME]

# Collections
gift_cards = db['gift_cards']

def get_db():
    return db 