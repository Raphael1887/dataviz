import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config import get_engine

dash.register_page(__name__, path='/developer', name='Développeur', order=3)

# --- 1. Récupération des données Dev ---
engine = get_engine()
df = pd.DataFrame()

try:
    if engine:
        query = "SELECT * FROM dev_metrics ORDER BY date ASC"
        df = pd.read_sql(query, engine)
except Exception as e:
    print(f"Erreur Dev SQL: {e}")

# --- 2. Calcul des KPIs ---
if not df.empty:
    avg_build_time = round(df['avg_build_time_sec'].mean(), 1)
    total_commits = df['commits_count'].sum()
    total_bugs = df['bugs_reported'].sum()
    
    # Indicateur simple de santé (Ratio Bugs/Commits)
    health_ratio = round((1 - (total_bugs / total_commits)) * 100, 1) if total_commits > 0 else 0
else:
    avg_build_time = 0
    total_commits = 0
    total_bugs = 0
    health_ratio = 0

# Style CSS commun
card_style = {
    'backgroundColor': '#2b2b2b', # Mode sombre pour les devs !
    'color': 'white',
    'borderRadius': '5px',
    'padding': '15px',
    'textAlign': 'center',
    'width': '22%',
    'margin': '10px',
    'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.3)'
}

# --- 3. Mise en page (Layout) ---
layout = html.Div([
    html.H2("Tableau de Bord Technique (DevOps)", style={'textAlign': 'center', 'marginBottom': '30px'}),

    # --- LIGNE 1 : Les KPIs (Dark Theme) ---
    html.Div([
        html.Div([
            html.H4("Total Commits", style={'color': '#aaa'}),
            html.H2(f"{total_commits}", style={'color': '#4caf50'}), # Vert
            html.P("Code livré (30j)")
        ], style=card_style),

        html.Div([
            html.H4("Temps de Build", style={'color': '#aaa'}),
            html.H2(f"{avg_build_time} s", style={'color': '#ff9800'}), # Orange
            html.P("Moyenne CI/CD")
        ], style=card_style),

        html.Div([
            html.H4("Bugs Détectés", style={'color': '#aaa'}),
            html.H2(f"{total_bugs}", style={'color': '#f44336'}), # Rouge
            html.P("Tickets ouverts")
        ], style=card_style),

        html.Div([
            html.H4("Qualité du Code", style={'color': '#aaa'}),
            html.H2(f"{health_ratio}%", style={'color': '#2196f3'}), # Bleu
            html.P("Taux de succès")
        ], style=card_style),
        
    ], style={'display': 'flex', 'justifyContent': 'center', 'flexWrap': 'wrap'}),

    html.Hr(),

    # --- LIGNE 2 : Les Graphiques ---
    html.Div([
        # Graphique 1 : Vélocité vs Qualité (Commits vs Bugs)
        html.Div([
            html.H3("Vélocité & Qualité"),
            dcc.Graph(id='velocity-graph', style={'height': '400px'})
        ], style={'width': '48%', 'padding': '1%', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),

        # Graphique 2 : Monitoring Serveur (CPU/RAM)
        html.Div([
            html.H3("Monitoring Serveur"),
            dcc.Graph(id='monitoring-graph', style={'height': '400px'})
        ], style={'width': '48%', 'padding': '1%', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'flexWrap': 'wrap'})
])


# --- 4. Callbacks ---

@callback(
    [Output('velocity-graph', 'figure'),
     Output('monitoring-graph', 'figure')],
    [Input('velocity-graph', 'id')]
)
def update_dev_graphs(_):
    if df.empty:
        empty = px.bar(title="Pas de données")
        return empty, empty

    # Graphique 1 : Combo Chart (Barres pour Commits, Ligne pour Bugs)
    fig_vel = go.Figure()
    fig_vel.add_trace(go.Bar(
        x=df['date'], y=df['commits_count'], 
        name='Commits', marker_color='#4caf50'
    ))
    fig_vel.add_trace(go.Scatter(
        x=df['date'], y=df['bugs_reported'], 
        name='Bugs', mode='lines+markers', line=dict(color='#f44336', width=3), yaxis='y2'
    ))
    
    fig_vel.update_layout(
        title="Activité Git vs Bugs",
        yaxis=dict(title="Nombre de Commits"),
        yaxis2=dict(title="Nombre de Bugs", overlaying='y', side='right'),
        legend=dict(x=0, y=1.1, orientation='h'),
        hovermode="x unified"
    )

    # Graphique 2 : Area Chart pour CPU/RAM
    fig_mon = go.Figure()
    fig_mon.add_trace(go.Scatter(
        x=df['date'], y=df['cpu_usage_percent'], 
        name='CPU Usage %', fill='tozeroy', line=dict(color='#2196f3')
    ))
    fig_mon.add_trace(go.Scatter(
        x=df['date'], y=df['memory_usage_percent'], 
        name='RAM Usage %', line=dict(color='#9c27b0', dash='dot')
    ))
    
    fig_mon.update_layout(
        title="Consommation Ressources Serveur",
        yaxis=dict(title="Pourcentage %", range=[0, 100]),
        legend=dict(x=0, y=1.1, orientation='h'),
        hovermode="x unified"
    )

    return fig_vel, fig_mon