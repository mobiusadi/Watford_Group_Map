import pandas as pd
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import plotly.express as px
from dash import callback_context

# Simplified data
data = {
    'location': ['Avignon', 'Madrid', 'Vienna', 'Singapore', 'Rhonda', 'Strasbourg', 'Paris'],
    'year': [2001, 1999, 2008, 2022, 2010, 2009, 2019],
    'latitude': [43.9481, 40.4168, 48.2082, 1.3521, 36.7349, 48.5734, 48.8566],  # Dummy latitudes
    'longitude': [4.8032, -3.7038, 16.3738, 103.8198, -5.1666, -5.1666, 2.3522]  # Corrected Rhonda longitude
}
df = pd.DataFrame(data)

app = dash.Dash(__name__)

app.layout = html.Div(
    style={'display': 'flex', 'height': '100vh'},
    children=[
        html.Div(
            id='card-list',
            style={'width': '30%', 'overflowY': 'auto', 'padding': '20px'},
            children=[
                html.Div(
                    id={'type': 'location-card', 'index': i},
                    children=[html.H3(f"{row['location']} ({row['year']})")],
                    style={'marginBottom': '10px', 'border': '1px solid #ddd', 'padding': '10px'}
                )
                for i, row in df.iterrows()
            ]
        ),
        html.Div(
            style={'width': '70%'},
            children=[
                dcc.Graph(
                    id='location-map',
                    figure=px.scatter_mapbox(
                        df,
                        lat="latitude",
                        lon="longitude",
                        hover_name="location",
                        hover_data={"year": True, "latitude": False, "longitude": False},
                        zoom=3,
                        height=800
                    ).update_layout(mapbox_style="open-street-map")
                )
            ]
        ),
    ]
)

@app.callback(
    Output('location-map', 'figure'),
    Input({'type': 'location-card', 'index': dash.ALL}, 'n_clicks'),
    State('location-map', 'figure'),
    State({'type': 'location-card', 'index': dash.ALL}, 'id')
)
def update_map_on_card_click(n_clicks, current_figure, card_ids):
    print("update_map_on_card_click CALLED")
    ctx = callback_context
    if ctx.triggered_id:
        clicked_index = ctx.triggered_id['index']
        clicked_row = df.iloc[int(clicked_index)]
        current_figure['layout']['mapbox']['center'] = {
            'lat': clicked_row['latitude'],
            'lon': clicked_row['longitude']
        }
        print(f"Clicked card index: {clicked_index}, Centering on: {clicked_row['location']}")
        return current_figure
    return current_figure

@app.callback(
    Output('card-list', 'children'),
    Input('location-map', 'clickData'),
    State('card-list', 'children')
)
def update_cards_on_map_click(click_data, current_cards):
    print("update_cards_on_map_click CALLED")
    if click_data:
        clicked_lat = click_data['points'][0]['lat']
        clicked_lon = click_data['points'][0]['lon']
        # Find the index of the clicked location
        clicked_index = df[
            (df['latitude'].round(4) == round(clicked_lat, 4)) &
            (df['longitude'].round(4) == round(clicked_lon, 4))
        ].index[0]

        updated_cards = []
        for i, card in enumerate(current_cards):
            new_card = dict(card)
            default_style = {'marginBottom': '10px', 'border': '1px solid #ddd', 'padding': '10px'}
            new_card['props']['style'] = default_style
            if i == clicked_index:
                new_card['props']['style'] = {'marginBottom': '10px', 'border': '2px solid red', 'padding': '10px'}
            updated_cards.append(new_card)
        print(f"Clicked map at: {clicked_lat}, {clicked_lon}, Highlighting card index: {clicked_index}")
        return updated_cards
    return current_cards

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)