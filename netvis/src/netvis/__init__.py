# Load the data in the dataframe
import pandas as pd
asn_df = pd.read_csv('data/asn.tsv', sep='\t', header=0, index_col=None, usecols=['Asn', 'As_name']).drop_duplicates(keep='first')