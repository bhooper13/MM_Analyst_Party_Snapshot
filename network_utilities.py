import re
import networkx as nx
import matplotlib as plt
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from collections import deque

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
def get_attribute_values(graph, attribute_name):
    """
    Given a networkx graph and an attribute name, this function returns a list of all values of the
    specified attribute for each node in the graph.

    :param graph: networkx graph
    :param attribute_name: string, name of the attribute to collect values for
    :return: list of attribute values
    """
    attribute_values = [data[attribute_name] for _, data in graph.nodes(data=True) if attribute_name in data]
    return attribute_values

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
    if attr_dict:
        st.markdown(f"**{attribute_name.title()} Data**")
        # st.write(f"Displaying data for attribute: {attribute_name.title()}")
        display_data(attr_dict, display_node_id=display_node_id, display_source=display_source)
        st.markdown("##")
    else:
        st.markdown(f"**No data for {attribute_name.title()}**")

def split_graph_by_distance(graph, node_id, number_of_edges=3):
    """
    Given a node id and a graph, this function returns two graph objects:
    - one graph object with nodes connected 1 edge away from the given node_id
    - a second graph object with nodes connected 2 to 5 edges away from the given node_id

    :param graph: A NetworkX graph object
    :param node_id: The node id for which the graph objects need to be created
    :return: A tuple containing the two graph objects (one_edge_away, two_to_five_edges_away)
    """

    # Initialize the two graph objects
    one_edge_away = nx.Graph()
    two_to_n_edges_away = nx.Graph()

    # Iterate through 1 to 5 edges away from the given node_id
    for i in range(1, number_of_edges + 1):
        # Get the nodes at the current distance (i) from the given node_id
        current_level_nodes = nx.single_source_shortest_path_length(graph, node_id, cutoff=i)
        current_level_nodes = {node: dist for node, dist in current_level_nodes.items() if dist == i}
        # If the current distance is 1, add nodes and edges to the one_edge_away graph
        if i == 1:
            one_edge_away.add_nodes_from([(node, graph.nodes[node]) for node in current_level_nodes])
            one_edge_away.add_edges_from([(node_id, neighbor) for neighbor in current_level_nodes])
        elif 1 < i <= number_of_edges:
            two_to_n_edges_away.add_nodes_from([(node, graph.nodes[node]) for node in current_level_nodes])
            two_to_n_edges_away.add_edges_from([(node_id, neighbor) for neighbor in current_level_nodes])
    return one_edge_away, two_to_n_edges_away

def get_search_result_subgraph(graph, string_to_search_for, n):
    node_results = search_network(graph, string_to_search_for)
    if node_results:
        sub_graph = get_subgraph_within_n_steps(graph, node_results, n)
        return sub_graph, node_results
    else:
        st.write("No results found for '{}'. Displaying full graph".format(string_to_search_for))
        return graph, None

def queue(a, b, qty):
    """either x0 and x1 or y0 and y1, qty of points to create"""
    q = deque()
    q.append((0, qty - 1))  # indexing starts at 0
    pts = [0] * qty
    pts[0] = a
    pts[-1] = b  # x0 is the first value, x1 is the last
    while len(q) != 0:
        left, right = q.popleft()  # remove working segment from queue
        center = (left + right + 1) // 2  # creates index values for pts
        pts[center] = (pts[left] + pts[right]) / 2
        if right - left > 2:  # stop when qty met
            q.append((left, center))
            q.append((center, right))
    return pts

