from neo4j import GraphDatabase
import networkx as nx
import community as community_louvain

driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "neo4j123"))

def build_graph():
    G = nx.Graph()

    with driver.session() as session:
        result = session.run("""
            MATCH (a)-[r]->(b)
            RETURN a.name AS source, b.name AS target
        """)

        for record in result:
            G.add_edge(record["source"], record["target"])

    return G

def detect_communities():
    G = build_graph()
    partition = community_louvain.best_partition(G)

    with driver.session() as session:
        for node, community_id in partition.items():
            session.run("""
                MATCH (n {name: $name})
                SET n.community = $community
            """, name=node, community=community_id)

    print("Communities assigned!")

detect_communities()