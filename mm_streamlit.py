import streamlit as st
# import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from streamlit_plotly_events import plotly_events

import network_utilities as nx_util
import streamlit_utilities as st_util

import streamlit_toggle as tog
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_PARAGRAPH_ALIGNMENT as PP_ALIGN
import matplotlib.pyplot as plt
import numpy as np

# viridis_cmap = plt.cm.get_cmap("viridis")
val_map={'account': 0.03, 'activity': 0.06846153846153846, 'additional_information': 0.10692307692307693, 'address': 0.1453846153846154, 'aircraft': 0.18384615384615385, 'cargo': 0.22230769230769232, 'container': 0.26076923076923075, 'cryptocurrency_address': 0.2992307692307693, 'cryptocurrency_cluster': 0.33769230769230774, 'electronic_address': 0.37615384615384617, 'identification': 0.4146153846153846, 'intellectual_property': 0.45307692307692315, 'ip_address': 0.4915384615384616, 'legal_matter': 0.53, 'location': 0.5684615384615386, 'name': 0.606923076923077, 'party': 0.6453846153846154, 'party_identification': 0.6838461538461539, 'phone_number': 0.7223076923076923, 'property': 0.7607692307692309, 'risk_factor': 0.7992307692307693, 'sanction': 0.8376923076923077, 'security': 0.8761538461538463, 'shipment': 0.9146153846153847, 'tradename': 0.9530769230769232, 'vessel': 0.9915384615384616}
# color_map = {key: viridis_cmap(value) for key, value in val_map.items()}
# Set up the Streamlit app
st.title("Mortal Mint Network Graph Query mm_streamlit.py")

# Get user input for character name
search_value = st.text_input("Enter the value to search the Mortal Mint Knowledge Graph for:", value ="")
show_legend=tog.st_toggle_switch(label="Toggle Legend",
                    key="Key1",
                    default_value=True,
                    label_after = False,
                    inactive_color = '#D3D3D3',
                    active_color="#11567f",
                    track_color="#29B5E8"
                    )
# Use the viridis colormap
viridis_cmap = plt.colormaps.get_cmap('viridis')
layout_option = st.sidebar.selectbox('Layout for network graphs:', ('Kamada', 'Shell', 'Spring',
                                                                    'Circular', 'Random'))

#load sythetic gml file
G = nx.read_gml('synthetic_mm.gml')
# color_map = [val_map.get(attributes['table'], 0.25) for node, attributes in G.nodes(data=True)]

if search_value != '':
    number_of_edges = st.sidebar.slider('Number of edges to show:', 1, 10, 2)
    G=nx_util.get_search_result_subgraph(G, search_value, number_of_edges)

node_table_labels = {node: attributes['table'] for node, attributes in G.nodes(data=True)}
network_graph = nx_util.create_network_graph(G, show_legend, layout_option)

#adds click interaction
# selected_points = plotly_events(network_graph)
# if selected_points:
#     a=selected_points[0]
#     st.write(a)

#previous way to plot graph, no click interaction
st.plotly_chart(network_graph, use_container_width=True)

if search_value:
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        display_ids = tog.st_toggle_switch(label="Display Node IDs",
                                           key="Key2",
                                           default_value=True,
                                           label_after=False,
                                           inactive_color='#D3D3D3',
                                           active_color="#11567f",
                                           track_color="#29B5E8"
                                           )
    with col2:
        display_source = tog.st_toggle_switch(label="Display Data Source",
                                              key="Key3",
                                              default_value=True,
                                              label_after=False,
                                              inactive_color='#D3D3D3',
                                              active_color="#11567f",
                                              track_color="#29B5E8"
                                              )
    # with col3:
        # st.download_button(label="Download ppt", file_name=f"{search_value} snapshot.pptx",



     # = ["phone_number", "full_address", "electronic_address", "address"]
    attribute_options = nx_util.get_unique_attribute_names(G)
    attributes= st.multiselect(label = "**Attributes to display**", options = attribute_options,
                               default= ["phone_number", "full_address", "electronic_address", "address"])

    # Create a 3 x 3 grid using beta_columns
    cols = [st.columns(3) for _ in range(3)]

    # Display the attribute data in the grid
    for i, attribute in enumerate(attributes):
        row = i // 3
        col = i % 3
        with cols[row][col]:
            nx_util.display_attribute_data(G, attribute, display_ids, display_source)
