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
                net.add_node(Ip,group=3,shape='image',image='./data/Media/source.png',title=title2)
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