import pandas as pd
from . import NetGraph

def load(filename):
    node_df = pd.read_excel(filename, sheet_name='nodes')
    edge_df = pd.read_excel(filename, sheet_name='edges')
    return NetGraph.NetGraph(nodes=node_df, edge_list=edge_df)