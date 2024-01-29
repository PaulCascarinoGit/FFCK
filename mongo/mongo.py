from pymongo import MongoClient

def create_database():
    client = MongoClient("mongodb://mongo:27017/")
    db = client["ma_base_de_donnees"]
    print("Base de données créée avec succès.")

if __name__ == "__main__":
    create_database()
