import re
import networkx as nx
import matplotlib as plt
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

def get_unique_attribute_names(G):
    """
    Get all unique attribute names from a NetworkX graph.

    :param G: NetworkX graph
    :return: List of unique attribute names
    """
    unique_attributes = set()

    for _, attributes in G.nodes(data=True):
        unique_attributes.update(attributes.keys())

    return list(unique_attributes)

def search_network(graph, string_to_search_for):
    """
    Given a networkx graph and a string to search for,
    return a list of node ids that have a matching attribute value.

    :param graph: networkx graph object
    :param string_to_search_for: string or substring value to look for anywhere in the graph
    :return: list of node ids
    """
    matching_nodes = []
    for node, attrs in graph.nodes(data=True):
        for attr, value in attrs.items():
            if re.search(string_to_search_for, str(value), re.IGNORECASE):
                matching_nodes.append(node)
                break
    return matching_nodes

def find_nodes_with_attr(G, attr_value):
    """
    Given a networkx graph G and a string variable attr_value,
    return the nodes in the graph that have an attribute with a value equal to attr_value.
    """
    matching_nodes = []
    for node in G.nodes:
        node_attrs = G.nodes[node]
        for attr in node_attrs:
            if node_attrs[attr] == attr_value:
                matching_nodes.append(node)
                break
    return matching_nodes

def get_subgraph_within_n_steps(G, node_id, n=3):
    """
    Given a networkx graph G and a node ID, return the subgraph that includes
    all nodes within n hops of the target node.
    """
    subgraph_nodes = set()
    if type(node_id) == list:
        nodes_to_check = node_id
    else:
        nodes_to_check = [node_id]
    for i in range(n):
        next_nodes = set()
        for node in nodes_to_check:
            if node not in subgraph_nodes:
                subgraph_nodes.add(node)
                next_nodes.update(G.neighbors(node))
        nodes_to_check = list(next_nodes)
    return G.subgraph(subgraph_nodes)

def get_attr_dict(G, attr_name):
    #todo think if there is a better way to return values instead of a
    # dictionary of node ids and nested dictionaries with source and attribute values
    """
    Given a networkx graph G and an attribute name, return a dictionary
    that includes the value found, the "raw source" key value, and the node ID
    where the attribute was found.
    """
    attr_dict = {}
    for node_id, attrs in G.nodes(data=True):
        if attr_name in attrs:
#             attr_value = attrs[attr_name]
            attr_dict[node_id] = {'raw_source': attrs['raw_source'], attr_name: attrs[attr_name]}
    return attr_dict

def display_data(node_data, display_node_id = True, display_source = True):
    """
    Given a dictionary of node data, display the values and sources in a streamlit app.
    :param node_data:
    :return:
    ex:
        Node ID: cddb5f32-d12c-3846-8720-c60712839f6b
        raw_source: bsa
        street_address1: 90396 Davis Spring
        Node ID: 4a272602-9fa2-3a51-981d-017da99f2e0f
        raw_source: bsa
        street_address1: 82654 Jessica Orchard
        Node ID: 03b89440-3dc5-3c6e-b54f-b5f80c6f9058
        raw_source: bsa
        street_address1: 829 Jacob Groves
    """
    for node_id, attributes in node_data.items():
        if display_node_id:
            st.write(f"Node ID: {node_id}")
        for attribute, value in attributes.items():
            if attribute == 'raw_source' and not display_source:
                pass
            else:
                st.write(f"{value}")

def display_attribute_data(G, attribute_name, display_node_id=True, display_source=True):
    """
    Given a networkx graph G and an attribute name, display the values and sources in a streamlit app.
    :param G:
    :param
    :return:
    """
    attr_dict = get_attr_dict(G, attribute_name)

    st.markdown(f"**{attribute_name.title()} Data**")
    # st.write(f"Displaying data for attribute: {attribute_name.title()}")
    display_data(attr_dict, display_node_id=display_node_id, display_source=display_source)
    st.markdown("##")

def get_search_result_subgraph(graph, string_to_search_for, n):
    node_results = search_network(graph, string_to_search_for)
    if node_results:
        sub_graph = get_subgraph_within_n_steps(graph, node_results, n)
        return sub_graph
    else:
        st.write("No results found for '{}'. Displaying full graph".format(string_to_search_for))
        return graph
def draw_graph_with_highlighted_node(graph, node_ids, highlight_color='red', node_size=40):
    """
    Draw a NetworkX graph with a highlighted node.

    Parameters:
    graph (networkx.Graph): The NetworkX graph to be drawn.
    node_ids (list of str): a list containing all ID of the nodes to be highlighted.
    highlight_color (str, optional): The color for highlighting the node. Default is 'red'.
    node_size (int, optional): The size of the nodes in the graph. Default is 2000.

    Returns:
    None
    """
    pos = nx.spring_layout(graph)

    # Draw all nodes except the highlighted one
    non_highlighted_nodes = [node for node in graph.nodes() if node not in node_ids]
    nx.draw_networkx_nodes(graph, pos, nodelist=non_highlighted_nodes, node_size=node_size)

    # Draw the highlighted node
    nx.draw_networkx_nodes(graph, pos, nodelist=node_ids, node_color=highlight_color, node_size=node_size * 1.5,
                           linewidths=3)

    # Draw the edges and labels
    nx.draw_networkx_edges(graph, pos)
    plt.show()

def create_network_graph(G, display_legend=True, layout='Spring'):

    if layout == 'Kamada':
        pos = nx.kamada_kawai_layout(G)
    if layout == 'Shell':
        pos = nx.shell_layout(G)
    if layout == 'Spring':
        pos = nx.spring_layout(G, k=.2, iterations=20, seed=42)
    if layout =='Circular':
        pos = nx.circular_layout(G)
    # case 'Spectral':
    #     pos = nx.spectral_layout(G)
    if layout == 'Random':
        pos = nx.random_layout(G)

    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y, line=dict(width=1, color='#888'), hoverinfo='none', mode='lines'
    )

    node_x = [pos[node][0] for node in G.nodes()]
    node_y = [pos[node][1] for node in G.nodes()]
    node_labels = ['<br>'.join(f'{key}: {value}' for key, value in G.nodes[node].items()) for node in G.nodes()]
    node_tables = [G.nodes[node]["table"] for node in G.nodes()]

    node_trace = px.scatter(x=node_x, y=node_y,
                            text=node_labels,
                            color=node_tables,
                                color_discrete_sequence=px.colors.qualitative.D3)

    for trace in node_trace.data:
        trace.update(dict(mode='markers', marker=dict(size=10, line_width=2), hovertemplate='%{text}'))

    fig = go.Figure(data=[edge_trace] + list(node_trace.data),
                    layout=go.Layout(
                        showlegend=display_legend,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        height=500,
                        # width=800,
                        legend=dict(
                            # Adjust click behavior
                            itemclick="toggleothers",
                            itemdoubleclick="toggle"
                        )
                    ))
    return fig
