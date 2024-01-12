import requests
import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
import plotly.io as pio
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Requête pour les informations sur les stations
station_info_url = "https://velib-metropole-opendata.smovengo.cloud/opendata/Velib_Metropole/station_information.json"

# Requête pour l'état actuel des stations
station_status_url = "https://velib-metropole-opendata.smovengo.cloud/opendata/Velib_Metropole/station_status.json"

# Déclaration de la variable bikes_available_column en tant que variable globale
bikes_available_column = 'num_bikes_available'

# Fonction pour mettre à jour les données
def update_data():
    response_info = requests.get(station_info_url)
    response_status = requests.get(station_status_url)

    if response_info.status_code == 200 and response_status.status_code == 200:
        data_info = response_info.json()
        data_status = response_status.json()

        if 'data' in data_info and 'data' in data_status:
            stations_info = data_info['data']['stations']
            stations_status = data_status['data']['stations']

            df_info = pd.DataFrame(stations_info)
            df_status = pd.DataFrame(stations_status)

            df_merged = pd.merge(df_info, df_status, on='station_id', how='inner')

            if bikes_available_column in df_merged.columns:
                df_merged['available_bikes_ratio'] = df_merged[bikes_available_column] / df_merged['capacity']
                df_merged['size1'] = 1
                df_merged = df_merged.dropna(subset=['available_bikes_ratio'])
                return df_merged
            else:
                print(f"La colonne '{bikes_available_column}' n'est pas présente dans le DataFrame.")
                return pd.DataFrame()
        else:
            print("Les clés 'data' sont manquantes dans la réponse JSON.")
            return pd.DataFrame()
    else:
        print(f"Échec de la requête. Code d'état (informations sur les stations) : {response_info.status_code}")
        print(f"Échec de la requête. Code d'état (état actuel des stations) : {response_status.status_code}")
        return pd.DataFrame()

# Fonction pour ajouter l'heure à l'image
def add_timestamp_to_image(image_path, target_size=(1000, 700)):
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)

    # Utilisez une police spécifique pour garantir la couleur noire
    font = ImageFont.load_default()

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    draw.text((10, 10), current_time, (0, 0, 0), font=font)  # Position et couleur du texte (0, 0, 0) correspond au noir
    img.save(image_path)

    # Redimensionner l'image
    resized_img = img.resize(target_size, Image.ANTIALIAS)
    resized_img.save(image_path)

# Initialiser l'application Dash
app = dash.Dash(__name__)

# Create images folder if not exists
if not os.path.exists('images'):
    os.makedirs('images')

# Callback pour la mise à jour des données
@app.callback(Output('live-update-text', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_layout(n):
    df_merged = update_data()

    if not df_merged.empty:
        # Recréer la carte avec les nouvelles données
        fig = px.scatter_mapbox(df_merged,
                                lat="lat",
                                lon="lon",
                                hover_name="name",
                                hover_data=["station_id", bikes_available_column, "capacity"],
                                size_max=8,
                                size='size1',
                                color="available_bikes_ratio",
                                color_continuous_scale="RdYlGn",
                                range_color=[0, 1],
                                zoom=10)
        fig.update_layout(mapbox_style="open-street-map")
        
        # Configure the map for the desired changes
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

        # Sauvegarder le screenshot avec un nom unique basé sur le numéro de screen, la date et l'heure
        screenshot_path = f"images/screenshot-{n}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"  # Modification du nom du fichier
        pio.write_image(fig, screenshot_path)

        # Ajouter l'heure à l'image
        add_timestamp_to_image(screenshot_path, target_size=(1000, 700))

        # Mettre à jour le contenu de la table avec les nouvelles données
        table_data = [
            html.Tr([
                html.Td(row['name']),
                html.Td(f"{row['available_bikes_ratio']*100:.2f}%"),
                html.Td(row['capacity'])
            ])
            for _, row in df_merged.iterrows()
        ]

        return [
            dcc.Graph(figure=fig, style={'height': 'calc(100vh - 10px)'}),
            html.H3("Liste des stations :"),
            html.Table([
                html.Tr([
                    html.Th("Nom de la station"),
                    html.Th("Disponibilité (%)"),
                    html.Th("Nombre total de places")
                ]),
                *table_data
            ])
        ]
    else:
        return "Échec de la mise à jour des données."

# Mise à jour des données toutes les 10 secondes
app.layout = html.Div([
    dcc.Interval(
        id='interval-component',
        interval=60*1000*10,  # en millisecondes
        n_intervals=0
    ),
    html.Div(id='live-update-text')
])

# Exécuter l'application Dash
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True)