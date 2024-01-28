from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import date
import configparser

# Accès au site de la fédération française de canoë-kayak, un site qui héberge les données de la compétition.
# Les données sont "dynamique" et l'on en a de nouvelles à chaques compétition en France (environ chaque semaine).

# Les données sont stockées sur une page web statique, nous pouvons donc effectuer un processus de scrapping.
# Ancien site http://www.ffcanoe.asso.fr/eau_vive/slalom/classement/embarcations/index

# Cependant, je trouve utile de trav    ailler sur le nouveau site qui est dynamique pour enrichir les connaissances.
# Nouveau site : https://www.ffck.org/slalom/competitions/classement_national/
# Après extraction, je remarque que les données sont stocké sur la page (dynamique) :
# Page des données : https://cna-slalom.nicolas-abbal.com/#/ranking 
# J'utilise ce site car la localisation des balises en inspectant dans le navigateur est plus simple 
# Je me rends compte que le données sont gérés dynamiquement par javascipt, d'où l'utilisation de Selenium


def extract_ranking_with_selenium(url, number = 3000, date = date.today() ):
    """Retourne un tableau contenant les données "non-propres" des classements et un second contenant les labels de ces données    
    Args : 
         url (str) : l'url de la page à extraire
         number (int) : le nombre d'observations (classement) à récolter, la fonction arrondi au multiple de 100 supérieur
         date (date) : la date de la prise de données, default = today    
    Returns : 
        tab(str) : table contenant les données "non-propres" du classement national en canoë-kayak en France
        tab(str) : table contenant le nom des labels des données du premier tableau
    Pistes de travail : 
        Travail sur l'optimisation des wait avec Selenium
        Recherche de l'optimisation de la conversion des conversions .text
        web driver non en local
    """
    # Initialisation du web driver et adaptation des différentes versions
    # On les traites à partir des Path de config.ini :
    config = configparser.ConfigParser()
    config.read('config.ini')
    chrome_binary_path = config.get('Chrome', 'binary_path')
    webdriver_path = config.get('WebDriver', 'path')

    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = chrome_binary_path
    chrome_options.add_argument(f"executable_path={webdriver_path}")

    # Erreur de certificats SSL => solution find in stack overflow : 
    # https://stackoverflow.com/questions/75160044/how-to-resolve-this-error-in-selenium-error-couldnt-read-tbscertificate-as-s
    # On supprime l'erreur au lieu de la traiter mais estun gain de temps et le site est sécurisé
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    data_list, label_list, label_list_txt, data_list_txt  = [], [], [], []

    # L'on veut récupérer les données à la date : notre argument date
    # L'on appelle donc la méthode modify_date qui permet cela
    modify_date(date,driver)

    # On veux récupérer les 3000 ou number meilleurs athlètes, ainsi faire tourner nos 30 ou int(number/100) premières pages de 100.
    for i in range( int(number/100)+1) :       
        # Remplissage de la case pour avoir une page de 100 données (le maximum) : 
        select_nbr_data = Select(driver.find_element(By.ID,'boatNumber'))
        select_nbr_data.select_by_value("100")

        # Attend le chargement de la page pour être certain de la récupération des données
        driver.implicitly_wait(10)         

        # Chargement des labels uniquement pour la première itération.
        if i == 0 :
            label_list = driver.find_elements(By.TAG_NAME, 'th')
        data_list.extend(driver.find_elements(By.TAG_NAME, 'td'))

        #conversion des driver en text ici car cela évite l'importation du module selenium autre-part
        label_list_txt = [label.text for label in label_list]
        data_list_txt.extend([data.text for data in data_list])

        # Dans la pagination il faut trouver le bouton next-page pour à chaque fois aller sur la page suivante : 
        select_num_page = driver.find_element(By.XPATH,"//button[@aria-label=\"Go to next page\" and @class=\"page-link\"]")
        select_num_page.click()

        # On réinitialiste data_list pour éviter une répétition sur la dernière itération 
        data_list = []
        # Attend le chargement de la page pour être certain de la récupération des données
        driver.implicitly_wait(10)
    driver.close()
    driver.quit()       
    return data_list_txt, label_list_txt

