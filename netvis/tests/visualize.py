import netvis as nv
import os

dirpath = 'data/netgraphs/'
directory = os.fsencode(dirpath)
ng = nv.NetGraph.NetGraph()

# Collect all NetGraphs obtained
for file in os.listdir(directory):
    fname = os.fsdecode(file)
    if fname.endswith(".xlsx"):
        ng1 = nv.NetGraph.load(os.path.join(dirpath,fname))
        ng.union(ng1)

# Display integrated graph
ng.disp()