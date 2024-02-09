from pymongo import MongoClient
from dash import Dash, html, Output, Input, callback_context
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import datetime
import pandas as pd

import layout
from pymongo import MongoClient

import time

# Permet de créer un dashboard de présentation des classement du canoe-kayak en France.
# Utilise Dash et implémente le dashboard à l'addresse : http://127.0.0.1:8050/
# Le principe de cette fonction est de permettre à l'utilisateurs d'appliquer des filtres sur la base de données MongoDB
# Et de rendre les layouts dynamiques
# Args : 
#     collection : Nos données de la base de donnéees MangoDB    




# On crée la mise en page de notre Dashboard
# Utilisation du thème Cerulean pour la simplicité et la gamme de couleur autour du bleu (couleur de l'eau)
external_stylesheets = [dbc.themes.CERULEAN]

# On supprime les callbacks excpetions car cela nous permets de pouvoir cacher certains éléments
app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)  


# Définition de la couche layout de notre dashboard
# On veux un simplicité tout en ayant quelque chose de beau donc :
# Utilisation du Dash Bootstrap Components de https://dash.plotly.com/tutorial
app.layout = dbc.Container([
    # Titre, sous-titre et crédit de notre dashboard
    dbc.Row([
        dbc.Col(html.H1('Répartition des athlètes de la FFCK Slalom', className="text-primary text-center fs-1")),
    ]),
    dbc.Row([
        html.H2([   'Données récupérées sur : ',
                    html.A( 'Site officiel FFCK', 
                            href='https://www.ffck.org/slalom/competitions/classement_national/', 
                            target='_blank')
        ], className="text-primary text-center fs-3"),
    ]),               
    dbc.Row([
        dbc.Col(html.H3('Par Paul Cascarino et Mathis Quinio-cosquer, projet data-engineer, Esiee Paris', className="text-primary text-center fs-5")),
    ]),

    html.Hr(),

    # On veux maintenant filtrer notre dataframe
    # On vas donc créer ci-dessous des composants de dash ou de boostrap dash
    # Afin d'appliquer des filtres dynamiquement sur notre dataframe
    dbc.Row([
        # Filtrage :
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H5('Filtrage :', className='card-title'),
                    # Filtrage du Sexe des athlètes
                    dbc.Row([
                        dbc.Col(html.Div('Sexe : ', style={'margin-right': '7px'}), width = 'auto'  ),                            
                        dbc.Col(dbc.Checklist(  options = [ {'label': 'Homme', 'value': 'H'}, 
                                                            {'label': 'Femme', 'value': 'D'}], 
                                                inline=True,
                                                id = 'gender-checklist',
                                                value=['H', 'D'] 
                                            )),
                    ]),

                    html.Hr(),
                    # Filtrage de l'embarcation des athlètes
                    dbc.Row([
                        dbc.Col(html.Div('Embarcation : ', style={'margin-right': '7px'}), width = 'auto'  ),                       
                        dbc.Col(dbc.Checklist(  options = [ {'label': 'C1', 'value': 'C1'}, 
                                                            {'label': 'K1', 'value': 'K1'},
                                                            {'label': 'C2', 'value': 'C2'}], 
                                                inline = True,
                                                id = 'boat-checklist',
                                                value=['C1', 'K1', 'C2']
                                            )),
                    ]),
                    html.Hr(),
                    # Filtrage de la catégorie des athlètes
                    dbc.Row([
                        dbc.Col(html.Div('Catégorie : ', style={'margin-right': '7px'}), width = 'auto'  ),                       
                        dbc.Col(dbc.Checklist(  options=[   
                                                    {'label': 'Minime', 'value': 'M'},
                                                    {'label': 'Cadet', 'value': 'C'},
                                                    {'label': 'Junior', 'value': 'J'},
                                                    {'label': 'Senior', 'value': 'S'},
                                                    {'label': 'Veteran 1', 'value': 'V1'},
                                                    {'label': 'Veteran 2', 'value': 'V2'},
                                                    {'label': 'Veteran 3', 'value': 'V3'},
                                                    {'label': 'Veteran 4', 'value': 'V4'},
                                                    {'label': 'Veteran 5', 'value': 'V5'},                                                
                                                ], 
                                                inline=True,
                                                id = 'categorie-checklist',
                                                value=['M', 'C', 'J', 'S', 'V1', 'V2', 'V3', 'V4', 'V5'] )),
                    ]),
                    html.Hr(),
                    # Filtrage de l'âge des athlètes
                    dbc.Row([
                        dbc.Col(html.Div('Ages (min-max) : ', style={'margin-right': '7px'}), width = 'auto'  ),                       
                        dbc.Col(dcc.RangeSlider(
                                id = 'age-slider',
                                min = 14,
                                max = 75,
                                step = 1,
                                # Pour vaoir des marques sur les catégories (+)
                                marks = {14: '14', 18: '18', 34: '34', 50: '50', 75: '75'},
                                value = [14, 75], 
                                tooltip = {"placement": "bottom", "always_visible": True},
                                # Pour ne pas inverser max et min
                                allowCross = False 
                        ))
                    ]),                                        
                ]),
            ),
        ), 

        # Filtrage partie 2
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H5('Filtrage :', className='card-title'),
                    
                    # Filtrage des divisions des athlètes
                    dbc.Row([
                        dbc.Col(html.Div('Division : ', style={'margin-right': '7px'}), width = 'auto'  ),                       
                        dbc.Col(dbc.Checklist(  options=[   {'label': 'N1', 'value': 'N1'},
                                                    {'label': 'N2', 'value': 'N2'},
                                                    {'label': 'N3', 'value': 'N3'},
                                                    {'label': 'Reg', 'value': 'Reg'}                                                 
                                                ], 
                                        inline=True,
                                        id = 'division-checklist',
                                        value=['N1', 'N2', 'N3', 'Reg'])),
                    ]),

                ]),
            ),
        ), 

    ]),# Row de la partie filtrage
    


    # Partie sur les layouts de notre dashboard :
    # Pourplus de visibilités, nous voulons cacher les layouts
    # Et permettre de sélectionner les layouts que nous voulons :
    # Nous allons pour cela créer un tableau clickable avec les layout en choix
    dbc.Tabs(id='tabs_layout', active_tab='tab-hist', children=[
        dbc.Tab(label='Tableau et statistiques', tab_id='tab-tab'),
        dbc.Tab(label='Histogramme de la moyenne', tab_id='tab-hist'),
        dbc.Tab(label='Carte de la répartition des clubs', tab_id='tab-map'),
        #dbc.Tab(label='Graph des num de licences', tab_id='tab-graph'),
        dbc.Tab(label='Graph des âges', tab_id='tab-ages'),
    ]),
    html.Hr(),
    html.Div(id='tab_content')


    ], fluid=True) # fin de dbc.Containers()

