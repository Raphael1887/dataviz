import dash
from dash import dcc, html, dash_table, callback
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
# Import de la fonction de connexion à la base de données
from config import get_engine 

# Enregistrement de la page dans le registre de Dash
dash.register_page(__name__, path='/data_manager', name='Data Manager', order=2)

# --- 1. Récupération des données depuis PostgreSQL ---
# La connexion se fait au chargement de la page/app
engine = get_engine()
df = pd.DataFrame()
df_medals = pd.DataFrame()
all_nations = []

try:
    if engine:
        # Requête SQL pour récupérer toutes les données de la table
        query = "SELECT * FROM athlete_events"
        df = pd.read_sql(query, engine)
        
        # Préparation des données :
        # On remplace les valeurs NULL dans 'Medal' par 'None' si ce n'est pas déjà fait en base
        # Cela permet de filtrer facilement les médaillés
        df_medals = df[df['Medal'] != 'None'].copy()
        
        # Liste de toutes les nations pour les menus déroulants
        all_nations = sorted(df['NOC'].unique().tolist())
    else:
        print("Erreur: Impossible d'obtenir la connexion à la base de données (engine is None).")
        
except Exception as e:
    print(f"Erreur lors de la récupération des données SQL: {e}")

# Message de log si les données sont vides
if df.empty:
    print("Attention: Le DataFrame est vide. Vérifiez que la BDD est bien remplie via le script load_data.py")


