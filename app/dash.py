from flask import Flask, render_template
from dash import Dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from flask import Blueprint
import os,json
folder = os.getcwd()
bp = Blueprint('dash', __name__)
from scipy.sparse import load_npz
import numpy as np
import re 
data_folder = f"{folder}/app/static/data"
from plotly.colors import qualitative
colors = qualitative.Pastel1 

@bp.route('/clustering')
def clusters():
    return render_template('dash.html')

def create_dash(flask_app):
    dash_app = Dash(__name__, server=flask_app, url_base_pathname='/dash/')

    citation_matrix_3d = np.load(f'{data_folder}/citation_matrix_3d.npy')
    centroids_3d = np.load(f'{data_folder}/centroids_3d.npy')
    citation_matrix = load_npz(f'{data_folder}/author_citations.npz')
    labels =  np.load(f'{data_folder}/labels.npy')
    with open(f"{data_folder}/author_citations.json","r") as file: 
        author_list, centroid_labels = json.load(file)

    dash_app.layout = html.Div([
        dcc.Input(id='author-search', type='text', placeholder="Search Author"),
        html.Label('\nNumber of Nearest Neighbors (Slider)', style={'font-weight': 'bold', 'font-size': '16px'}),  # Label for the slider
        dcc.Slider(
            id='neighbor-slider',
            min=1,
            max=10,
            step=1,
            value=3,
            marks={i: f'{i}' for i in range(1, 11)},
            tooltip={"placement": "bottom", "always_visible": True},
        ),
        dcc.Graph(id='3d-scatter-plot'),
    ])

    @dash_app.callback(
        Output('3d-scatter-plot', 'figure'),
        [Input('author-search', 'value'),
        Input('neighbor-slider', 'value')]
    )
    def update_3d_scatter(selected_author, num_neighbors):
        scatter_data = []
        if not selected_author:
            author_indices = range(len(author_list))
        else:
            author_indices = [i for i, author in enumerate(author_list) if re.search(selected_author, author, re.IGNORECASE)]
    
        # If an author is selected, highlight them and find nearest neighbors
        if selected_author:
            try:
                similarities = cosine_similarity(citation_matrix.toarray())
                for idx, author_idx in enumerate(author_indices): 
                    color = colors[idx % len(colors)]
                    similarity_scores = similarities[author_idx]
                    
                    # Get indices of nearest neighbors
                    neighbor_indices = np.argsort(-similarity_scores)[1:num_neighbors+1]
                    
                    # Highlight selected author
                    scatter_data.append(go.Scatter3d(
                        x=[citation_matrix_3d[author_idx, 0]],
                        y=[citation_matrix_3d[author_idx, 1]],
                        z=[citation_matrix_3d[author_idx, 2]],
                        mode='markers+text',
                        marker=dict(size=10, color=color),
                        text=[author_list[author_idx]],
                        hovertemplate="%{text}<extra></extra>", 
                        name=author_list[author_idx]
                    ))

                    # Highlight nearest neighbors
                    scatter_data.append(go.Scatter3d(
                        x=citation_matrix_3d[neighbor_indices, 0],
                        y=citation_matrix_3d[neighbor_indices, 1],
                        z=citation_matrix_3d[neighbor_indices, 2],
                        mode='markers',
                        marker=dict(size=7, color=color),
                        text=[author_list[i] for i in neighbor_indices],
                        hovertemplate="%{text}<extra></extra>", 
                        name='Nearest Neighbors'
                    ))

            except ValueError:
                pass  # Author not found, do nothing
        else: 
            scatter_data.append(go.Scatter3d(
            x=citation_matrix_3d[:, 0],
            y=citation_matrix_3d[:, 1],
            z=citation_matrix_3d[:, 2],
            mode='markers',
            marker=dict(
                size=5,
                color=labels,  # Use cluster labels for color
                colorscale='magenta',
                opacity=0.8
            ),
            text=[author_list[i] for i in author_indices],
            hovertemplate="%{text}<extra></extra>", 
            name='Authors'
            ))

        # Plot the centroids and label them
        scatter_data.append(go.Scatter3d(
            x=centroids_3d[:, 0],
            y=centroids_3d[:, 1],
            z=centroids_3d[:, 2],
            mode='markers',
            marker=dict(
                size=7,
                color='black',
                symbol='x',
            ),
            text=[f"Centroid {i}: " + ', '.join([f"{feature} ({float(value):.2f})" for feature, value in centroid_labels[i]]) 
              for i in range(len(centroids_3d))],
            textposition="top center",
            hovertemplate="%{text}<extra></extra>", 
            name='Centroids'
        ))

        # Define the layout
        layout = go.Layout(
            scene=dict(
                xaxis_title='PC1',
                yaxis_title='PC2',
                zaxis_title='PC3'
            ),
            margin=dict(l=0, r=0, b=0, t=0)
        )

        return go.Figure(data=scatter_data, layout=layout)

    return dash_app
