import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import networkx.algorithms.community as nx_comm
from math import isnan
import numpy as np

def synthetic_to_graph(df):
    # df = pd.read_csv(file, low_memory=False)
    # split into edge and node types
    edge_pd = df[df['table_type'] == 'edge'].drop(columns=['table_type']).rename(
        columns={"from_id": "source", "to_id": "target"})
    node_pd = df[df['table_type'] != 'edge'].drop(columns=['table_type'])
    # get unique node and edge names
    edge_tables = edge_pd['table'].unique()
    node_tables = node_pd['table'].unique()
    # start graph and add in all nodes
    G = nx.Graph()
    G.add_nodes_from(node_pd['guid'].tolist())
    # add in edges with attributes
    for i in edge_tables:
        sub_df = edge_pd.loc[edge_pd['table'] == i]
        # sub_df = edge_pd.loc[edge_pd['table'] == i].dropna(axis=1, how='all')
        sub_df = sub_df.astype(str)
        H = nx.from_pandas_edgelist(sub_df, edge_attr=True)
        G = nx.compose(G, H)
    # add in node attributes
    for i in node_tables:
        sub_df = node_pd.loc[node_pd['table'] == i]
        # sub_df = node_pd.loc[node_pd['table'] == i].dropna(axis=1, how='all')
        sub_df = sub_df.astype(str)
        sub_dict = [v.dropna().to_dict() for k, v in sub_df.iterrows()]
        node_attr = dict(zip(sub_df['guid'].tolist(), sub_dict))
        nx.set_node_attributes(G, node_attr)

    return G, node_attr

df = pd.read_excel('synthetic_graph_data_small.xlsx')
# df = df.replace('nan', np.nan)
# df = df[df['raw_source']=='bsa']
# X = df[(df['raw_source']=='bsa') & (df['table_type']=='edge')].head(100)
# Y = df[(df['raw_source']=='bsa') & (df['table_type']!='edge')].head(100)
# XY = pd.concat([X,Y], ignore_index=True)

#drop timestamp column
df = df.drop(columns=['timestamp','from_date',
                      'to_date',
                      'datetime',
                      'observationtime',
                      'datetime',
                      'filing_date'])

#cast all columns as string
# df = df.astype(str)
G, node_attributes = synthetic_to_graph(df)
nx.write_gml(G, "synthetic_mm.gml")

