import pandas as pd
import random
import subprocess
import io
import zipfile
import os
import socket
from pyvis.network import Network

from netvis import asn_df

# Routine to find IP address
def get_ip():
    # Obtain IP address of source
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ipaddr = s.getsockname()[0]
    s.close()
    return ipaddr

'''
class NetGraph

An object class containing the nodes of a network and
the connections between the nodes. The data of the node
is stored in a DataFrame object and the connections
are stored in an edge list.
'''
class NetGraph:
    # Initialize NetGraph object
    def __init__(self, nodes=pd.DataFrame(columns=['Ip', 'Asn', 'As_name']), edge_list=pd.DataFrame(columns=['Ip', 'next_Ip']), source=pd.DataFrame(columns=['Src_ip'])):
        self.nodes = nodes
        self.edge_list = edge_list
        # Obtain IP address of source
        self.source = pd.DataFrame({'Src_ip':[get_ip()]})
    
    # Add to NetGraph by performing traceroute using mtr
    def traceroute(self, dest, logfile):
        # Get output of mtr command
        csv_str = subprocess.run(['mtr', '-4', '-zCnc8', dest], stdout=subprocess.PIPE).stdout.decode('utf-8')
        # Log the raw data output on file
        fh = open(logfile, 'a')
        fh.write(csv_str)
        fh.write('*\n')
        fh.close()
        # Create dataframe from CSV output
        union_df = pd.read_csv(io.StringIO(csv_str), usecols=['Ip', 'Asn'])
        union_df = union_df.loc[union_df['Ip'] != '???']
        union_df['Asn'] = union_df['Asn'].apply(lambda x: 0 if x.partition(' ')[0][2:] == '???' else int(x.partition(' ')[0][2:]))
        # Join with ASN dataframe and retain requried columns
        union_df = union_df.merge(asn_df, on='Asn', how='left')[['Ip','Asn','As_name']]
        # Add row for host IP
        ipaddr = get_ip()
        new_row = pd.DataFrame({'Ip' : ipaddr, 'Asn' : 0, 'As_name' : None}, index=[0])
        union_df = pd.concat([new_row, union_df]).reset_index(drop=True)
        # Pair up adjacent rows using concat and drop last row
        edge_df = pd.concat([union_df, union_df.shift(-1).add_prefix('next_')], axis=1)[:-1][['Ip', 'next_Ip']]
        # Create a temporary new NetGraph object
        merge_ng = NetGraph(union_df, edge_df)
        # Unite the two objects
        self.union(merge_ng)
 
    # Add nodes and edges of another NetGraph
    def union(self, ng):
        # Merge nodes
        self.nodes = pd.concat([self.nodes, ng.nodes], axis=0, ignore_index=True).drop_duplicates(keep='first')
        # Augment edge list
        self.edge_list = pd.concat([self.edge_list, ng.edge_list], axis=0, ignore_index=True).drop_duplicates(keep='first')
        # Add sources
        self.source = pd.concat([self.source, ng.source], axis=0, ignore_index=True).drop_duplicates(keep='first')
    
    # Save NetGraph to Excel files for processing
    def save(self, filename):
        with pd.ExcelWriter(filename) as writer:
            self.nodes.to_excel(writer, sheet_name='nodes', index=False)
            self.edge_list.to_excel(writer, sheet_name='edges', index=False)
            self.source.to_excel(writer, sheet_name='sources', index=False)

    def generate_color(self):
        c = '#%06x' % random.randint(0, 0xFFFFFF)
        while(c in self.color):
            c = '#%06x' % random.randint(0, 0xFFFFFF)
        return c

    # Display the NetGraph as a graph in HTML format
    def disp(self):
        net = Network(directed=True,height="98vh",bgcolor="#FAF0E6")
        self.nodes.reset_index(inplace=True)
        num_rows = self.nodes.shape[0]
        self.color = {"#FAF0E6":"BGcolor"}
        self.mp = {}
        print(self.source)

        # Adding edges in net
        for i in range(0,num_rows):
            Asn, ASName, Ip = self.nodes.loc[i,["Asn","As_name","Ip"]]
            title1 = f"AS Number: {Asn}\nAS Name: {ASName}"
            title2 = "AS Number unavailable"

            if (Ip in self.source):               
                net.add_node(Ip,shape='square',title="Destination",physics="fixed")
            elif (Asn == 0):
                if not(0 in self.mp):
                    c = self.generate_color()
                    self.color[c] = "no ASN"
                    self.mp[0] = c

                net.add_node(Ip,color=self.mp[0],title=title2)
            else:
                if not (Asn in self.mp):
                    c = self.generate_color()
                    self.color[c] = Asn
                    self.mp[Asn] = c
                    
                net.add_node(Ip,color=self.mp[Asn],title=title1,shape='triangle')
        # Adding edges in net
        net.add_edges(tuple(zip(self.edge_list.loc[:,"Ip"],self.edge_list.loc[:,"next_Ip"])))
        # edge will take color from both nodes
        net.inherit_edge_colors('both')
        # produces index.html
        net.write_html('server/static/graph.html',notebook=False)

        # Storing legends data in csv
        legend_data = [list(self.color.keys())[1:],list(self.color.values())[1:]]
        df = pd.DataFrame(legend_data)
        df = df.T
        df.columns = ["Color","Description"]
        df.to_csv('./data/legends/legends.csv',index=False,header=True)

# Utility to load NetGraph object from Excel file
def load(filename):
    node_df = pd.read_excel(filename, sheet_name='nodes')
    edge_df = pd.read_excel(filename, sheet_name='edges')
    source_df = pd.read_excel(filename, sheet_name='sources')
    return NetGraph(nodes=node_df, edge_list=edge_df, source=source_df)
