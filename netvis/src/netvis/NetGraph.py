import pandas as pd
import subprocess
import io
import zipfile
import os
from datetime import datetime
from pyvis.network import Network
# openpyxl, pyvis

from netvis import asn_df

'''
class NetGraph

An object class containing the nodes of a network and
the connections between the nodes. The data of the node
is stored in a DataFrame object and the connections
are stored in an edge list.
'''
class NetGraph:
    def __init__(self, nodes=pd.DataFrame(columns=['Ip', 'Asn', 'As_name']), edge_list=pd.DataFrame(columns=['Ip', 'next_Ip'])):
        self.nodes = nodes
        self.edge_list = edge_list
    
    def traceroute(self, dest):
        # Get output of mtr command
        csv_str = subprocess.run(['mtr', '-zCnc4', dest], stdout=subprocess.PIPE).stdout.decode('utf-8')
        # Create dataframe from CSV output
        union_df = pd.read_csv(io.StringIO(csv_str), usecols=['Ip', 'Asn'])
        union_df = union_df.loc[union_df['Ip'] != '???']
        union_df['Asn'] = union_df['Asn'].apply(lambda x: 0 if x[2:] == '???' else int(x[2:]))
        # Join with ASN dataframe and retain requried columns
        union_df = union_df.merge(asn_df , on='Asn', how='left')[['Ip','Asn','As_name']]
        # Pair up adjacent rows using concat and drop last row
        edge_df = pd.concat([union_df, union_df.shift(-1).add_prefix('next_')], axis=1)[:-1][['Ip', 'next_Ip']]
        # Create a temporary new NetGraph object
        merge_ng = NetGraph(union_df, edge_df)
        # Unite the two objects
        self.union(merge_ng)
    
    def union(self, ng):
        # Merge nodes
        self.nodes = pd.concat([self.nodes, ng.nodes], axis=0, ignore_index=True).drop_duplicates(keep='first')
        # Augment edge list
        self.edge_list = pd.concat([self.edge_list, ng.edge_list], axis=0, ignore_index=True).drop_duplicates(keep='first')
    
    def save(self, filename):
        with pd.ExcelWriter(filename) as writer:
            self.nodes.to_excel(writer, sheet_name='nodes', index=False)
            self.edge_list.to_excel(writer, sheet_name='edges', index=False)

    def disp(self):
        net = Network(directed=True,height="100vh")
        num_rows = self.nodes.shape[0]
        
        # Adding edges in net
        for i in range(0,num_rows):
            Asn, ASName, Ip = self.nodes.loc[i,["Asn","As_name","Ip"]]
            title1 = f"AS Number: {Asn}\nAS Name: {ASName}"
            title2 = "AS Number unavailable"
            if (i == 0):
                net.add_node(Ip,group=3,shape='image',image='data:image/png;base64,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',title=title2)
            elif (Asn == 0):
                net.add_node(Ip,group=1,title=title2)
            else:
                net.add_node(Ip,group=2,title=title1)
        # Adding edges in net
        net.add_edges(tuple(zip(self.edge_list.loc[:,"Ip"],self.edge_list.loc[:,"next_Ip"])))
        # edge will take color from both nodes
        net.inherit_edge_colors('both')
        # produces index.html
        net.show('index.html',notebook=False)

def load(filename):
    node_df = pd.read_excel(filename, sheet_name='nodes')
    edge_df = pd.read_excel(filename, sheet_name='edges')
    return NetGraph(nodes=node_df, edge_list=edge_df)