# result = collection.find()
# df = pd.DataFrame(list(result))
#  Montre la page de layout sélectionnée
@app.callback(
    Output('tab_content', 'children'),
    Input('tabs_layout', 'active_tab')
    
)
def show_layout(tab):
    """Permet de montrer les layout disponibles en fonction de la sélection du tableau
    Args : 
        tab (str) : l'élement donc la page sélectionné sur le tableau
    Return dbc.Col() : une mini-page dbc qui montre le layout sélectionné
    """
    if tab == 'tab-tab': 
    # Affiche un tableau de la dataframe filtré dynamiquement 
        return dbc.Col([
                    dbc.Card(
                        dbc.CardBody([
                            dbc.Row([

                                dbc.Col([
                                    dbc.Row([
                                        dbc.Card(dbc.CardBody([
                                                html.Div("Nombre d'athlètes : "),
                                                html.Div(id = 'nbr_bar')
                                            ]))
                                    
                                    ]),
                                    dbc.Row([
                                        dbc.Card(dbc.CardBody([
                                            html.Div('Proportion des sexes : '),
                                            dcc.Graph(  figure = {},
                                                        id = 'sexe_bar'
                                            ),
                                        ]))
                                    ]),
                                    dbc.Row([
                                        dbc.Card(dbc.CardBody([
                                            html.Div('Proportion des embarcations: '),
                                            dcc.Graph(  figure = {},
                                                        id = 'embarcation_bar'
                                            ),
                                        ]))
                                    ]),
                                    dbc.Row([
                                        dbc.Card(dbc.CardBody([
                                            html.Div('Moyenne des moyennes : '),
                                            html.Div(id = 'moyenne_bar')
                                        ]))
                                    ]),
                                ]),
                                dbc.Col([
                                    dbc.Row([
                                        dbc.Card(dbc.CardBody([
                                            html.Div('Moyenne des années de naissances : '),
                                            html.Div(id = 'annee_bar')
                                        ]))
                                    ]),                                        
                                    dbc.Row([
                                        dbc.Card(dbc.CardBody([
                                            html.Div('Proportion des catégories : '),
                                            dcc.Graph(  figure = {},
                                                        id = 'cate_bar'
                                            ),
                                        ]))
                                    ]),
                                    dbc.Row([
                                        dbc.Card(dbc.CardBody([
                                            html.Div('Proportion des divisions : '),
                                            dcc.Graph(  figure = {},
                                                        id = 'division_bar'
                                            ),
                                        ]))
                                    ]),
                                ]),   
                            ])                         

                        ])
                    ),
                    dbc.Col(

                        dcc.Graph(  figure = {},
                                    id = 'tab_points'
                        )),
                ]),

    elif tab == 'tab-hist' :         
    # Affiche un histogramme de la dataframe filtré dynamiquement
        return dbc.Row(
                    dbc.Col([
                        dbc.Card(
                            dbc.CardBody([
                                html.H5("Options pour l'histogramme : ", className='card-title'),
                                html.Div('Sélection de la forme : '),
                                dbc.Checklist(  options = [ {'label': 'Stack', 'value': 'stack'}],
                                                id = 'hist_stack'),
                                html.Div('Sélection de la plage de valeurs : '),  
                                dcc.Slider(
                                    id = 'hist-slider',
                                    min = 1,    
                                    max = 500,
                                    step = 1,
                                    value = 25,
                                    tooltip = {"placement": "bottom", "always_visible": True},
                                marks = {mark: str(mark) for mark in range(1, 500, 50)}           
                                ),
                            ])
                        ),
                        dcc.Graph(  figure = {},
                                    id = 'histogram_points')
                    ])
                ),

    elif tab == 'tab-map' :
        # Affiche une map de la dataframe filtré dynamiquement
        return dbc.Row(
                    dbc.Col(
                        html.Iframe(
                            srcDoc=open('map_club.html', 'r').read(),
                            width='100%',
                            height='500',
                            id='map_points'
                        )
                    )
                )
    elif tab == 'tab-ages' : 
        return  dbc.Col([
                    dcc.Graph(  figure = {},
                                id = 'ages_points'
                    ),
                ])

