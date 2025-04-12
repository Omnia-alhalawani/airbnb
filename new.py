from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd

# Load data
df = pd.read_csv('cleaned_airbnb.csv')
df.rename(columns=lambda x: x.strip(), inplace=True)

# Unique values
neighbourhood_groups = df['neighbourhood_group'].unique()
room_types = df['room_type'].unique()

# Precomputed static charts
fig_neigh = px.pie(df, names='neighbourhood_group', title='Neighbourhood Group Distribution',
                   color_discrete_sequence=px.colors.sequential.RdBu)
fig_neigh.update_traces(textposition='inside', textinfo='percent+label')
fig_neigh.update_layout(showlegend=False)

fig_room = px.pie(df, names='room_type', title='Room Type Distribution',
                  color_discrete_sequence=px.colors.sequential.Agsunset)
fig_room.update_traces(textposition='inside', textinfo='percent+label')
fig_room.update_layout(showlegend=False)

fig_price = px.histogram(df, x="price", nbins=50, title="Price Distribution",
                         color_discrete_sequence=['#FF7F0E'])

fig_nights = px.box(df, x="room_type", y="minimum_nights", title="Minimum Nights by Room Type",
                    color="room_type", color_discrete_sequence=px.colors.qualitative.Bold)
fig_nights.update_layout(yaxis_range=[0, 30])

fig_reviews = px.bar(
    df.groupby('neighbourhood_group')['number_of_reviews'].mean().reset_index(),
    x='neighbourhood_group', y='number_of_reviews',
    title='Avg. Number of Reviews per Neighbourhood Group',
    color='neighbourhood_group', color_discrete_sequence=px.colors.qualitative.Bold
)

fig_avail = px.bar(
    df.groupby('neighbourhood_group')['availability_365'].mean().reset_index(),
    x='neighbourhood_group', y='availability_365',
    title='Average Yearly Availability by Neighbourhood Group',
    color='neighbourhood_group', color_discrete_sequence=px.colors.qualitative.Bold
)

fig_days_review = px.histogram(
    df, x='days_from_last_review', nbins=50,
    title='Days Since Last Review',
    color_discrete_sequence=['#636EFA']
)

top_neigh = df.groupby('neighbourhood')['price'].mean().sort_values(ascending=False).head(10).reset_index()
fig_top_neigh = px.bar(
    top_neigh, x='neighbourhood', y='price',
    title='Top 10 Expensive Neighbourhoods (Avg. Price)',
    color='neighbourhood', color_discrete_sequence=px.colors.qualitative.Bold
)

fig_box_dist = px.box(
    df, x='neighbourhood_group', y='distance_to_city_center',
    title='Distance to City Center by Neighbourhood Group',
    color='neighbourhood_group', color_discrete_sequence=px.colors.qualitative.Bold
)

# Start Dash app
app = Dash(__name__)
server=app.server
# Layout with dropdowns + all charts
app.layout = html.Div([
    html.H1("Airbnb Listings in NYC", style={
        'textAlign': 'center',
        'color': '#2c3e50',
        'backgroundColor': '#f7f7f7',
        'padding': '20px',
        'borderRadius': '10px'
    }),

    html.Div([
        html.Div([
            html.Label('Select Neighbourhood Group:'),
            dcc.Dropdown(
                id='neighbourhood-dropdown',
                options=[{'label': ng, 'value': ng} for ng in neighbourhood_groups],
                value=list(neighbourhood_groups),
                multi=True
            )
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            html.Label('Select Room Type:'),
            dcc.Dropdown(
                id='room-type-dropdown',
                options=[{'label': rt, 'value': rt} for rt in room_types],
                value=list(room_types),
                multi=True
            )
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),
    ], style={'padding': '20px'}),

    dcc.Graph(id='map-graph'),
    dcc.Graph(id='price-distance-graph'),

    html.Div([
        html.Div([dcc.Graph(figure=fig_neigh)], style={'width': '50%', 'display': 'inline-block'}),
        html.Div([dcc.Graph(figure=fig_room)], style={'width': '50%', 'display': 'inline-block'}),
    ]),

    html.Div([
        html.Div([dcc.Graph(figure=fig_price)], style={'width': '50%', 'display': 'inline-block'}),
        html.Div([dcc.Graph(figure=fig_nights)], style={'width': '50%', 'display': 'inline-block'}),
    ]),

    html.Div([
        html.Div([dcc.Graph(figure=fig_reviews)], style={'width': '50%', 'display': 'inline-block'}),
        html.Div([dcc.Graph(figure=fig_avail)], style={'width': '50%', 'display': 'inline-block'}),
    ]),

    html.Div([
        html.Div([dcc.Graph(figure=fig_days_review)], style={'width': '50%', 'display': 'inline-block'}),
        html.Div([dcc.Graph(figure=fig_top_neigh)], style={'width': '50%', 'display': 'inline-block'}),
    ]),

    dcc.Graph(figure=fig_box_dist)
], style={'backgroundColor': '#f0f2f5', 'padding': '30px', 'fontFamily': 'Segoe UI'})

# Callbacks for filtered charts
@app.callback(
    Output('map-graph', 'figure'),
    Output('price-distance-graph', 'figure'),
    Input('neighbourhood-dropdown', 'value'),
    Input('room-type-dropdown', 'value')
)
def update_graphs(selected_ng, selected_rt):
    filtered_df = df[df['neighbourhood_group'].isin(selected_ng) & df['room_type'].isin(selected_rt)]

    fig_map = px.scatter(
        filtered_df, x="latitude", y="longitude", color="neighbourhood_group", size="price",
        hover_name="neighbourhood", title="Filtered Airbnb Listings in NYC",
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig_map.update_layout(xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))

    fig_dist_price = px.scatter(
        filtered_df, x='distance_to_city_center', y='price', color='room_type',
        title='Filtered Price vs Distance to City Center', opacity=0.6,
        hover_data=['neighbourhood', 'neighbourhood_group'],
        color_discrete_sequence=px.colors.qualitative.Bold
    )

    return fig_map, fig_dist_price

# Run app
if __name__ == '__main__':
    app.run(port=8080)
