import pandas as pd
import subprocess
import io

from netvis import asn_df

'''
class NetGraph

An object class containing the nodes of a network and
the connections between the nodes. The data of the node
is stored in a DataFrame object and the connections
are stored in an edge list.
'''
class NetGraph:
    def __init__(self):
        self.nodes = pd.DataFrame(columns=['Ip','Asn','As_name'])
        self.edge_list = pd.DataFrame(columns=['Ip', 'next_Ip'])
    
    def traceroute(self, dest):
        # Get output of mtr command
        csv_str = subprocess.run(['mtr', '-zCnc4', dest], stdout=subprocess.PIPE).stdout.decode('utf-8')
        # Create dataframe from CSV output
        union_df = pd.read_csv(io.StringIO(csv_str), usecols=['Ip', 'Asn'])
        union_df = union_df.loc[union_df['Ip'] != '???']
        union_df['Asn'] = union_df['Asn'].apply(lambda x: 0 if x[2:] == '???' else int(x[2:]))
        # Join with ASN dataframe and retain requried columns
        union_df = union_df.merge(asn_df , on='Asn')[['Ip','Asn','As_name']]
        # Merge nodes
        self.nodes = pd.concat([self.nodes, union_df], axis=0, ignore_index=True).drop_duplicates(keep='first')
        # Pair up adjacent rows using concat and drop last row
        union_df = pd.concat([union_df, union_df.shift(-1).add_prefix('next_')], axis=1)[:-1][['Ip', 'next_Ip']]
        # Augment adjacency list
        self.edge_list = pd.concat([self.edge_list, union_df], axis=0, ignore_index=True).drop_duplicates(keep='first')
        # drop_duplicates(keep='first')
    
    def disp(self):
        print(self.nodes)
        print(self.edge_list)