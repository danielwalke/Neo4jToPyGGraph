from impl.GraphRetriever import GraphRetriever

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "password")

graphRetriever = GraphRetriever(URI, AUTH)
graphRetriever.load_graph()
graphObject = graphRetriever.get_graph()
print(graphObject)