from pymongo import MongoClient

# Connexion à la base de données MongoDB
client = MongoClient('mongodb://mongo:27017')
db = client['FFCK_BDD']  # Remplacez par le nom de votre base de données

# Exemple de récupération de données depuis une collection
collection = db['ffck_collection']  # Remplacez par le nom de votre collection

# Récupération de tous les documents dans la collection
result = collection.find({'Category': 'C'})

# Affichage des résultats
for document in result:
    print(document)

# Fermeture de la connexion
client.close()
