from impl.NeoDriver import NeoDriver
from meta.GraphObject import Graph
from neo4j import GraphDatabase


class GraphRetriever(NeoDriver):
    """
    Graph Retriever object is used for querying a neo4j graph to a heterogeneous pytorch geometric graph. The output
    is the Graph-object which contains a dictionary for the node ids (node_type: node_ids), a dictionary for the node
    features (node_type: node_features) and a dictionary for the edge index (edge_type: edge_index)
    Everything is done with pure python function, i.e., a later conversion to torch tensors is required
    However installing torch for the usage is not required. The only requirement is the package neo4j version >= 5.19.0

    Parameters
    ----------
    uri : str
        The arg is used to connect to the neo4j database.
        Provide a link, e.g., "bolt://localhost:7687"
    auth: tuple
        The arg is used to connect to the neo4j database.
        Provide a tuple consisting of the username and password for the database access, e.g., ("neo4j", "password")
    Attributes
    ----------
    driver : Neo4jDriver
        This is where we store the connection to the neo4j driver given users uri and auth
    node_types : list[str]
        This is the store for the list of node types present in the database. Each node type is a string
    edge_types : list[tuple]
        This is the store for the list of edge types present in the database. Each edge type is a triple of
        (source_node_type, edge_label, target_node_type)
    id_to_idx_dict: dict(dict(int:int))
        This is the store for the edge index remapping. Retrieved node ids from the database need to be remapped
         to the index of the representative feature matrix of the node type. It is a dictionary of dictionaries with
         the node type as key and as value a dictionary of the node_id: node_idx
    graph_object: Graph
        This stores the final resulting graph object
    """

    def __init__(self, uri, auth):
        driver = GraphDatabase.driver(uri, auth=auth)
        super().__init__(driver)

        self.node_types = None
        self.edge_types = None
        self.id_to_idx_dict = dict()
        self.graph_object = Graph()

    def load_graph(self):
        """We need to load the graph from the graph database and need to transform it. This loads the graph into
        the graph object
                Returns
                -------
                graph_object
                    Graph object- the final graph object in pytorch geometric format

        """
        self.node_types = self.query_all_node_types()
        self.edge_types = self.query_all_edge_types()
        print(self.node_types)
        print(self.edge_types)
        self.set_id_dict()
        self.set_id_to_idx_dict()
        self.set_edge_dict()
        # self.set_feature_dict()
        return self.graph_object

    def set_id_to_idx_dict(self):
        """This functions calculates the dictionary id_to_idx_dict, ie., for each node type a dictionary is created
            which contains the node id as key and the index of this id in the matrix as value"""
        graph_object = self.graph_object
        for node_type in self.node_types:
            self.id_to_idx_dict[node_type] = {node_id: idx for idx, node_id in
                                              enumerate(graph_object.ids_dict[node_type])}

    def set_id_dict(self):
        """This function sets all node ids for each node type as a dictionary into the graph object,
            i.e., dict(node_type: node_id)
            Raise:
            :exception if node types are not loaded"""
        if self.node_types is None: raise Exception("Node types not queried!")
        for node_type in self.node_types:
            ids = self.query_node_ids_per_type(node_type)
            self.graph_object.add_ids(node_type, ids)

    def set_feature_dict(self):
        """This function sets all node features (can be adopted in the NeoDriver) for each node type as a dictionary
         into the graph object, i.e., dict(node_type: node_features)
          Raise:
            :exception if node types are not loaded
          """
        if self.node_types is None: raise Exception("Node types not queried!")
        for node_type in self.node_types:
            node_features = self.query_node_features_per_type(node_type)
            self.graph_object.add_features(node_type, node_features)

    def get_remapped_edge_index(self, edge_type, edge_index):
        """This function constructs the remapped edge index so that the resulting edge index contains the node indices
         from the feature matrix instead of the originally returned node ids.
         Parameters
        ----------
        edge_type : tuple(str, str, str)
            The respective edge type that contains a tuple of the source_node_type, edge_label, target_node_type
        edge_index : [list, list]
            The original edge index containing source node ids as list at the first position and at the second position
            the target nodes ids as list for the respective edge type

        Returns
        -------
        remapped_edge_index: [list, list]
            The remapped edge index containing source node indices as list at the first position and at the
            second position the target nodes indices as list for the respective edge type"""
        source, _, target = edge_type
        source_id_to_idx = self.id_to_idx_dict[source]
        target_id_to_idx = self.id_to_idx_dict[target]
        remapped_edge_index = list(map(lambda source_id: source_id_to_idx[source_id], edge_index[0])), \
                              list(map(lambda target_id: target_id_to_idx[target_id], edge_index[1]))
        return remapped_edge_index

    def set_edge_dict(self):
        """This function sets all edge indices for each edge type as a dictionary into the graph object,
         i.e., dict(edge_type: remapped_edge_index)
                  Raise:
                    :exception if edge types are not loaded
                  """
        if self.edge_types is None: raise Exception("Edge types not queried!")
        for edge_type in self.edge_types:
            edge_index = self.get_edge_index_per_type(edge_type)
            edge_index = self.get_remapped_edge_index(edge_type, edge_index)
            self.graph_object.add_edge_index(edge_type, edge_index)

    def get_graph(self):
        """This function returns the constructed graph object
                Returns
                -------
                graph_object
                    The constructed graph object based on the noe4j database
        """
        return self.graph_object
