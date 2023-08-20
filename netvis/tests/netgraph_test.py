import netvis.NetGraph as ng

ngraph = ng.NetGraph()
ngraph.traceroute('github.com')
ngraph.traceroute('bbc.com')
ngraph.disp()