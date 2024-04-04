class Graph:
    """
    This is the graph object returned by the GraphRetriever
        Attributes
        ----------
        ids_dict : dict(str, list[int])
            dictionary containing each node type as key and as value the node ids for this node type in the complete
            neo4j database, e.g., node_type: [0, 1, 2]
        feature_dict: dict(str, list[any])
            dictionary containing each node type as key and as value the node features for this node type in the
             complete neo4j database
        edge_index_dict: dict(tuple[str, str, str], [list, list])
            dictionary containing each edge type (tuple of source_node_type, edge_label, target_node_type) as key and as
            value the edge index for this edge type in the complete neo4j database
    """
    def __init__(self):
        self.ids_dict = dict()
        self.feature_dict = dict()
        self.edge_index_dict = dict()

    def add_ids(self, key, ids):
        """This functions adds the ids of a specific node type into the graphs' ids_dicts
         Parameters
        ----------
        key : str
            the node type for the dictionary
        ids : list[int]
            the list of node ids for this specific node type
        """
        self.ids_dict[key] = ids

    def add_features(self, key, features):
        """This functions adds the features of a specific node type into the graphs' feature_dict
                 Parameters
                ----------
                key : str
                    the node type for the dictionary
                features : list[any]
                    the list of node features for this specific node type
                """
        self.feature_dict[key] = features

    def add_edge_index(self, key, edge_index):
        """This functions adds the edge index of a specific edge type into the graphs' edge_index_dict
                         Parameters
                        ----------
                        key : tuple[str, str, str]
                            the edge type for the dictionary (tuple of source_node_type, edge_label, target_node_type)
                        edge_index : [list, list]
                            the remapped edge index for the respective edge type containing a list that contains at the
                            first position all source node indices and at the secind position the targte node ids for
                             this specific edge type
                        """
        self.edge_index_dict[key] = edge_index

    def __str__(self):
        ##TODO
        """
        Just returns the graph object a s string
        :return: the graph as a string format
        """
        print(self.ids_dict)
        print(self.feature_dict)
        print(self.edge_index_dict)
        return ""