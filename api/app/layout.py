import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
        
from mycode import data_processing as dp

import folium, branca

# Ce module permet la création de layout pour représenter aux mieux la répartition des athlètes de la FFCK slalom
# Les layout seront utilisés dans un dashboard avec le module dashboard

def filter_df(df, dict_list_selection):
    """Permet de filtrer notre dataframe afin de sélectionner les observations voulues
    Args : 
        df (dataframe) : la dataframe où nous voullons appliquer les filtres
        dict_list_selection (dict(list)) : un dictionnaire qui on pour clés le nom des séries et valeurs une liste des filtres voulues pour la série
    Returns : 
        dataframe : le dataframe filtré en fonction de notre dictionnaire de filtres
    """
    filtered_df = df
    # Notre dict est None si aucune valeurs est sélectionné
    # Ainsi nous ne voullons retourner un dataframe qui vaut None
    if dict_list_selection is not None or dict_list_selection=={} :
        for key_categorie, value_list in dict_list_selection.items() :
            # Création d'un masque qui associe chaque bonnes valeurs à True 
            # On peux ainsi utiliser l'opérateur OR pour "additionner" nos masques entre chaque valeurs de chaque clé
            # On peux utiliser l'opérateur AND pour "additionner" nos masques entre chaque clés
            mask = [False] * len(filtered_df)
            if value_list is not None :
                for value in value_list :
                    mask_for_value = filtered_df[key_categorie] == value
                    mask = [a or b for a, b in zip(mask, mask_for_value)]
                # On applique notre masque pour notre catégorie :
                # Ce qui correspond au AND car on supprime si False
            filtered_df = filtered_df[mask]
        # On divise notre dataframe en fonction de notre filtrage
        final_filtered_df = filtered_df 
    else :
        final_filtered_df = None
    return final_filtered_df 


def give_division_list(df) :    
    """Permet de séparer une dataframe en liste de dataframe en fonction des Divisions
    Args : 
        df (dataframe) : la datframe que nous voullons diviser
    Return :
        list(dataframe) : Une liste contenant les dataframe en fonction des divisions
    """ 
    if df is None : 
        return None
    grouped = df.groupby('Division')
    df_all = [group for name, group in grouped]

    return df_all

def give_division_hist( list_df, 
                        stack, 
                        slider,
                        serie_name = 'Moyenne', 
                        list_color = ['#e41a1c','#377eb8','#4daf4a','#984ea3'], 
                        title = 'Histogramme des moyennes des athlètes',
                        x_axis_name = 'Moyenne des athlètes', 
                        y_axis_name = 'Nombre',                    
                       ) :
    """Permet de créer un histogramme des moyennes en fonction de la liste des dataframe des division
    Args : 
        list_df ([dataframe]) : Une liste de dataframe séparés en division
        serie_name (str) : Le nom de la série de la dataframe voulue pour notre histogramme
        list_color ([string]) : Une liste conteant les codes hexadécimaux de couleurs voulues
        title (str) : le titre de notre histogramme
        x_axis_name (str) : le nom de l'axe x de notre histogramme
        y_axis_name (str) : le nom de l'axe y de notre histogramme
        athlete_name (str) : le nom de la disciplie/ catégorie des athlètes de notre histogramme
        stack : pour changer la forme de l'histogramme
        slider : pour modifier la plage des valeurs de l'histogramme
    Return :
        fig (go.fig of plotly.graph_objects) : Notre histogramme voullu
    """
    final_filtered_df = list_df

    # On traite la couche data de notre histogramme :
    data_list = []
    # Notre df est None si il est None, alors on veux afficher un histogramme vide
    if final_filtered_df is not None : 
        for df_division, color in zip(final_filtered_df, list_color) :         
            data = go.Histogram (   x = df_division[serie_name],
                                    xbins = dict(start=0,end=1500,size=slider),
                                    name = df_division['Division'].iloc[0],
                                    customdata = df_division['Division'],
                                    hoverinfo = 'none',
                                    hovertemplate = '%{y} %{athlete_name} en %{customdata} entre %{x}',
                                    marker = dict(color = color)
                                )
            data_list.append(data)
    # Si nous n'avons aucune valeurs, nous voullons afficher un histogramme vide de même échelles
    # Cela pemet de ne pas trop changer entre le vide ou non
    else : 
        data = go.Histogram (   x = None,
                                xbins = dict(start=0,end=1500,size=25),
                            )
        data_list=[data]

    # On traite la couche layout de notre histogramme :
    # On associe les titres avec les paramètres de notre fonction
    layout = go.Layout(
        title= title,
        xaxis=dict(title = x_axis_name),
        yaxis=dict(title = y_axis_name),
        barmode = stack
    )
    # On retourne ainsi notre figure :
    fig = go.Figure(data=data_list, layout=layout)
    return fig

