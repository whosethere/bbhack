from pymongo import MongoClient

def get_mongo_conenction(collection_name):
    
    client = MongoClient('mongodb+srv://') #baza danych
    db = client['endurotrails']
    collection = db[collection_name]

    return collection
