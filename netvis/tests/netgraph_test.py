import netvis as nv
import os

ngraph = nv.NetGraph.NetGraph()
ngraph.traceroute('github.com')
ngraph.traceroute('bbc.com')
ngraph.save('test.xlsx')

n2 = nv.NetGraph.load('test.xlsx')
n2.disp()
os.remove('test.xlsx')