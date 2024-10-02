
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def plot_fitness():
    df = pd.read_csv("results/combined_results.csv")
    
    # Add a scatter plot trace for each sublist
    fig = px.scatter_3d(df, x='steps', y='weight_shifted', z='full_cells')
    # Add a red dot at (0, 0, 0)
    fig.add_trace(go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode='markers',
        marker=dict(size=5, color='red'),
        name='Red dot'
    ))
    # Show the plot
    fig.show()

plot_fitness()