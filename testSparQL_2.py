import rdflib

g = rdflib.Graph()

# ... add some triples to g somehow ...
g.parse("http://bioportal.bioontology.org/ontologies/BHO")

qres = g.query(
    """SELECT DISTINCT ?bleeding_disorder
       WHERE {
       }""")

for row in qres:
    print(str( row ))