def modify_date(date, driver ) :
    """Permet de modifier la date sur une page de la ffck
    Args : 
        date(date) qui est la date à laquel l'on veut scraper les données
        driver(driver) le driver de la session active
    """
    # Notre page affiche les données actualisé à aujourd'hui, par défaut
    # Si nous voulons les données d'une autre date, alors il faut la changer
    if date != date.today() : 
        # On veux récupérer les données pour une date précise :
        # Les valeurs du calendrier ne vont pas en dessous de 2023 pour le classement.
        # Il est nécessaire d'attendre que notre élément soit clickable  
        wait = WebDriverWait(driver, 10)
        modify_date = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[@for='rankingDate']")))
        # Permet de clicker même si des éléments interviennent au dessus ce qui provoquais une erreur
        driver.execute_script("arguments[0].click();", modify_date)
        # Attend le chargement de nouvelle cellule
        driver.implicitly_wait(10)   
        # Cela affiche les dates du mois actuel par défaut
        # Il faut changer la date si c'est sur un autre mois :
        num_month = date.month
        num_day = date.day
        # On choisit le bon mois
        if num_month == (date.today()).month :
            select_day(num_month, num_day, driver)
        elif num_month < (date.today()).month :
            for i in range ((date.today()).month - num_month) : 
                wait = WebDriverWait(driver, 10)
                previous_month = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='__BVID__44__calendar-nav_']/button[2]")))
                previous_month.click()
            select_day(num_month, num_day, driver)
           
def select_day(num_month, num_day, driver):
    """Permet de sélectionner la bonne date sur la page avec le bon mois
    Args : 
        num_mont (int) : Le numéro du mois voulu
        num_day (int) : Le numéro du jour voulu 
        driver(driver) : le driver de la session active   
    """
    #Il faut maintenant sélectionner le bon jour : 
    id_cell = "__BVID__44__cell-2023-@month-@day_"
    id_cell_month_completed = id_cell.replace("@month", good_date(str(num_month)))
    id_cell_all_completed = id_cell_month_completed.replace("@day", good_date(str(num_day)))
    modify_day = driver.find_element(By.ID, id_cell_all_completed)
    modify_day.click()
    


def good_date(n):
    """Retourne l'entier avec un 0 devant pour qu'il y ait deux chiffres si nécessaire
    Args : 
        n (int) : auquel on veux formatter à deux chiffres
    Return :
        n (str) : Notre nombre formatter à 2 chiffres    
    """
    if int(n)<10 : 
        n = f'0{n}'
    return n

# def scrap_address_club(clubs, url) :
#     """Retourne un dictionnaire avec l'addresse de tous les clubs de la liste
#     Args : 
#         clubs [str] : nom de tous les clubs à récupérer l'addresse
#         url (str) : l'url de la page contenant les addresses
#     Return : 
#         addresse_dict {str} : Les clées sont les noms des clubs, les valeurs leurs addresses    
#     """
#     for club in clubs : 
#         # Initialisation du web driver et adaptation des différentes versions
#         chrome_options = webdriver.ChromeOptions()
#         chrome_options.binary_location = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"  
#         chrome_options.add_argument("executable_path=C:\\Users\\paulc\\Downloads\\chromedriver_win64\\chromedriver.exe")

#         # Erreur de certificats SSL => solution find in stack overflow : 
#         # https://stackoverflow.com/questions/75160044/how-to-resolve-this-error-in-selenium-error-couldnt-read-tbscertificate-as-s
#         # On supprime l'erreur au lieu de la traiter mais estun gain de temps et le site est sécurisé
#         chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

#         driver = webdriver.Chrome(options=chrome_options)
#         driver.get(url)
#         wait = WebDriverWait(driver, 10)  # Adjust the timeout as needed
#         try :
#             show_cells = driver.find_element(By.XPATH,'//a[@href="#" and contains(@class, "js-toggle-area-trigger")]')
#             show_cells.click()
        
#         search_club = wait.until(EC.presence_of_element_located((By.ID, 'search_location')))

# Permet de tester uniquement ce module.
def main() :  
    url = 'https://www.ffck.org/trouver-un-club/'
    # data = ['Canoe Kayak Du Pays De Broceliande']     
    # scrap_address_club(data)
    
if __name__ == '__main__' : 
    main()

