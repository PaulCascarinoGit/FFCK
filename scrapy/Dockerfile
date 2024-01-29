# Utilisez l'image de base Python 3.11
FROM python:3.11

# Définissez le répertoire de travail dans le conteneur
WORKDIR /app

# Copiez le fichier requirements.txt du répertoire local vers le répertoire de travail du conteneur
COPY ./scrapy/requirements.txt /app/requirements.txt

# Installez les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiez tout le contenu du répertoire local dans le répertoire de travail du conteneur
COPY ./scrapy /app

WORKDIR /app/WebCrawler/WebCrawler/spiders
# Commande par défaut à exécuter lors du démarrage du conteneur
CMD ["scrapy", "crawl", "classement_ffck"]