#  Mise à jour de notre map
@app.callback(
    Output('map_points', 'srcDoc'),
    [   Input('gender-checklist', 'value'), 
        Input('boat-checklist', 'value'),
        Input('categorie-checklist', 'value'),
        Input('age-slider', 'value'),
        Input('division-checklist', 'value'),
        #Input('date-slider', 'value'),
    ]
)
def update_map(   selected_gender, selected_boat, selected_categorie, selected_age_range,
                        selected_div):
    """Permet de mettre à jour notre map en mettant à jour notre dataframe suivi de notre map
    Toucher un à filtre (Input) vas automatiquement lancer cette fonction
    Puis cela vas appliquer les filtres sur notre df de base
    Afin d'appliquer notre fonction qui génère une map en fonction du df sélectionné
    Args : 
        selected_gender, selected_boat, selected_categorie, selected_age_range,
        selected_div, selected_date : permettent de récupérer les données des filtres
    Return (map) : La lecture de la nouvelle map généré par la nouvelle dataframe        
    """
    filtered_df =  update_df(   selected_gender, selected_boat, selected_categorie, selected_age_range, 
                                selected_div)
    layout.give_club_map(filtered_df)
    return open('map_club.html', 'r').read()

    

#  Mise à jour de notre histogramme
@app.callback(
    Output('histogram_points', 'figure'),
    [   Input('gender-checklist', 'value'), 
        Input('boat-checklist', 'value'),
        Input('categorie-checklist', 'value'),
        Input('age-slider', 'value'),
        Input('division-checklist', 'value'),
        Input('hist_stack', 'value'),
        Input('hist-slider', 'value'),

    ]
)
def update_histogram(   selected_gender, selected_boat, selected_categorie, selected_age_range,
                        selected_div, stack, slider):
    """Permet de mettre à jour notre histogramme en mettant à jour notre dataframe suivi de notre histogramme
    Toucher un à filtre (Input) vas automatiquement lancer cette fonction
    Puis cela vas appliquer les filtres sur notre df de base
    Afin d'appliquer notre fonction qui génère un histogramme en fonction du df sélectionné
    Args : 
        selected_gender, selected_boat, selected_categorie, selected_age_range,
        selected_div, selected_date : permettent de récupérer les données des filtres
        stack : pour changer la forme de l'histogramme
        slider : pour modifier la plage des valeurs de l'histogramme
    Return fig (fig) : L'histogramme généré avec le dataframe filtré       
    """
    filtered_df =  update_df(   selected_gender, selected_boat, selected_categorie, selected_age_range, 
                                selected_div)
    final_filtered_df = layout.give_division_list(filtered_df)
    if not stack : 
        stack = None
    else: 
        stack =stack[0]
    fig = layout.give_division_hist(final_filtered_df, stack, slider)
    return fig


