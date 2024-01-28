# Données duu canoë-kayak en France
Projet de data-engineering réalisé par Paul Cascarino et Mathis Quinio-cosquer

## Sommaire
1. [Introduction](#introduction)
2. [User Guide](#userguide)
3. [Developper Guide](#developperguide)
4. [Analyse des fonctionnalités](#AAAAA)


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
 
## Developperguide

### Scraping des données

#### Option A avec Selenium (non validé impossibilité d'utiliser Docker)
Nous voullons dans un premier temps scrapper les données du site : https://www.ffck.org/slalom/competitions/classement_national/

C'est un site dynamique, les textes sont générés avec du Javascript donc nous avons dans un premier temps utilisé __Selenium__ pour y extraire les données.

 Installer le WebDriver à l'addresse : 

https://sites.google.com/chromium.org/driver/downloads?authuser=0

#### Lancement du scraping : 

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

### Option B Scrapy sur un site statique

http://www.ffcanoe.asso.fr/eau_vive/slalom/classement/embarcations/index


Consignes
- Vous devez scraper des données sur le site web de votre choix
- Stocker ces données dans une BDD
- Afficher les données sur un site web avec la techno de votre choix (Flask, Dash, etc...)
- Les services de votre projet devront tourner sur des container Docker
- rédiger une documentation technique et fonctionnelle de votre projet (comment le lancer, choix techniques, etc...)
- Votre projet doit être disponible sur un repository github sur lequel vous nous avez invité à collaborer

Bonus
- Utilisation de docker-compose
- Scraping en temps réel
- Moteur de recherche avec Elastic Search