def give_club_map(df_ranking):
    """Permet de générer une map en fonction de la localisation des club et de la dataframe des classements
    La localisation des clubs est une dataframe que nous allons considérer statique 
    Au cours d'une année, peu de clubs arrivent ou partent.
    La fonction vas créer dans le répertoire local un fichier map_club.html qui est la nouvelle map.
    Args : 
        df_ranking (dataframe pandas) : la dataframe des classement pour générer une map
    
    """
    # Chargement des données des clubs ici car statique
    df_club = pd.read_csv('./data/resultats_clubs_complets.csv', sep=';')
    
    # Coordonnées du centre de la carte que j'ai choisi en testant
    coords_center_map = (46.8, 2.6)
    
    # Création de la carte avec un niveau de zoom initial
    map = folium.Map(location=coords_center_map, zoom_start=6)    
    # Permet de voir les cours d'eau, utile en canoë	
    folium.TileLayer('stamenwatercolor').add_to(map)

    # Filtrage des clubs ayant des coordonnées disponibles
    df_club = df_club[df_club['Coordonnées'] != 'Coordonnées non disponibles']
    
    # Comptage du nombre d'athlètes par club dans la dataframe de classement
    club_counts = df_ranking.groupby('Club')['Code_bateau'].count()

    # Filtrage des clubs ayant un comptage inférieur à 2
    df_club = df_club[df_club['Club'].isin(club_counts[club_counts >= 2].index)]
    
    # Paramètres pour la taille des marqueurs
    min_radius = 0
    max_radius = 30
    min_athletes = club_counts.min()  
    max_athletes = club_counts.max() 

    # Calcul du pourcentage d'hommes par club
    H_count = df_ranking[df_ranking['Sexe'] == 'H'].groupby('Club')['Sexe'].count()
    H_percent = (H_count / club_counts) * 100
    H_percent = H_percent.fillna(0)
    
    # Triez les pourcentages
    sorted_percentages = H_percent.sort_values()
    sorted_percentages = sorted_percentages.astype(int)
    
    # Création d'une LinearColormap pour la couleur en fonction du pourcentage
    cm = branca.colormap.LinearColormap(['red', 'blue'], vmin=0, vmax=100)

    # Ajout de la colormap à la carte
    map.add_child(cm)
    
    # Ajout des marqueurs pour chaque club sur la carte
    for index, row in df_club.iterrows():
        coord = row['Coordonnées']
        club = row['Club']
                # Filtrage des clubs ayant un comptage inférieur à 2
        if club_counts.get(club, 0) >= 2 : 
            lat, lon = [float(val) for val in coord.strip('[]').split(',')]
            
            # Calcul de la taille du marqueur en fonction du nombre d'athlètes
            athlete_count_size = min_radius + (club_counts.get(club, 0) - min_athletes) / (max_athletes - min_athletes) * (max_radius - min_radius)
            
            # Obtention de la couleur en fonction du pourcentage
            color = cm(int(sorted_percentages.get(club, 0)))
            
            # Ajout du marqueur à la carte
            folium.CircleMarker(
                location=(lon, lat),
                radius=int(athlete_count_size),
                color=color,
                fill=True,
                fill_color=color,
                popup=club + "\n Nombre d'athlètes : " + str(club_counts.get(club, 0))
            ).add_to(map)
    
    # Sauvegarde de la carte dans un fichier HTML local
    map.save(outfile='map_club.html')
    

    for index, row in df_club.iterrows():
            coord = row['Coordonnées']
            club = row['Club']
            lat, lon = [float(val) for val in coord.strip('[]').split(',')]
            athlete_count_size = min_radius + (club_counts.get(club,0) - min_athletes) / (max_athletes - min_athletes) * (max_radius - min_radius)
            color = cm(int(sorted_percentages.get(club, 0)))  # Obtenir la couleur en fonction du pourcentage
            folium.CircleMarker(
                location = (lon, lat), 
                radius = int(athlete_count_size),
                color = color,
                fill = True,
                fill_color = color,
                popup = club + "\n Nombre d'athlètes : " + str(club_counts.get(club,0))
            ).add_to(map)

    map.save(outfile='map_club.html')
    

def give_licence_graph(df):
    """Donne un graphique de la moyenne en fonction du numéro de licence
    Args : df (dataframe pandas) : la df que nous traiter pour obtenir le graphique
    """ 
    df = df[df['Code_bateau'].str[:3] != 'INV']
    df['Code_bateau'] = df['Code_bateau'].str[3:]
    df['Code_bateau'] = df['Code_bateau'].astype('float')
    df.sort_values(by='Code_bateau', ascending=True)
    # On supprime la catégorie des C2 et le sexe mixte qui ont un numéro de licence beaucoup plus grand : 
    df = df[ df['Embarcation'] != 'C2' ]
    df = df[ df['Sexe'] != 'M' ]
    trace = go.Scatter( x=df['Code_bateau'],
                        y=df['Moyenne'],
                        mode='markers' )
    
    data = [trace]

    layout = go.Layout( title='Moyenne en fonction du numéro de licence',
                        xaxis={'title': 'Numéro de licence'},
                        yaxis={'title': 'Moyenne'}
                    )
    fig = go.Figure(data=data, layout=layout)
    return fig

