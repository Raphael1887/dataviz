import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config import get_engine

dash.register_page(__name__, path='/admin', name='Administrateur', order=1)

# --- 1. Récupération des données Admin ---
engine = get_engine()
df = pd.DataFrame()

try:
    if engine:
        # On récupère les 30 derniers jours triés par date
        query = "SELECT * FROM admin_metrics ORDER BY date ASC"
        df = pd.read_sql(query, engine)
except Exception as e:
    print(f"Erreur Admin SQL: {e}")

# --- 2. Calcul des KPIs (Indicateurs Clés) ---
if not df.empty:
    total_users_active = df['active_users'].sum()
    avg_latency = round(df['avg_response_time_ms'].mean(), 2)
    total_errors = df['server_errors'].sum()
    last_update = df['date'].iloc[-1].strftime('%d/%m/%Y')
else:
    total_users_active = 0
    avg_latency = 0
    total_errors = 0
    last_update = "N/A"

# Style CSS pour les cartes KPIs
card_style = {
    'backgroundColor': 'white',
    'borderRadius': '10px',
    'padding': '20px',
    'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.1)',
    'textAlign': 'center',
    'width': '30%',
    'margin': '10px'
}

# --- 3. Mise en page (Layout) ---
layout = html.Div([
    html.H2("Tableau de Bord Supervision (Admin)", style={'textAlign': 'center', 'marginBottom': '30px'}),

    # --- LIGNE 1 : Les KPIs ---
    html.Div([
        # Carte 1
        html.Div([
            html.H4("Trafic Mensuel", style={'color': '#666'}),
            html.H2(f"{total_users_active}", style={'color': '#007bff'}),
            html.P("Utilisateurs actifs cumulés")
        ], style=card_style),

        # Carte 2
        html.Div([
            html.H4("Santé Serveur", style={'color': '#666'}),
            html.H2(f"{total_errors}", style={'color': '#dc3545'}), # Rouge si erreur
            html.P("Total Erreurs (30j)")
        ], style=card_style),

        # Carte 3
        html.Div([
            html.H4("Performance Moyenne", style={'color': '#666'}),
            html.H2(f"{avg_latency} ms", style={'color': '#28a745'}), # Vert
            html.P("Temps de réponse moyen")
        ], style=card_style),
        
    ], style={'display': 'flex', 'justifyContent': 'center', 'backgroundColor': '#f8f9fa', 'padding': '20px', 'borderRadius': '10px'}),

    html.Hr(),

    # --- LIGNE 2 : Les Graphiques ---
    html.Div([
        # Graphique 1 : Évolution du trafic
        html.Div([
            html.H3("Évolution du Trafic Utilisateur"),
            dcc.Graph(id='traffic-graph', style={'height': '400px'})
        ], style={'width': '48%', 'padding': '1%'}),

        # Graphique 2 : Corrélation Traffic vs Latence (ou Erreurs)
        html.Div([
            html.H3("Logs d'Erreurs Quotidien"),
            dcc.Graph(id='errors-graph', style={'height': '400px'})
        ], style={'width': '48%', 'padding': '1%'})
    ], style={'display': 'flex', 'justifyContent': 'space-between'})
])


# --- 4. Callbacks ---
# Note : Ici les graphiques sont statiques car basés sur le CSV chargé au démarrage.
# On utilise tout de même un callback pour les générer proprement au chargement.

@callback(
    [Output('traffic-graph', 'figure'),
     Output('errors-graph', 'figure')],
    [Input('traffic-graph', 'id')] # Dummy input juste pour déclencher le chargement
)
def update_admin_graphs(_):
    if df.empty:
        empty_fig = px.bar(title="Aucune donnée disponible")
        return empty_fig, empty_fig

    # Graphique 1 : Ligne double (Active Users + New Signups)
    fig_traffic = go.Figure()
    fig_traffic.add_trace(go.Scatter(x=df['date'], y=df['active_users'], mode='lines+markers', name='Utilisateurs Actifs'))
    fig_traffic.add_trace(go.Bar(x=df['date'], y=df['new_signups'], name='Nouvelles Inscriptions', opacity=0.5))
    fig_traffic.update_layout(title="Utilisateurs Actifs vs Inscriptions", hovermode="x unified")

    # Graphique 2 : Barres rouges pour les erreurs
    fig_errors = px.bar(
        df, x='date', y='server_errors',
        title="Distribution des erreurs serveur",
        labels={'server_errors': 'Nombre d\'erreurs', 'date': 'Date'},
        color='server_errors',
        color_continuous_scale='Reds'
    )
    # On enlève la légende couleur inutile
    fig_errors.update_layout(coloraxis_showscale=False)

    return fig_traffic, fig_errors