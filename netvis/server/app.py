from flask import Flask, render_template, url_for
import os
import netvis as nv

app = Flask(__name__)

@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                 endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

@app.route('/')
def hello():
    dirpath = '../data/netgraphs/'
    directory = os.fsencode(dirpath)
    ng = nv.NetGraph.NetGraph()

    # Collect all NetGraphs obtained
    for file in os.listdir(directory):
        fname = os.fsdecode(file)
        if fname.endswith(".xlsx"):
            ng1 = nv.NetGraph.load(os.path.join(dirpath,fname))
            ng.union(ng1)

    # Display integrated graph
    color,desc = ng.disp()
    return render_template('index.html',ittr = list(zip(color,desc)))

if __name__ == '__main__':
    app.run(debug=True)