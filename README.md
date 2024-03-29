# Données du canoë-kayak en France
Projet de data-engineering réalisé par Paul Cascarino et Mathis Quinio-cosquer

## Sommaire
1. [Introduction](#introduction)
2. [User Guide](#userguide)
3. [Developper Guide](#developperguide)
4. [Analyse des fonctionnalités](#Analyse)


## Introduction

### Présentation des données
Nous allons travailler sur les données de la Fédération Française de Canoë-Kayak (FFCK) en slalom. Pour expliquer rapidement le canoë-kayak et surtout les données que nous avons : 

![Classement](https://git.esiee.fr/cascarip/pythonviz/-/raw/main/image/classement.JPG)

 * Dans le même sport nous avons plusieurs embarcations (le canoë et le kayak) que nous nommons respectivement __C1__ et __K1__ et nous rajoutons le canoë à 2 place __C2__.
 * C'est un sport pratiqué par les __hommes__ et les __femmes__ et nous avons bien une distinction dans les disciplines.
 * Nous avons aussi plusieurs catégories d'âges allant de -15 ans (__U15__) à +35 ans (__M35__).
 * Nous avons plusieurs niveaux nationals de compétition allant de __N1__ qui sont les tout meilleurs en Frances suivi de __N2__, __N3__, et du niveau régional : __Reg__
 * Chaque athlète appartient à un unique __club__.
 * Le niveau de chaque athlète est donné par une __Moyenne__ qui est calculés selon les résultats de l'athlète et dans sa discipline dans l'année : plus la moyenne est basse, plus l'athlète est mathématiquement fort. La moyenne est arrangé en fonction du sexe et de l'embarcation pratiqué.

 ### Les objectifs de ce projet

 L'objectif de ce projet est d'observer la répartition des athlètes pratiquant le canoë-kayak slalom en France. On pourra observer en fonction des âges, du sexe, de la région des clubs la répartition des athlètes. Cela peut permettre d'axer les études sur le sujet sur des points précis si l'on trouver des corrélations et d'avoir une visualisation plus globale.




## User guide

Pour lancer notre dashboard, il suffit de se mettre dans le répertoire du projet et d'effectuer la commande : 
__docker-compose up --build__

Notre scraping vas commencer ainsi ue le dashboard et la base de données vont être refresh en __temps réel__

Pour accéder au dashboard, ,il suffit de se connecter à l'addresse : http://127.0.0.1:8050/

Le scraping se fait en continue, il faut refresh la page du dashboard pour voir le données en fonction du scraping en temps réel.


 
## Developperguide

### Scraping des données

#### Option A avec Selenium (non validé impossibilité d'utiliser Docker)
Nous voullons dans un premier temps scrapper les données du site : https://www.ffck.org/slalom/competitions/classement_national/

C'est un site dynamique, les textes sont générés avec du Javascript donc nous avons dans un premier temps utilisé __Selenium__ pour y extraire les données.

 Installer le WebDriver à l'addresse : 

https://sites.google.com/chromium.org/driver/downloads?authuser=0

##### Lancement du scraping : 

Ouvrez le fichier config.ini dans un éditeur de texte et faire correspondre les chemins pour le navigateur Chrome ('binary_path') et le Webdriver ('path') et enregistrez le.

Modifiez ensuite les variables : 
[Tester le scraping]
test = True si vous voulez tester le scraping, False si non
date_start = date de début en years-month-day
date_end = date de fin en years-month-day
intervalle_day = Laissez à 7 pour faire correspondre une semaine
nbr_data = nombre de data à récupérer, 100 permet de faire vite

Nous pouvons maintenant executer notre application en effectuant la commande : 
```python main.py```

#### Option B Scrapy sur un site statique

Ainsi nous allons utiliser Scrapy en coordination avec Docker afin de réaliser notre Scraping.

Il nous faut un site statique pour faciliter le processus, miracle l'ancien site de la ffck est toujours
disponible et est codé avec html/php. Ainsi les balises sont statiques et que donc sont accessible facilement
vias Scarpy ! 

http://www.ffcanoe.asso.fr/eau_vive/slalom/classement/embarcations/index

De plus nous avons accès à toutes les années précédentes jusqu'à 2010. Pour un temps de récupération et de codage
nettement réduit.

Nous créons donc notre dossier avec notre framework Scrapy.

<img src="images/architecture.png" alt="architecture" class="align-center" /

Notre framework est articulé avec plusieurs composants qui gèrent chacun un
rôle différent. Nous allons les détailler.

-   Les **Spiders** : permettent de naviguer sur un site et de
    référencer les règles d'extraction d la donnée. 
    Dans notre exemple nous allons passer de pages en pages  pour avoir accès à tous les athlètes :
    ```
    # Gérer la pagination
    next_page = response.css('div.paging a.next::attr(href)').extract_first()
    if next_page:
        yield scrapy.Request(url=response.urljoin(next_page), callback=self.parse)
    ```

    Nous allons aussi défiler d'années en années pour observer leurs évolutions dans le temps: 
    ```
    A faire
    ```

    Il nous suffit d'extraire nos données avec : 
    ```
     for row in response.xpath('//table[@cellpadding="0" and @cellspacing="0"]/tr[@class="paire" or @class="impaire"]'):
            item = ClassementFfckItem()
            item['Rank'] = row.xpath('td[1]/text()').extract_first()
            item['Scratch'] = row.xpath('td[2]/text()').extract_first()
            ...
    ```
-   Les **Pipelines** : font le lien entre la donnée brute et des objets structurés. 
    Dans notre exemple nous créons simplement une classe ppour créér l'objet athlète : 
    ```
    class athlete(scrapy.Item):
        Rank = scrapy.Field()
        Scratch = scrapy.Field()
        Name = scrapy.Field()
    ```

-   Les **Middlewares** : permettent d'effectuer des transformations sur
    les objets ou sur les requêtes exécutées par l'engine.
    Dans notre exemple
-   Le **Scheduler** : gère l'ordre et le timing des requêtes
    effectuées.


__C:\Users\paulc\Documents\Esiee_Paris\E4\dataengineering\ffck\scrapy\WebCrawler> scrapy crawl classement_ffck -o output.csv__

##### Lancement du scraping avec scrapy

__Construction de l'image Docker :__

```
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
```
- Se mettre dans le répertoire scrapy : ``` cd scrapy```
- Construction du docker à partir du dockerfile : ```docker build -t dockerfile .```

__Lancement de l'image Docker :__
-  Lancement de l'image, création du conteneur```docker run dockerfile```


### Stockage des données

#### Utilisation de MongoDB

Nous avons choisi d'utiliser MongoDB pour son optimisation sur la mémoire.
car ous avons une base de données assez conséquentes : environ 3000 athlètes.

Nous utilisons pour plus de facilité l'image docker de mongodb et créons le docker-compose suivant afin de connecter notre scraping à une base de données : 

```
version: '3'

services:
  scrapy:
    build:
      context: .
      dockerfile: ./scrapy/dockerfile
    volumes:
      - ./scrapy:/app
    depends_on:
      - mongo
    environment:
      MONGO_URI: 'mongodb://mongo:27017'
      MONGO_DATABASE: 'FFCK_BDD'

  mongo:
    image: mongo
    ports:
      - "27017:27017"

  api:
    build:
      context: .
      dockerfile: ./api/dockerfile
    volumes:
      - ./api:/app
    depends_on:
      - mongo
    environment:
      MONGO_URI: 'mongodb://mongo:27017'
      MONGO_DATABASE: 'FFCK_BDD'
```

Ainsi dans notre pipeline et nos settings, nous pouvons créer notre base de données et y ajouter les données propres du scraping.

Nous lançons maintenant notre projet avec sur le répertoire de base du projet: 

```
docker-compose up --build
```

### Création du dashboard

Nous avons choisi d'utiliser Dash pour sa facilité d'utilisation, sa flexibilité et car il s'intègre très bien avec du Python.


- Assurer vous que le conteneur Mongodb fonctionne et stocke toutes les données

- Se mettre dans le répertoire api ```cd ./api/app```



__Lancement du Dashboard :__

- Exécution du dashboard avec la commande : ```python app.py```
- Le tableau de bord sera accessible à l'adresse suivante : http://127.0.0.1:8050/



Vous pouvez ensuite arrêter Mongodb ```docker-compose down```

### Analyse

#### Trop ambitieux par rapport aux temps et conditions :

Nous avons surestimer l'ampleur du projet et nous avons accumulés des problèmes lors de la transition du dashboard 
avec docker. Les boutons ainsi que les graphique ne fonctionnait plus comme il devraient et les temps de corrections immenses...

De plus nous voullions effectuer la sélection des données avec des filtres de mongodb mais les erreurs précédentes
nous ont contraintes de les effectuer avec les dataframe de Pandas, le résultat reste cependant le même car le dataframe est
actualisé à chaque actuualisation de la page.
