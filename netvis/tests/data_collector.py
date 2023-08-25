import netvis as nv
import socket

# Collect data using library functions
def collect_data(urlfile, excel_file, logfile):
    fh = open(urlfile, 'r')
    L = fh.readlines()
    ngraph = nv.NetGraph.NetGraph()
    for line in L:
        ngraph.traceroute(line.rstrip(), logfile)
    ngraph.save(excel_file)

# Call the function here with correct arguments
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ipaddr = s.getsockname()[0]
s.close()
urlfile='data/urls.txt'
excel_file = 'data/netgraphs/netgraph_'+ipaddr+'.xlsx'
logfile = 'data/logs/mtr_'+ipaddr+'.txt'
collect_data(urlfile, excel_file, logfile)
