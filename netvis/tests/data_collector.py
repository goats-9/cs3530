import netvis as nv
import socket

# Collect data using library functions
def collect_data(urlfile, excel_file):
    fh = open(urlfile, 'r')
    L = fh.readlines()
    ngraph = nv.NetGraph.NetGraph()
    for line in L:
        ngraph.traceroute(line)
    ngraph.save(excel_file)

# Call the function here with correct arguments
urlfile='urls.txt'
ipaddr = socket.gethostbyname(socket.gethostname())
excel_file='netgraph_'+ipaddr+'.txt'
collect_data(urlfile, excel_file)
