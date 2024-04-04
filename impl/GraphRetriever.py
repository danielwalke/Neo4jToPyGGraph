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
                    Graph object the final graph object in pytorch geometric format

        """
        print("Start loading the graph")
        self.node_types = ['Disease', 'Tissue', 'Biological_process', 'Molecular_function', 'Cellular_component', 'Modification',
         'Phenotype', 'Experiment', 'Experimental_factor', 'Units', 'Chromosome', 'Gene', 'Transcript', 'Protein',
         'Amino_acid_sequence', 'Peptide', 'User', 'Project', 'Subject', 'Biological_sample', 'Analytical_sample',
         'Modified_protein', 'Clinical_variable', 'Complex', 'Food', 'Known_variant', 'Clinically_relevant_variant',
         'Publication', 'Functional_region', 'Metabolite', 'Protein_structure', 'GWAS_study', 'Pathway', 'Drug']
        self.edge_types = [('Disease', 'HAS_PARENT', 'Disease'), ('Experimental_factor', 'MAPS_TO', 'Disease'),
         ('Modified_protein', 'ASSOCIATED_WITH', 'Disease'), ('Protein', 'ASSOCIATED_WITH', 'Disease'),
         ('Clinically_relevant_variant', 'ASSOCIATED_WITH', 'Disease'),
         ('Protein', 'IS_BIOMARKER_OF_DISEASE', 'Disease'), ('Metabolite', 'ASSOCIATED_WITH', 'Disease'),
         ('Protein', 'DETECTED_IN_PATHOLOGY_SAMPLE', 'Disease'), ('Project', 'STUDIES_DISEASE', 'Disease'),
         ('Tissue', 'HAS_PARENT', 'Tissue'), ('Protein', 'ASSOCIATED_WITH', 'Tissue'),
         ('Protein', 'IS_QCMARKER_IN_TISSUE', 'Tissue'), ('Project', 'STUDIES_TISSUE', 'Tissue'),
         ('Protein', 'ASSOCIATED_WITH', 'Biological_process'),
         ('Biological_process', 'HAS_PARENT', 'Biological_process'),
         ('Complex', 'ASSOCIATED_WITH', 'Biological_process'),
         ('Modified_protein', 'ASSOCIATED_WITH', 'Biological_process'),
         ('Protein', 'ASSOCIATED_WITH', 'Molecular_function'),
         ('Molecular_function', 'HAS_PARENT', 'Molecular_function'),
         ('Protein', 'ASSOCIATED_WITH', 'Cellular_component'),
         ('Cellular_component', 'HAS_PARENT', 'Cellular_component'), ('Modification', 'HAS_PARENT', 'Modification'),
         ('Modified_protein', 'HAS_MODIFICATION', 'Modification'), ('Phenotype', 'HAS_PARENT', 'Phenotype'),
         ('Experimental_factor', 'MAPS_TO', 'Phenotype'), ('Experiment', 'HAS_PARENT', 'Experiment'),
         ('GWAS_study', 'STUDIES_TRAIT', 'Experimental_factor'),
         ('Experimental_factor', 'HAS_PARENT', 'Experimental_factor'), ('Units', 'HAS_PARENT', 'Units'),
         ('Transcript', 'LOCATED_IN', 'Chromosome'), ('Known_variant', 'VARIANT_FOUND_IN_CHROMOSOME', 'Chromosome'),
         ('Known_variant', 'VARIANT_FOUND_IN_GENE', 'Gene'), ('Drug', 'CURATED_TARGETS', 'Gene'),
         ('Gene', 'TRANSCRIBED_INTO', 'Transcript'), ('Peptide', 'BELONGS_TO_PROTEIN', 'Protein'),
         ('Transcript', 'TRANSLATED_INTO', 'Protein'), ('Gene', 'TRANSLATED_INTO', 'Protein'),
         ('Known_variant', 'VARIANT_FOUND_IN_PROTEIN', 'Protein'), ('Protein', 'CURATED_INTERACTS_WITH', 'Protein'),
         ('Protein', 'COMPILED_INTERACTS_WITH', 'Protein'), ('Drug', 'ACTS_ON', 'Protein'),
         ('Protein', 'ACTS_ON', 'Protein'), ('Drug', 'COMPILED_TARGETS', 'Protein'),
         ('Functional_region', 'FOUND_IN_PROTEIN', 'Protein'),
         ('Analytical_sample', 'HAS_QUANTIFIED_PROTEIN', 'Protein'), ('Metabolite', 'ASSOCIATED_WITH', 'Protein'),
         ('Modified_protein', 'IS_SUBSTRATE_OF', 'Protein'),
         ('Known_variant', 'CURATED_AFFECTS_INTERACTION_WITH', 'Protein'),
         ('Protein', 'HAS_SEQUENCE', 'Amino_acid_sequence'), ('User', 'IS_RESPONSIBLE', 'Project'),
         ('User', 'PARTICIPATES_IN', 'Project'), ('Biological_sample', 'BELONGS_TO_SUBJECT', 'Subject'),
         ('Project', 'HAS_ENROLLED', 'Subject'), ('Biological_sample', 'SPLITTED_INTO', 'Analytical_sample'),
         ('Protein', 'HAS_MODIFIED_SITE', 'Modified_protein'),
         ('Analytical_sample', 'HAS_QUANTIFIED_MODIFIED_PROTEIN', 'Modified_protein'),
         ('Peptide', 'HAS_MODIFIED_SITE', 'Modified_protein'), ('Clinical_variable', 'HAS_PARENT', 'Clinical_variable'),
         ('Experimental_factor', 'MAPS_TO', 'Clinical_variable'), ('Protein', 'IS_SUBUNIT_OF', 'Complex'),
         ('Drug', 'TARGETS_CLINICALLY_RELEVANT_VARIANT', 'Clinically_relevant_variant'),
         ('Known_variant', 'VARIANT_IS_CLINICALLY_RELEVANT', 'Clinically_relevant_variant'),
         ('Drug', 'MENTIONED_IN_PUBLICATION', 'Publication'), ('Disease', 'MENTIONED_IN_PUBLICATION', 'Publication'),
         ('Cellular_component', 'MENTIONED_IN_PUBLICATION', 'Publication'),
         ('Protein', 'MENTIONED_IN_PUBLICATION', 'Publication'), ('Tissue', 'MENTIONED_IN_PUBLICATION', 'Publication'),
         ('Functional_region', 'MENTIONED_IN_PUBLICATION', 'Publication'),
         ('GWAS_study', 'PUBLISHED_IN', 'Publication'), ('Modified_protein', 'MENTIONED_IN_PUBLICATION', 'Publication'),
         ('Protein', 'HAS_STRUCTURE', 'Protein_structure'), ('Known_variant', 'VARIANT_FOUND_IN_GWAS', 'GWAS_study'),
         ('Metabolite', 'ANNOTATED_IN_PATHWAY', 'Pathway'), ('Protein', 'ANNOTATED_IN_PATHWAY', 'Pathway'),
         ('Drug', 'INTERACTS_WITH', 'Drug')]
        print("Start loading node types")
        # self.node_types = self.query_all_node_types()
        print("Loaded node types")
        print("Start loading edge types")
        # self.edge_types = self.query_all_edge_types()
        print("Loaded edge types")
        print(self.node_types)
        print(self.edge_types)
        print("Start loading node ids")
        self.set_id_dict()
        print("Loaded node ids")
        print("Start creating id_to_idx dictionary")
        self.set_id_to_idx_dict()
        print("Loaded dictionary id:node index")
        print("Start loading edges")
        self.set_edge_dict()
        print("Loaded edges")
        print("Finished")
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
                    The constructed graph object based on the neo4j database
        """
        return self.graph_object