#  Mise à jour de notre graphique des ages
@app.callback(
    Output('ages_points', 'figure'),
    [   Input('gender-checklist', 'value'), 
        Input('boat-checklist', 'value'),
        Input('categorie-checklist', 'value'),
        Input('age-slider', 'value'),
        Input('division-checklist', 'value'),
    ]
)
def update_age( selected_gender, selected_boat, selected_categorie, selected_age_range,
                selected_div):
    """Permet de mettre à jour notre graphique des âges en mettant à jour notre dataframe suivi de notre graph
    Toucher un à filtre (Input) vas automatiquement lancer cette fonction
    Puis cela vas appliquer les filtres sur notre df de base
    Afin d'appliquer notre fonction qui génère un graph en fonction du df sélectionné
    Args : 
        selected_gender, selected_boat, selected_categorie, selected_age_range,
        selected_div, selected_date : permettent de récupérer les données des filtres
    Return fig (fig) : Le graph des âges généré avec le dataframe filtré       
    """
    filtered_df =  update_df(   selected_gender, selected_boat, selected_categorie, selected_age_range, 
                                selected_div)
    fig = layout.give_ages_graph(filtered_df)
    return fig

# Mise à jour de notre tableau
@app.callback(
    [
        Output('tab_points', 'figure'),
        Output('nbr_bar', 'children'),
        Output('sexe_bar', 'figure'),
        Output('embarcation_bar', 'figure'),
        Output('cate_bar', 'figure'),
        Output('annee_bar', 'children'),
        Output('division_bar', 'figure'),
        Output('moyenne_bar', 'children')
    ],
    [   
        Input('gender-checklist', 'value'), 
        Input('boat-checklist', 'value'),
        Input('categorie-checklist', 'value'),
        Input('age-slider', 'value'),
        Input('division-checklist', 'value'),
    ]
)
def update_tab(selected_gender, selected_boat, selected_categorie, selected_age_range, 
                selected_div,):
    """Permet de mettre à jour notre tableau en mettant à jour notre dataframe suivi de notre tableau
    Toucher un à filtre (Input) vas automatiquement lancer cette fonction
    Puis cela vas appliquer les filtres sur notre df de base
    Afin d'appliquer notre fonction qui génère un tableau en fonction du df sélectionné
    Args : 
        selected_gender, selected_boat, selected_categorie, selected_age_range,
        selected_div, selected_date : permettent de récupérer les données des filtres
    Return data (dict) : Les valeurs du tableaux généré avec le dataframe filtré       
    """
    filtered_df = update_df(selected_gender, selected_boat, selected_categorie, selected_age_range, 
                            selected_div)
    sel_df = None

    # Mise à jour des figures pour les graphiques
    sexe_bar = layout.generate_bar(filtered_df,sel_df,'Sexe')
    embarcation_bar = layout.generate_bar(filtered_df,sel_df,'Embarcation')
    cate_bar = layout.generate_bar(filtered_df,sel_df, 'Categorie')
    division_bar = layout.generate_bar(filtered_df,sel_df, 'Division')

    nbr_bar = str(filtered_df.shape[0])
    annee_bar = str(round(filtered_df['Annee'].mean(),3))
    moyenne_bar = str(round(filtered_df['Moyenne'].mean(),3))

    # Extraction des informations de la figure pour rendre la sortie sérialisable en JSON
    sexe_bar_json = sexe_bar.to_json()
    embarcation_bar_json = embarcation_bar.to_json()
    cate_bar_json = cate_bar.to_json()
    division_bar_json = division_bar.to_json()

    return [layout.give_tab(filtered_df, sel_df),  nbr_bar, 
            sexe_bar_json, embarcation_bar_json, cate_bar_json, annee_bar, division_bar_json, 
            moyenne_bar]  


