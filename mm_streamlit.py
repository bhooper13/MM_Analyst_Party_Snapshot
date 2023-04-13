import streamlit as st
# import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from streamlit_plotly_events import plotly_events
import time
import network_utilities as nx_util
import ppt_utilities as ppt_util
import plotly.io as pio
import os
import streamlit_toggle as tog
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_PARAGRAPH_ALIGNMENT as PP_ALIGN
import matplotlib.pyplot as plt
import numpy as np
pio.kaleido.scope.mathjax = None

# viridis_cmap = plt.cm.get_cmap("viridis")
val_map={'account': 0.03, 'activity': 0.06846153846153846, 'additional_information': 0.10692307692307693, 'address': 0.1453846153846154, 'aircraft': 0.18384615384615385, 'cargo': 0.22230769230769232, 'container': 0.26076923076923075, 'cryptocurrency_address': 0.2992307692307693, 'cryptocurrency_cluster': 0.33769230769230774, 'electronic_address': 0.37615384615384617, 'identification': 0.4146153846153846, 'intellectual_property': 0.45307692307692315, 'ip_address': 0.4915384615384616, 'legal_matter': 0.53, 'location': 0.5684615384615386, 'name': 0.606923076923077, 'party': 0.6453846153846154, 'party_identification': 0.6838461538461539, 'phone_number': 0.7223076923076923, 'property': 0.7607692307692309, 'risk_factor': 0.7992307692307693, 'sanction': 0.8376923076923077, 'security': 0.8761538461538463, 'shipment': 0.9146153846153847, 'tradename': 0.9530769230769232, 'vessel': 0.9915384615384616}
# color_map = {key: viridis_cmap(value) for key, value in val_map.items()}
# Set up the Streamlit app
st.title("Mortal Mint Network Graph Query")

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
    G, node_search_results_list = nx_util.get_search_result_subgraph(G, search_value, number_of_edges)

node_table_labels = {node: attributes['table'] for node, attributes in G.nodes(data=True)}
network_graph = nx_util.create_network_graph(G, show_legend, layout_option)

#adds click interaction
# selected_points = plotly_events(network_graph)
# if selected_points:
#     a=selected_points[0]
#     st.write(a)

#previous way to plot graph, no click interaction
st.plotly_chart(network_graph, use_container_width=True)
if st.button("Generate Results as PowerPoint"):
    #export network_graph as image
    pio.write_image(network_graph, 'figure.png', width=425, height=425)
    # network_graph.write_image("fig1.png")
    # ppt_util.close_specific_ppt_file(f"{search_value}_mortal_mint_snapshot.pptx")
    # time.sleep(1)
    pptx_io=ppt_util.export_to_powerpoint(G, search_value)
    # st.write(os.listdir("."))
    st.download_button("Download PowerPoint file", pptx_io,
                       file_name=f"{search_value}_mortal_mint_snapshot.pptx",
                       mime="application/vnd.openxmlformats-officedocument.presentationml.presentation")
if search_value:
    if len(node_search_results_list)>1:
        selected_node=st.selectbox("Select Node to focus on", node_search_results_list)
    else:
        selected_node=node_search_results_list[0]

     # = ["phone_number", "full_address", "electronic_address", "address"]
    #todo resolve when not all default options are in the attribute_options list
    attribute_options = nx_util.get_unique_attribute_names(G)
    default_attributes = ["phone_number", "full_address", "electronic_address", "address"]
    overlapping_attributes = list(set(default_attributes).intersection(set(attribute_options)))
    if overlapping_attributes:
        selected_attributes= overlapping_attributes
    else:
        selected_attributes = None
    attributes= st.multiselect(label = "**Attributes to display**", options = attribute_options,
                               default= selected_attributes
                               )
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        display_ids = tog.st_toggle_switch(label="Display Node IDs",
                                           key="Key2",
                                           default_value=False,
                                           label_after=False,
                                           inactive_color='#D3D3D3',
                                           active_color="#11567f",
                                           track_color="#29B5E8"
                                           )
    with col2:
        display_source = tog.st_toggle_switch(label="Display Data Source",
                                              key="Key3",
                                              default_value=False,
                                              label_after=False,
                                              inactive_color='#D3D3D3',
                                              active_color="#11567f",
                                              track_color="#29B5E8"
                                              )
    # with col3:
    # st.download_button(label="Download ppt", file_name=f"{search_value} snapshot.pptx",
    # Create a 3 x 3 grid using beta_columns

    graph_one_edge_away, graph_two_or_more_edges_away=nx_util.split_graph_by_distance(G, selected_node, number_of_edges)
    # Display the attribute data in the grid
    first_degree_container = st.container()
    first_degree_container.subheader("1st Degree Attribute Data")
    first_degree_cols = [st.columns(3) for _ in range(3)]
    with first_degree_container:
        for i, attribute in enumerate(attributes):
            row = i // 3
            col = i % 3
            with first_degree_cols [row][col]:
                nx_util.display_attribute_data(graph_one_edge_away, attribute, display_ids, display_source)

    second_degree_container = st.container()
    second_degree_container.subheader("2nd Degree or Greater Attribute Data")
    second_degree_cols = [st.columns(3) for _ in range(3)]
    with second_degree_container:
        for i, attribute in enumerate(attributes):
            row = i // 3
            col = i % 3
            with second_degree_cols [row][col]:
                nx_util.display_attribute_data(graph_two_or_more_edges_away, attribute, display_ids, display_source)