def give_ages_graph(df):
    """Donne un graphique de la moyenne en fonction de l'âge de l'année de naissances des athlètes
    Args : df (dataframe pandas) : la df que nous traiter pour obtenir le graphique
    """ 
    unique_years = df['Annee'].unique()
    unique_years.sort()

    Nombre_athletes_trace = go.Scatter(
        x=unique_years,
        y=df['Annee'].value_counts().loc[unique_years],
        mode='markers',
        name='Nombre d\'athlètes par année de naissance'
    )

    Moyenne_trace = go.Scatter(
        x=unique_years,
        y=df.groupby('Annee')['Moyenne'].mean().loc[unique_years],
        mode='markers',
        name='Moyenne par année de naissance'
    )

    data = [Nombre_athletes_trace, Moyenne_trace]

    layout = go.Layout(
        title="Moyenne en fonction de l'année de naissance",
        xaxis={'title': 'Année de naissance'},
        yaxis={'title': 'Moyenne'}
    )

    fig = go.Figure(data=data, layout=layout)

    return fig

def give_tab(df, selection_df) :
    """Retourne un tableau plotly en sélectionnant les colonnes de notre dataframe filtré. 
    On y mets les colonne de la selection en jaune en appliquant des masques spécifiques à la sélection
    """
    if not selection_df.empty :
        selection_mask = selection_df['Code_bateau'].isin(df['Code_bateau'])
        # selection_df = selection_df.drop(['Index','Code_bateau', 'Nombre_de_courses', 'Nombre_de_courses_nationales'], axis = 1)
        # selection_df = selection_df[[   'Classement', 'Prenom', 'Nom', 'Sexe', 'Embarcation', 
        #                             'Categorie', 'Annee', 'Division','Club', 'Moyenne' ]]
    else : 
        selection_mask = None

    # On supprime les colonnes que l'on ne veut pas montrer
    df = df.drop(['Index','Code_bateau', 'Nombre_de_courses', 'Nombre_de_courses_nationales'], axis = 1)    
    # On ajoute le classement du filtre
    df['Classement_tab'] = range(1, len(df) + 1)
    # On échange l'odre pour une meilleure visibilité
    df = df[[   'Classement','Classement_tab', 'Prenom', 'Nom', 'Sexe', 'Embarcation', 
                'Categorie', 'Annee', 'Division','Club', 'Moyenne' ]]
    
    
    # Choix des couleurs de chaque ligne 
    # Soit par rapport au sexe soit par rapport à la mise en avant avec les sélections
    dict_color = { 'H':'#a6bddb' , 'D':'#c994c7', 'Sel': '#fec44f' }
    tab_gender = [[] for _ in range(11)]
    for index, row in df.iterrows():
        gender = row['Sexe']
        if selection_mask is not None : 
            if index in selection_mask.index :
                for i in range(11):
                    color = dict_color.get('Sel', 'gray')
                    tab_gender[i].append(color)
            else:
                for i in range(11):
                    color = dict_color.get(gender, 'gray')
                    tab_gender[i].append(color)
        else :
            for i in range(11):
                    color = dict_color.get(gender, 'gray')
                    tab_gender[i].append(color)     
        

    fig = go.Figure(
            data=[
                go.Table(
                    header = dict(  values = df.columns,
                                    line_color = '#252525',
                                    fill_color = '#2b8cbe',
                                    align = 'center',
                                    font=dict(color='black', size=15)
                                ),
                    cells = dict(
                                values = [df[col] for col in df.columns],
                                line_color='#252525',
                                fill_color = tab_gender,
                                align='center',
                                font=dict(color='black', size=11),
                            ), 
                                                 
                )
        ])
    df_count = df.shape[0]

    h_count = df[df['Sexe']=='H']['Sexe'].count()
    h_percent = h_count / df_count
    f_percent = (1 - h_percent)*100

    c_count = df[df['Embarcation']=='C1']['Embarcation'].count()
    c_percent = c_count / df_count *100 

    mean = df['Moyenne'].mean()


    # Ajoutez un titre au-dessus de la table en utilisant la propriété 'annotations'
    fig.update_layout(
        annotations=[
            dict(
                text =  'Tableau du classement des athlètes filtrés',
                        
                x = 0.5, 
                y = 1.3,  
                showarrow = False, 
                font = dict(size = 20),  #
            ),
        ],
    )
    
    return fig
    
def generate_bar(df, selection_df, column_name, dict_color=None, width=300, height=300):
    '''Permet de généraliser la création de pie charts pour notre page des statistique en fonction du nom de la colonne. 
        Cela évite la redondance de code.
    '''
    column_counts = df[column_name].value_counts()
    fig = px.pie(df, values=column_counts.values, names=column_counts.index)

    if not selection_df.empty:
        selection = selection_df[column_name].unique()
        if dict_color is None:
            dict_color = {}

        for val in selection:
            dict_color[val] = 'yellow'

        # Set the colors of the sectors
        fig.update_traces(marker=dict(colors=list(dict_color.values())))

    fig.update_layout(width=width, height=height)
    fig.update_traces(textposition='inside', textinfo='percent+label', showlegend=False)
    
    return fig
