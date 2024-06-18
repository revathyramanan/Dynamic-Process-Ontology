
import os
from dotenv import load_dotenv
from classes.neo4j_connection import Neo4jConnection
import networkx as nx
import matplotlib.pyplot as plt

load_dotenv()
URI = 'bolt://localhost:7687'
USER = os.getenv("NEO4J_USER_NAME")
PASSWORD = os.getenv("NEO4J_PASSWD")
AUTH = (os.getenv("NEO4J_USER_NAME"), os.getenv("NEO4J_PASSWD"))



def extract_neo4j_data(tx):
    # Query to get all nodes and relationships
    query = """
    MATCH (n)-[r]->(m)
    RETURN n, r, m
    """
    result = tx.run(query)
    
    nodes = {}
    edges = []
    
    for record in result:
        node1 = record['n']
        node2 = record['m']
        rel = record['r']
        
        # Add nodes with properties
        if node1.id not in nodes:
            nodes[node1.id] = dict(node1.items())
        if node2.id not in nodes:
            nodes[node2.id] = dict(node2.items())
        
        # Add edge with properties
        edges.append((node1.id, node2.id, dict(rel.items())))
    
    return nodes, edges

def neo4j_to_networkx():
    with driver.session() as session:
        nodes, edges = session.read_transaction(extract_neo4j_data)
        
        # Create a NetworkX graph
        G = nx.DiGraph()  # Use DiGraph() for directed graph, Graph() for undirected
        
        # Add nodes with properties
        for node_id, node_attrs in nodes.items():
            G.add_node(node_id, **node_attrs)
        
        # Add edges with properties
        for source, target, edge_attrs in edges:
            G.add_edge(source, target, **edge_attrs)
        
        return G

def visualize_graph(G):
    plt.figure(figsize=(12, 12))
    
    # Generate layout for the graph
    pos = nx.spring_layout(G, seed=42)  # For consistent layout
    
    # Draw nodes with their properties
    nx.draw_networkx_nodes(G, pos, node_size=700, node_color='skyblue')
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, edgelist=G.edges(), arrowstyle='->', arrowsize=20)
    
    # Draw labels
    labels = {node: f"{data['name']}" for node, data in G.nodes(data=True)}
    nx.draw_networkx_labels(G, pos, labels, font_size=12)
    
    # Draw edge labels if needed (e.g., relationship types)
    edge_labels = {(u, v): f"{d.get('type', '')}" for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
    
    plt.title("NetworkX Graph from Neo4j")
    plt.show()

if __name__ == "__main__":
    # Instantiate Neo4j connection
    neo4j_obj = Neo4jConnection(uri=URI, 
                       user=USER,
                       pwd=PASSWORD)
    G = neo4j_to_networkx()
    
    # Output for verification
    print("Nodes:", G.nodes(data=True))
    print("Edges:", G.edges(data=True))
    
    # Visualize the graph
    visualize_graph(G)
    
    # Optionally save the graph
    nx.write_gpickle(G, "neo4j_graph.gpickle")
    