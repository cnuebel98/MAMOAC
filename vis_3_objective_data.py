
import plotly.express as px
import pandas as pd

def plot_fitness():
    df = pd.read_csv("results/combined_results.csv")
    
    # Add a scatter plot trace for each sublist
    fig = px.scatter_3d(df, x='steps', y='weight_shifted', z='full_cells')
    
    # Show the plot
    fig.show()

plot_fitness()