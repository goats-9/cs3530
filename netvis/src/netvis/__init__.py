# Load the data in the dataframe
import pandas as pd
asn_df = pd.read_csv('https://raw.githubusercontent.com/goats-9/cs3530-assignments/main/netvis/data/asn.tsv', sep='\t', header=0, index_col=None, usecols=['Asn', 'As_name']).drop_duplicates(keep='first')