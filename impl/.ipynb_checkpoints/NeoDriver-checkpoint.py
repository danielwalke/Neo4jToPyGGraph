class NeoDriver:
    """
        This is the object for connecting to the neo4j database and querying all required data
            Attributes
            ----------
            driver : Neo4jDrive
                Stores the neo4j driver connection
            database: str
                A string that represents the name of the neo4j database we want to query
        """

    def __init__(self, driver):
        self.driver = driver
        self.database = "neo4j"
        self.check_connection()

    def check_connection(self):
        """Checks the connection to the neo4j database
        Raise:
            :exception if connection cannot be established
        """
        self.driver.verify_connectivity()

    def query_all_node_types(self):
        """Queries all node types from the database
        Returns
        -------
        node_types: list[str]
            Returns all node types the database
        """
        records, _, _ = self.driver.execute_query(
            """
                MATCH (n)
                WITH DISTINCT labels(n) AS node_type
                RETURN node_type
            """,
            database_=self.database,
        )
        node_type_lists = list(map(lambda record: record.data()["node_type"], records))
        node_types = list(map(lambda filtered_node_type_list: filtered_node_type_list[0], node_type_lists))
        return node_types

    def query_all_edge_types(self):
        """Queries all edge types from the database
                Returns
                -------
                edge_types: list[tuple]
                    Returns all edge types the database
                """
        records, _, _ = self.driver.execute_query(
            """
                MATCH (source)-[r]->(target)
                WITH DISTINCT labels(source) AS source_type, type(r) AS edge_type, labels(target) AS target_type
                RETURN source_type,edge_type, target_type
            """,
            database_=self.database,
        )
        edge_types = list(map(lambda record: (record.data()["source_type"][0], record.data()["edge_type"],
                                              record.data()["target_type"][0]), records))
        return edge_types

    def query_node_ids_per_type(self, node_type):
        """Queries all node ids for a specific node type from the database
            Parameters
            ----------
            node_type : str
                The node type for which we want to query the node ids
            Returns
            -------
            node_ids: list[int]
                Returns all node ids in the database
        """
        records, _, _ = self.driver.execute_query(
            f"""
                MATCH (n:{node_type})
                WITH id(n) AS node_id
                RETURN node_id
            """,
            database_=self.database,
        )
        node_ids = list(map(lambda record: record.data()["node_id"], records))
        return node_ids

    def query_node_features_per_type(self, node_type):
        """Queries all node ids for a specific node type from the database
            Parameters
            ----------
            node_type : str
                The node type for which we want to query the node features
            Returns
            -------
            node_features: list[any]
                Returns all node features in the database
        """
        records, _, _ = self.driver.execute_query(
            f"""
                MATCH (n:{node_type})
                WITH properties(n) AS node_features
                RETURN node_features
            """,
            database_=self.database,
        )
        node_features = list(map(lambda record: record.data()["node_features"], records))
        return node_features

    def get_edge_index_per_type(self, edge_type):
        """Queries all node ids for a specific node type from the database
            Parameters
            ----------
            edge_type : tuple(str, str, str)
                The edge type for which we want to query the edge index, provided as a tuple of
                source_node_type, edge_label, and target_node_type
            Returns
            -------
            edge_index: [list, list]
                Returns the edge index from the database in the form of a list with length 2 that contains all source
                node ids at the first position and the target node ids inn the second position
        """
        source, edge, target = edge_type
        records, _, _ = self.driver.execute_query(
            f"""
                MATCH(source:{source})-[r:{edge}]->(target:{target})
                WITH COLLECT(distinct[id(startNode(r)), id(endNode(r))]) as edge_index
                UNWIND edge_index AS edge
                WITH COLLECT(edge[0]) as source, COLLECT(edge[1]) as target
                RETURN [source, target] as edge_index
            """,
            database_=self.database,
        )
        edge_index = list(map(lambda record: record.data()["edge_index"], records))[0]
        return edge_index
