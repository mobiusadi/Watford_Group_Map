import pandas as pd
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import plotly.express as px
from dash import callback_context
from dash import html

# Simplified data
data = {
    'location': ['Avignon', 'Madrid', 'Vienna', 'Singapore', 'Rhonda', 'Strasbourg', 'Paris',
                 'Westport', 'Dessau', 'Basel', 'Copenhagen', 'Washington DC', 'Berlin',
                 'London', 'Amsterdam', 'Dusseldorf', 'Scandinavia', 'Madrid', 'Zurich'],
    'year': [2001, 1999, 2008, 2022, 2010, 2009, 2019,
             2002, 2003, 2004, 2005, 2011, 2012,
             2013, 2014, 2015, 2016, 2017, 2018],
    'latitude': [43.9481, 40.4168, 48.2082, 1.3521, 36.7349, 48.5734, 48.8566,
                 53.8021, 51.8533, 47.5596, 55.6761, 38.8951, 52.5200,
                 51.5074, 52.3676, 51.2277, 60.0, 40.4168, 47.3769],  # Approximate latitudes
    'longitude': [4.8032, -3.7038, 16.3738, 103.8198, -5.1666, 7.7521, 2.3522,
                  -9.5037, 12.2427, 7.5885, 12.5683, -77.0369, 13.4050,
                  -0.1278, 4.9041, 6.7734, 20.0, -3.7038, 8.5417]   # Approximate longitudes
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
                    figure=px.scatter_map(
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
        # Hidden div to store the index of the selected location
        html.Div(id='selected-index', style={'display': 'none'})
    ]
)

@app.callback(
    Output('location-map', 'figure'),
    Output('selected-index', 'children'),
    Input({'type': 'location-card', 'index': dash.ALL}, 'n_clicks'),
    State('location-map', 'figure'),
    State({'type': 'location-card', 'index': dash.ALL}, 'id'),
    prevent_initial_call=True
)
def update_map_on_card_click(n_clicks, current_figure, card_ids):
    print("update_map_on_card_click CALLED")
    ctx = callback_context
    if ctx.triggered_id:
        clicked_index = int(ctx.triggered_id['index'])
        clicked_row = df.iloc[clicked_index]
        updated_figure = dict(current_figure)
        updated_figure['layout']['mapbox']['center'] = {
            'lat': clicked_row['latitude'],
            'lon': clicked_row['longitude']
        }
        updated_figure['data'][0]['marker']['color'] = ['blue'] * len(df)
        updated_figure['data'][0]['marker']['color'][clicked_index] = 'red'

        print(f"Clicked card index: {clicked_index}, Centering on: {clicked_row['location']}")
        return updated_figure, clicked_index
    return current_figure, dash.no_update

@app.callback(
    Output('card-list', 'children'),
    Input('selected-index', 'children'),
    State('card-list', 'children')
)
def highlight_card(selected_index, current_cards):
    if selected_index is not None:
        updated_cards_list = []
        for i, card in enumerate(current_cards):
            new_card = dict(card)
            default_style = {'marginBottom': '10px', 'border': '1px solid #ddd', 'padding': '10px'}
            new_card['props']['style'] = default_style
            if i == int(selected_index):
                new_card['props']['style'] = {'marginBottom': '10px', 'border': '2px solid red', 'padding': '10px'}
            updated_cards_list.append(new_card)
        return updated_cards_list
    return current_cards

@app.callback(
    Output('selected-index', 'children', allow_duplicate=True),
    Output('location-map', 'figure', allow_duplicate=True),
    Input('location-map', 'clickData'),
    State('location-map', 'figure'),
    prevent_initial_call=True
)
def update_cards_on_map_click(click_data, current_figure):
    print("update_cards_on_map_click CALLED")
    if click_data:
        clicked_lat = click_data['points'][0]['lat']
        clicked_lon = click_data['points'][0]['lon']
        try:
            clicked_index = df[
                (df['latitude'].round(4) == round(clicked_lat, 4)) &
                (df['longitude'].round(4) == round(clicked_lon, 4))
            ].index[0]

            updated_figure_map_click = dict(current_figure)
            updated_figure_map_click['data'][0]['marker']['color'] = ['blue'] * len(df)
            updated_figure_map_click['data'][0]['marker']['color'][clicked_index] = 'red'

            print(f"Clicked map at: {clicked_lat}, {clicked_lon}, Highlighting card index: {clicked_index}")
            return clicked_index, updated_figure_map_click
        except IndexError:
            print("No location found at clicked coordinates.")
            return dash.no_update, current_figure
    return dash.no_update, current_figure

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)