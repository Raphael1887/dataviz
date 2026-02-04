import dash
from dash import html, dcc

# Initialisation de l'application Dash en mode multi-pages
# Le paramètre use_pages=True active la fonctionnalité des pages automatiques
app = dash.Dash(__name__, use_pages=True, suppress_callback_exceptions=True)

server = app.server

# Définition de la mise en page (Layout) principale
app.layout = html.Div([
    html.H1('Tableau de Bord Olympique par Rôle', style={'textAlign': 'center'}),
    
    # Barre de navigation basée sur les fichiers dans le dossier 'pages/'
    html.Div([
        html.H2('Navigation', style={'padding-left': '20px'}),
        html.Div(
            [
                dcc.Link(
                    f"{page['name']}", href=page["relative_path"],
                    style={'margin-right': '15px', 'font-size': '1.1em'}
                )
                for page in dash.page_registry.values()
            ],
            style={'display': 'flex', 'justify-content': 'center', 'margin-bottom': '20px'}
        )
    ]),

    html.Hr(),

    # Conteneur où le contenu de la page sélectionnée sera affiché
    dash.page_container
])


if __name__ == '__main__':
    # Correction de la méthode de lancement pour les versions récentes de Dash
    app.run(debug=True, host='0.0.0.0', port=8050)