def make_middle_points(first_x, last_x, first_y, last_y, qty):
    """line segment end points, how many midpoints, hovertext"""
    # Add 2 because the origin will be in the list, pop first and last (the nodes)
    middle_x_ = queue(first_x, last_x, qty + 2)
    middle_y_ = queue(first_y, last_y, qty + 2)
    middle_x_.pop(0)
    middle_x_.pop()
    middle_y_.pop(0)
    middle_y_.pop()
    return middle_x_, middle_y_

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
    if layout == 'Random':
        pos = nx.random_layout(G)

    EDGE_POINTS_QUANTITY = 10
    EDGE_POINTS_OPACITY = 0
    edge_x = []
    edge_y = []
    edge_middle_y = []
    edge_middle_x = []
    edge_middle_text = []

    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

        # the 3 is points per line; x0 at the end is for hovertext
        middle_x, middle_y = make_middle_points(x0, x1, y0, y1, EDGE_POINTS_QUANTITY)
        edge_middle_x.extend(middle_x)
        edge_middle_y.extend(middle_y)

        # edge_middle_text.extend([f"EDGE{idx0}{idx1}"] * EDGE_POINTS_QUANTITY)
        #adds hover text to the edges
        edge_middle_text.extend(['<br>'.join(f'{key}: {value}' for key, value in G.edges[edge].items())]
                                * EDGE_POINTS_QUANTITY)

    # edge_labels = ['<br>'.join(f'{key}: {value}' for key, value in G.edges[edge].items()) for edge in G.edges()]

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y, line=dict(width=1, color='#888'), hovertemplate='%{text}',mode='lines')

    # for trace in edge_trace.data:
    #     trace.update(
    #         # dict(mode='lines', marker=dict(size=10, line_width=2),
    #                       hovertemplate='%{text}')

    #made the edges have hover text
    m2node_trace = go.Scatter(x=edge_middle_x, y=edge_middle_y, mode="markers", showlegend=False,
                              hovertemplate="%{hovertext}",
                              hovertext=edge_middle_text,
                              marker=go.scatter.Marker(opacity=EDGE_POINTS_OPACITY))
    node_x = [pos[node][0] for node in G.nodes()]
    node_y = [pos[node][1] for node in G.nodes()]
    node_labels = ['<br>'.join(f'{key}: {value}' for key, value in G.nodes[node].items()) for node in G.nodes()]
    node_tables = [G.nodes[node]["table"] for node in G.nodes()]

    #determines what color to use for each node when displaying the network graph
    color_map = {
        'account': px.colors.qualitative.D3[0],
        'activity': px.colors.qualitative.D3[1],
        'additional_information': px.colors.qualitative.D3[2],
        'address': px.colors.qualitative.D3[3],
        'aircraft': px.colors.qualitative.D3[4],
        'cargo': px.colors.qualitative.D3[5],
        'container': px.colors.qualitative.D3[6],
        'cryptocurrency_address': px.colors.qualitative.D3[7],
        'cryptocurrency_cluster': px.colors.qualitative.D3[8],
        'electronic_address': px.colors.qualitative.D3[9],
        'identification': px.colors.qualitative.T10[2],
        'intellectual_property': px.colors.qualitative.T10[3],
        'ip_address': px.colors.qualitative.Plotly[0],
        'legal_matter': px.colors.qualitative.Plotly[1],
        'location': px.colors.qualitative.Plotly[2],
        'name': px.colors.qualitative.Plotly[3],
        'party': px.colors.qualitative.Plotly[4],
        'party_identification': px.colors.qualitative.Plotly[5],
        'phone_number': px.colors.qualitative.Plotly[6],
        'property': px.colors.qualitative.Plotly[7],
        'risk_factor': px.colors.qualitative.Plotly[8],
        'sanction': px.colors.qualitative.Plotly[9],
        'security': px.colors.qualitative.T10[4],
        'shipment': px.colors.qualitative.T10[5],
        'tradename': px.colors.qualitative.T10[0],
        'vessel': px.colors.qualitative.T10[1],
        'osints':px.colors.qualitative.T10[6]
    }

    node_trace = px.scatter(x=node_x, y=node_y,
                            text=node_labels,
                            color=node_tables,
                            # color_discrete_sequence=px.colors.qualitative.D3,
                            color_discrete_map=color_map)

    for trace in node_trace.data:
        trace.update(dict(mode='markers', marker=dict(size=10, line_width=2), hovertemplate='%{text}'))

    figure = go.Figure(data=[edge_trace, m2node_trace] + list(node_trace.data),
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
    return figure