# --- 2. Mise en page (Layout) ---
layout = html.Div([
    html.H2("Visualisation des Performances Olympiques (Source: PostgreSQL)", style={'textAlign': 'center'}),

    # --- FILTRE GLOBAL SAISON ---
    html.Div([
        html.Label("1. Choisissez la Saison :", style={'fontWeight': 'bold', 'marginRight': '10px'}),
        dcc.RadioItems(
            id='season-filter',
            options=[
                {'label': ' Jeux d\'Été (Summer)', 'value': 'Summer'},
                {'label': ' Jeux d\'Hiver (Winter)', 'value': 'Winter'}
            ],
            value='Summer',
            inline=True,
            style={'display': 'inline-block'}
        )
    ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': '#f9f9f9', 'marginBottom': '20px'}),

    # Conteneur Flexbox pour aligner les deux graphiques côte à côte
    html.Div([
        
        # --- BLOC GAUCHE : TOP 3 NATIONS ---
        html.Div([
            html.H3("Top 3 Nations par Sport"),
            html.Label("Sélectionnez un sport :"),
            dcc.Dropdown(id='sport-dropdown', clearable=False), # Options remplies par callback
            
            # Note : Height fixée à 450px pour éviter le bug d'extension infinie
            dcc.Graph(id='top-nations-graph', style={'height': '450px'}) 
        ], style={'width': '48%', 'padding': '1%', 'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)', 'borderRadius': '5px'}),
        
        # --- BLOC DROIT : COMPARATEUR ---
        html.Div([
            html.H3("Comparateur de Nations"),
            html.Label("Comparez l'historique des deux pays :"),
            
            html.Div([
                dcc.Dropdown(
                    id='country-1-dropdown',
                    options=[{'label': i, 'value': i} for i in all_nations],
                    value='USA', # Valeur par défaut
                    clearable=False,
                    style={'marginBottom': '5px'}
                ),
                dcc.Dropdown(
                    id='country-2-dropdown',
                    options=[{'label': i, 'value': i} for i in all_nations],
                    value='FRA', # Valeur par défaut
                    clearable=False
                )
            ]),
            
            # Note : Height fixée à 450px ici aussi
            dcc.Graph(id='comparison-graph', style={'height': '450px'}) 
        ], style={'width': '48%', 'padding': '1%', 'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)', 'borderRadius': '5px'})
    
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'flex-start', 'flexWrap': 'wrap'}),
    
    html.Hr(),
    
    # --- SECTION 3 : DONNÉES BRUTES ---
    html.H4("Aperçu des Données Brutes (100 premières lignes)"),
    dash_table.DataTable(
        id='raw-data-table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.head(100).to_dict('records'),
        sort_action="native",
        filter_action="native",
        style_table={'overflowX': 'auto', 'height': '300px', 'overflowY': 'auto'},
        style_header={'backgroundColor': 'lightgrey', 'fontWeight': 'bold'},
        style_cell={'minWidth': '100px', 'width': '150px', 'maxWidth': '300px', 'textAlign': 'left'}
    )
])


# --- 3. Callbacks (Logique Interactive) ---

# Callback A : Mettre à jour la liste des sports (Dépend de la Saison)
@callback(
    [Output('sport-dropdown', 'options'),
     Output('sport-dropdown', 'value')],
    [Input('season-filter', 'value')]
)
def set_sports_options(selected_season):
    if df.empty:
        return [], None
    
    # On ne garde que les sports existants dans la saison choisie
    season_sports = sorted(df[df['Season'] == selected_season]['Sport'].unique().tolist())
    
    # On sélectionne le premier sport par défaut pour éviter un graphique vide
    default_val = season_sports[0] if season_sports else None
    
    return [{'label': s, 'value': s} for s in season_sports], default_val


# Callback B : Graphique Top 3 Nations (Dépend de Saison + Sport)
@callback(
    Output('top-nations-graph', 'figure'),
    [Input('season-filter', 'value'),
     Input('sport-dropdown', 'value')]
)
def update_top_nations(season, sport):
    if df_medals.empty or not sport:
        return px.bar(title="Pas de données (Vérifiez la BDD)")
        
    # Filtrer par saison ET par sport
    filtered = df_medals[(df_medals['Season'] == season) & (df_medals['Sport'] == sport)]
    
    # Compter les médailles par nation
    counts = filtered['NOC'].value_counts().reset_index()
    counts.columns = ['NOC', 'Count']
    
    # Garder le Top 3
    top_3 = counts.head(3)

    fig = px.bar(
        top_3, x='NOC', y='Count', color='Count',
        title=f"Top 3 - {sport} ({season})",
        labels={'Count': 'Médailles', 'NOC': 'Pays'}
    )
    
    # SUPPRESSION DE LA BARRE DE COULEUR (LÉGENDE) À DROITE
    fig.update_layout(coloraxis_showscale=False)
    
    return fig


# Callback C : Graphique Comparaison (Dépend de Saison + Pays 1 + Pays 2)
@callback(
    Output('comparison-graph', 'figure'),
    [Input('season-filter', 'value'),
     Input('country-1-dropdown', 'value'),
     Input('country-2-dropdown', 'value')]
)
def update_comparison(season, country1, country2):
    if df_medals.empty:
        return px.line(title="Pas de données (Vérifiez la BDD)")
    
    # 1. On ne garde que la saison choisie
    season_df = df_medals[df_medals['Season'] == season]
    
    # 2. On ne garde que les lignes concernant les deux pays sélectionnés
    comparison_df = season_df[season_df['NOC'].isin([country1, country2])].copy()
    
    if comparison_df.empty:
        return px.line(title="Aucune médaille pour ces pays dans cette saison")

    # 3. On groupe par Année et par Pays pour avoir le total par édition
    yearly_counts = comparison_df.groupby(['Year', 'NOC'])['Medal'].count().reset_index()
    yearly_counts.columns = ['Year', 'NOC', 'Total Medals']
    
    # 4. Création du graphique multi-lignes
    fig = px.line(
        yearly_counts, 
        x='Year', y='Total Medals', color='NOC',
        markers=True,
        title=f"Comparaison : {country1} vs {country2} ({season})",
        labels={'Total Medals': 'Nombre de Médailles', 'Year': 'Année', 'NOC': 'Pays'}
    )
    
    # Petite amélioration pour que l'axe X affiche bien les années olympiques (tous les 4 ans souvent)
    fig.update_xaxes(dtick=4) 
    
    return fig