def update_df(selected_gender, selected_boat, selected_categorie, selected_age_range, 
                selected_div):
    """Permet d'appliquer les filtres mis en paramètres sur la df actuelle
    Cela permet donc de gérer dynamiquement nos layout 
    Avec une gestion dynamique des filtres de notre df
    Args : 
        selected_gender, selected_boat, selected_categorie, selected_age_range,
        selected_div, selected_date : permettent de récupérer les données des filtres
        date (datetime.Date()) : permet de choisir la dataframe en fonction du numéro de semaine de la date
    Return df (df) : Une nouvelle dataframe filtrée     
    """

    # Récupère dynamiquement le dataframe dans la bdd mongo
    result = collection.find()
    df = pd.DataFrame(list(result))
    filter = {}

    if selected_gender :
        filter['Sexe'] = selected_gender
    if selected_boat :  
        filter['Embarcation'] = selected_boat
    if selected_categorie :
        filter['Categorie'] = selected_categorie
    if selected_div :
        filter['Division'] = selected_div
    if selected_age_range is not None and len(selected_age_range) == 2:
        age_min, age_max = selected_age_range
        filter['Annee'] = {"$gte": 2023 - age_max, "$lte": 2023 - age_min} 

    #return layout.filter_df(df,filter)
    return df


def run_dash_server():
    # Lancer le serveur Dash
    server = app.run_server(host='0.0.0.0', port=8050, debug=True, use_reloader=False)


if __name__ == '__main__':

    mongo_ready = False
    while not mongo_ready:
        try:
            # Try to connect to MongoDB
            client = MongoClient('mongo:27017', serverSelectionTimeoutMS=30000, socketTimeoutMS=30000, connectTimeoutMS=30000)
            db = client['FFCK_BDD']
            collection = db['ffck_collection']
            mongo_ready = True
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            print("Retrying in 5 seconds...")
            time.sleep(5)
 
    # df = None
    # while df is None:
    #     result = collection.find()
    #     df = pd.DataFrame(list(result))
    #     filter = {}
    #     filter['Sexe'] = 'H'
    #     print("attendre")
    #     time.sleep(5)
    # print('df : ')
    # print(df.columns)
    # print('layout: ')
    # df_bis = layout.filter_df(df,filter)
    # print(df_bis['Sexe'])

    run_dash_server()
        
    # Personnalisez le message d'accueil


