# utilise une image python:3.8  préexistante à partir un autre Dockerfile.
FROM python:3.11

# définis le répertoire de travail dans le conteneur
WORKDIR /app

# ajoutes les fichier du dossier courant dans le contexte de Docker.
COPY . .

# execution des commandes
RUN pip install -r /app/requirements.txt

# définis le répertoire de travail dans le conteneur
WORKDIR /app/WebCrawler/WebCrawler/spiders

# déterminer la commande devant être lancée.
CMD ["scrapy", "crawl", "classement_ffck", "-o", "output.csv"]

