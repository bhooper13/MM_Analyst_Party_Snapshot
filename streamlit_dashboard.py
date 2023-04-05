import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import mpld3
import streamlit.components.v1 as components
def draw_graph(graph):
    fig, ax = plt.subplots()

    # draw the graph
    nx.draw(graph, ax=ax)
    # show the plot
    #st.pyplot(fig)
    fig_html = mpld3.fig_to_html(fig)
    components.html(fig_html, height=800)

def make_streamlit():
    # create a sample graph
    G = nx.Graph()
    G.add_edges_from([(1,2),(2,3),(3,4),(4,1),(2,4)])

    st.title("NetworkX Graph with Zoom")

    # draw the graph using the draw_graph function
    draw_graph(G)
# create a function to draw the graph



# create a streamlit app

