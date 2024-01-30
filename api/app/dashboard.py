from dash import Dash, html, Output, Input, callback_context
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import datetime
import pandas as pd

import layout

from pymongo import MongoClient
from elasticsearch import Elasticsearch

# Ce module permet la création d'un dashboard sur les classements des athlètes de la FFCK
# Les layout utilisés sont disponibles au module layout

# Connexion à la base de données MongoDB
client = MongoClient('mongodb://mongo:27017')
db = client['FFCK_BDD']  # Remplacez par le nom de votre base de données

# Exemple de récupération de données depuis une collection
collection = db['ffck_collection']  # Remplacez par le nom de votre collection


def create_dashboard_dash(collection):
    """Permet de créer un dashboard de présentation des classement du canoe-kayak en France.
    Utilise Dash et implémente le dashboard à l'addresse : http://127.0.0.1:8050/
    Le principe de cette fonction est de permettre à l'utilisateurs d'appliquer des filtres sur la base de données MongoDB
    Et de rendre les layouts dynamiques
    Args : 
        collection : Nos données de la base de donnéees MangoDB    
    """
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

        # On veux maintenant filtrer nos données
        # On vas donc créer ci-dessous des composants de dash ou de boostrap dash
        # Afin d'appliquer des filtres dynamiquement sur nos données
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
                                                )),
                        ]),
                        html.Hr(),
                        # Filtrage de la catégorie des athlètes
                        dbc.Row([
                            dbc.Col(html.Div('Catégorie : ', style={'margin-right': '7px'}), width = 'auto'  ),                       
                            dbc.Col(dbc.Checklist(  options=[   
                                                        {'label': 'U15', 'value': 'U15'},
                                                        {'label': 'U18', 'value': 'U18'},
                                                        {'label': 'U34', 'value': 'U34'},
                                                        {'label': 'M35', 'value': 'M35'}                                                 
                                                    ], 
                                                    inline=True,
                                                    id = 'categorie-checklist')),
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
                        # Filtrage de la date de la dataframe
                        # Pour plus de simplicité, nous avons décider de prendre le numéro de la semaine
                        # Cela réduit le nombre de données à récupérer
                        # Et comme les courses sont toutes les semaines, cela n'affecte pas le classement de la date
                        dbc.Col(
                            html.Div('Sélection du numéro de semaine : '),

                        ),
                        dcc.Slider(
                            id = 'date-slider',
                            min = 1,    
                            max = datetime.date.today().isocalendar()[1],
                            step = 1,
                            marks = {mark : str(mark) for mark in range(datetime.date.today().isocalendar()[1]) if mark%5==0},
                            value = 1,
                            tooltip = {"placement": "bottom", "always_visible": True},                    
                        ),
                        # Boutons de lecture (Play) et de pause (Pause)
                        dbc.Col([
                            dbc.Row([
                                dbc.Button("Play", id="play-button", color="primary", className="mr-2"),
                                dbc.Button("Pause", id="pause-button", color="danger"),
                            ], className = 'text-center'
                            )                            
                        ]),
                        html.Hr(),
                        # Filtrage des divisions des athlètes
                        dbc.Row([
                            dbc.Col(html.Div('Division : ', style={'margin-right': '7px'}), width = 'auto'  ),                       
                            dbc.Col(dbc.Checklist(  options=[   {'label': 'N1', 'value': 'N1'},
                                                        {'label': 'N2', 'value': 'N2'},
                                                        {'label': 'N3', 'value': 'N3'},
                                                        {'label': 'Reg', 'value': 'Reg'}                                                 
                                                    ], 
                                            inline=True,
                                            id = 'division-checklist')),
                        ]),

                    ]),
                ),
            ), 

             # Permet la recherche et donc la mise en avant d'athlète
             # Mettre en avant un athlète permet de changer dans la majorité des cas 
             # les couleurs concernés afin de les rendre plus visibles
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H5('Sélection (mise en avant): ', className = 'card-title'),
                        dbc.Input(
                                id = 'name_text',
                                type = 'text',
                                placeholder = 'Nom, prénom ou club'
                        ),
                        html.Div(id = 'validation_name'),                         
                    ]),
                ),
            ), 
        ]),# Row de la partie filtrage
        # Permet de gérer le temps et faire défiler notre numéro de la semaine
        dcc.Interval(
            id = 'interval-component',
            interval = 5000,  # en millisecondes
            n_intervals = 0  # initialisez à zéro
        ),
        html.Hr(),

        
        # Partie sur les layouts de notre dashboard :
        # Pourplus de visibilités, nous voulons cacher les layouts
        # Et permettre de sélectionner les layouts que nous voulons :
        # Nous allons pour cela créer un tableau clickable avec les layout en choix
        dbc.Tabs(id='tabs_layout', active_tab='tab-hist', children=[
            dbc.Tab(label='Tableau et statistiques', tab_id='tab-tab'),
            dbc.Tab(label='Histogramme de la moyenne', tab_id='tab-hist'),
            dbc.Tab(label='Carte de la répartition des clubs', tab_id='tab-map'),
            dbc.Tab(label='Graph des num de licences', tab_id='tab-graph'),
            dbc.Tab(label='Graph des âges', tab_id='tab-ages'),
        ]),
        html.Hr(),
        html.Div(id='tab_content')
        

    ], fluid=True) # fin de dbc.Containers()


    # Nous allons maintenant créer les différentes fontions qui permettent de rendre dynamique les éléments

    # Permet la sélection avec les nom, prénoms ou clubs :
    @app.callback(
        Output("validation_name", "children"),
        [   Input('gender-checklist', 'value'), 
            Input('boat-checklist', 'value'),
            Input('categorie-checklist', 'value'),
            Input('age-slider', 'value'),
            Input('division-checklist', 'value'),
            Input('date-slider', 'value'),
            Input("name_text", "value"),
        ]
    )
    def validation_name(    selected_gender, selected_boat, selected_categorie, selected_age_range,
                            selected_div, selected_date, selected_name ):
        """Permet de voir si les éléments (les lettres) rentrés dans l'input des sélection
        permettent de retrouver un ou des noms, prénoms ou clubs en fonction des filtres de la df.
        Cette fonction va donc retourner une liste des éléments sélectionnés 
        Args : 
            selected_gender, selected_boat, selected_categorie, selected_age_range, 
            selected_div, date = selected_date : permettent de récupérer les donnés du filtre
            selected_name (str) : les éléments de l'input des sélections
        Return 
            list_group (list) : qui permet l'affichage des éléments correspondant (peut être None)
        """
        filtered_df =  update_df(   selected_gender, selected_boat, selected_categorie, selected_age_range, 
                                    selected_div, date = selected_date)
        # On veut retrouver les éléments de la df filtrés en corrélation avec notre input de sélection
        if selected_name :
            mask = (
                    filtered_df['Nom'].str.contains(selected_name, case=False, na=False) | 
                    filtered_df['Prenom'].str.contains(selected_name, case=False, na=False) |
                    filtered_df['Club'].str.contains(selected_name, case=False, na=False)
                    )
            # On réduit notre df à notre sélection pour plus de simplicité
            filtered_df =  filtered_df[mask]
        if not filtered_df.empty:
            # Créez une liste d'éléments dbc.ListGroupItem pour chaque nom
            name_list = [dbc.ListGroupItem(f"{row['Prenom']} {row['Nom']} {row['Embarcation']}") for index, row in filtered_df.iterrows()]

            # On ceux afficher 5 personnes pour ne pas encombrer notre dashboard :
            if len(name_list) >= 5 :
                len_list = len(name_list)
                name_list = name_list[:4]
                name_list.append('('+str(len_list)+') athlètes') 
            # Utilisez dbc.ListGroup pour afficher la liste d'éléments
            list_group = dbc.ListGroup(name_list)

            return list_group
        else :
            return None

    # Permet de faire avancer le temps
    @app.callback(
        Output('date-slider', 'value'),
        Input('interval-component', 'n_intervals')
    )
    def update_interval(n):
        """Permet de faire avancer le temps à un intervale de 1 et donc le slider du numéro de la semaine
        Args : 
            n (int) : notre numéro de la semaine
        Return : 
            n + 1 (int) : le numéro de la semaine suivante
        """
        return n + 1

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
        elif tab == 'tab-graph' : 
            return  dbc.Col([
                        dcc.Graph(  figure = {},
                                    id = 'licence_points'
                        ),
                    ])
        elif tab == 'tab-ages' : 
            return  dbc.Col([
                        dcc.Graph(  figure = {},
                                    id = 'ages_points'
                        ),
                    ])
    
    # Permet de faire fonctionner les boutons pour le slider du temps
    @app.callback(
        Output('interval-component', 'disabled'),
        Output('play-button', 'disabled'),
        Output('pause-button', 'disabled'),
        Input('play-button', 'n_clicks'),
        Input('pause-button', 'n_clicks'),
        Input('interval-component', 'n_intervals'),
        prevent_initial_call=True
    )
    def control_play_pause(play_clicks, pause_clicks, n_intervals):
        """Permet de controller les boutons pause et stop de notre dashboard 
        Est utilisé pour la gestion du numéro de la semaine et l'avancement dans le temps
        Args : 
            play_clicks : 
            pause_clicks : 
            n_intervals : 
        Return :
            Les valeurs de play_clicks, pause_clicks, n_intervals
        """
        ctx = callback_context
        if not ctx.triggered:
            return True, False, False

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'play-button':
            return False, True, False
        elif button_id == 'pause-button':
            return True, False, True
        elif n_intervals is None:
            return True, False, False
        else:
            return False, True, False
        

    #  Mise à jour de notre map
    @app.callback(
        Output('map_points', 'srcDoc'),
        [   Input('gender-checklist', 'value'), 
            Input('boat-checklist', 'value'),
            Input('categorie-checklist', 'value'),
            Input('age-slider', 'value'),
            Input('division-checklist', 'value'),
            Input('date-slider', 'value'),
        ]
    )
    def update_map(   selected_gender, selected_boat, selected_categorie, selected_age_range,
                            selected_div, selected_date):
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
                                    selected_div, date = selected_date)
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
            Input('date-slider', 'value'),
            Input('hist_stack', 'value'),
            Input('hist-slider', 'value'),

        ]
    )
    def update_histogram(   selected_gender, selected_boat, selected_categorie, selected_age_range,
                            selected_div, selected_date, stack, slider):
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
                                    selected_div, date = selected_date,)
        final_filtered_df = layout.give_division_list(filtered_df)
        if not stack : 
            stack = None
        else: 
            stack =stack[0]
        fig = layout.give_division_hist(final_filtered_df, stack, slider)
        return fig
    
    #  Mise à jour de notre graphique des licences
    @app.callback(
        Output('licence_points', 'figure'),
        [   Input('gender-checklist', 'value'), 
            Input('boat-checklist', 'value'),
            Input('categorie-checklist', 'value'),
            Input('age-slider', 'value'),
            Input('division-checklist', 'value'),
            Input('date-slider', 'value'),

        ]
    )
    def update_licence(   selected_gender, selected_boat, selected_categorie, selected_age_range,
                            selected_div, selected_date):
        """Permet de mettre à jour notre graphique des licences en mettant à jour notre dataframe suivi de notre graph
        Toucher un à filtre (Input) vas automatiquement lancer cette fonction
        Puis cela vas appliquer les filtres sur notre df de base
        Afin d'appliquer notre fonction qui génère un graph en fonction du df sélectionné
        Args : 
            selected_gender, selected_boat, selected_categorie, selected_age_range,
            selected_div, selected_date : permettent de récupérer les données des filtres
        Return fig (fig) : Le graph des licences généré avec le dataframe filtré       
        """
        filtered_df =  update_df(   selected_gender, selected_boat, selected_categorie, selected_age_range, 
                                    selected_div, date = selected_date)
        fig = layout.give_licence_graph(filtered_df)
        return fig
    

    #  Mise à jour de notre graphique des ages
    @app.callback(
        Output('ages_points', 'figure'),
        [   Input('gender-checklist', 'value'), 
            Input('boat-checklist', 'value'),
            Input('categorie-checklist', 'value'),
            Input('age-slider', 'value'),
            Input('division-checklist', 'value'),
            Input('date-slider', 'value'),

        ]
    )
    def update_age( selected_gender, selected_boat, selected_categorie, selected_age_range,
                    selected_div, selected_date):
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
                                    selected_div, date = selected_date)
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
            Input('date-slider', 'value'),
            Input('name_text', 'value'),
        ]
    )
    def update_tab(selected_gender, selected_boat, selected_categorie, selected_age_range, 
                   selected_div, selected_date, validation_name):
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
                                selected_div, date = selected_date)
        if validation_name :
            selection_df = give_selection_df(filtered_df, validation_name)
        else : 
            selection_df = pd.DataFrame()

        # Mise à jour des figures pour les graphiques
        sexe_bar = layout.generate_bar(filtered_df, selection_df,'Sexe')
        embarcation_bar = layout.generate_bar(filtered_df, selection_df,'Embarcation')
        cate_bar = layout.generate_bar(filtered_df, selection_df, 'Categorie')
        division_bar = layout.generate_bar(filtered_df, selection_df, 'Division')

        nbr_bar = str(filtered_df.shape[0])
        annee_bar = str(round(filtered_df['Annee'].mean(),3))
        moyenne_bar = str(round(filtered_df['Moyenne'].mean(),3))
        return [layout.give_tab(filtered_df, selection_df),  nbr_bar, 
                sexe_bar, embarcation_bar, cate_bar, annee_bar, division_bar, 
                moyenne_bar]
        
    
    def give_selection_df(filtered_df, validation_name) :
        mask = (
            filtered_df['Nom'].str.contains(validation_name, case=False, na=False) | 
            filtered_df['Prenom'].str.contains(validation_name, case=False, na=False) |
            filtered_df['Club'].str.contains(validation_name, case=False, na=False)
        )
        filtered_df =  filtered_df[mask]
        return filtered_df
    
    def update_df(selected_gender, selected_boat, selected_categorie, selected_age_range, 
                  selected_div, date = 1):
        """Permet d'appliquer les filtres mis en paramètres sur la df actuelle
        Cela permet donc de gérer dynamiquement nos layout 
        Avec une gestion dynamique des filtres de notre df
        Args : 
            selected_gender, selected_boat, selected_categorie, selected_age_range,
            selected_div, selected_date : permettent de récupérer les données des filtres
            date (datetime.Date()) : permet de choisir la dataframe en fonction du numéro de semaine de la date
        Return df (df) : Une nouvelle dataframe filtrée     
        """
        result = collection.find()


        #df_good_date = df.get(date)
        #filter = {}
        #gender_tab, boat_tab = [], []
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
            filter['Annee'] = []
            # La df ne contient que les dates de nécessance, on retire donc l'age à 2023
            for year in range(2023 - age_max, 2023 - age_min +1) :
                filter['Annee'].append(year)
        return layout.filter_df(df_good_date, filter)

    # On run notre Dashboard disponible à l'addresse : http://127.0.0.1:8050/
    app.run_server(debug=True)


# Permet de tester ce module :
if __name__ == '__main__' :    
    df = dp.result_csv_to_df('result_df.csv')
    create_dashboard_dash(df)
