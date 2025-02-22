import os
import json
from dotenv import load_dotenv
from classes.neo4j_connection import Neo4jConnection  # Import your Neo4j connection class
import networkx as nx
import matplotlib.pyplot as plt

# Load environment variables
load_dotenv()
URI = 'bolt://localhost:7687'
USER = os.getenv("NEO4J_USER_NAME")
PASSWORD = os.getenv("NEO4J_PASSWD")

# Instantiate the Neo4j connection
neo4j_obj = Neo4jConnection(uri=URI, user=USER, pwd=PASSWORD)

def extract_neo4j_data():
    """
    Extract nodes and relationships from Neo4j.
    Returns a dictionary of nodes and a list of edges.
    """
    query = """
    MATCH (n)-[r]->(m)
    RETURN n, r, m
    """
    result = neo4j_obj.query(query)

    nodes = {}
    edges = []

    for record in result:
        node1 = record['n']
        node2 = record['m']
        rel = record['r']

        # Add node1 (with type and name)
        if node1.id not in nodes:
            # Extract the node type (label)
            node_type = next(iter(node1.labels), 'Unknown')  # Default to 'Unknown' if no labels
            # Determine node_name based on label
            if 'Cycle' in node1.labels:
                node_name = f"Cycle{node1.get('cycle_state', '')}"  # Cycle state value appended to label
            elif 'Marker' in node1.labels:
                node_name = node1.get('marker_name', 'Unknown')  # Marker name directly
            else:
                node_name = node1.get('item_name', str(node1.id))  # Default to item_name or node_id

            nodes[node1.id] = dict(node1.items())
            nodes[node1.id]['node_type'] = node_type
            nodes[node1.id]['node_name'] = node_name

        # Add node2 (with type and name)
        if node2.id not in nodes:
            # Extract the node type (label)
            node_type = next(iter(node2.labels), 'Unknown')  # Default to 'Unknown' if no labels
            # Determine node_name based on label
            if 'Cycle' in node2.labels:
                node_name = f"Cycle{node2.get('cycle_state', '')}"  # Cycle state value appended to label
            elif 'Marker' in node2.labels:
                node_name = node2.get('marker_name', 'Unknown')  # Marker name directly
            else:
                node_name = node2.get('item_name', str(node2.id))  # Default to item_name or node_id

            nodes[node2.id] = dict(node2.items())
            nodes[node2.id]['node_type'] = node_type
            nodes[node2.id]['node_name'] = node_name

        # Add edge with properties
        edges.append({
            "source": node1.id,
            "target": node2.id,
            "attributes": dict(rel.items())
        })

    return nodes, edges

def neo4j_to_networkx():
    """
    Converts Neo4j data to a NetworkX graph.
    """
    nodes, edges = extract_neo4j_data()

    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes with properties
    for node_id, node_attrs in nodes.items():
        G.add_node(node_id, **node_attrs)

    # Add edges with properties
    for edge in edges:
        G.add_edge(edge["source"], edge["target"], **edge["attributes"])

    return G

def save_networkx_json(G, filename="networkx_graph.json"):
    """
    Saves the NetworkX graph in JSON format, including node type and node name.
    """
    graph_data = {
        "nodes": [
            {"id": node, "attributes": data} for node, data in G.nodes(data=True)
        ],
        "edges": [
            {"source": u, "target": v, "attributes": data} for u, v, data in G.edges(data=True)
        ]
    }

    with open(filename, "w") as f:
        json.dump(graph_data, f, indent=4)

    print(f"NetworkX graph saved as {filename}")

def load_networkx_json(filename="networkx_graph.json"):
    """
    Loads a NetworkX graph from a JSON file.
    """
    with open(filename, "r") as f:
        graph_data = json.load(f)

    G = nx.DiGraph()

    # Add nodes
    for node in graph_data["nodes"]:
        G.add_node(node["id"], **node["attributes"])

    # Add edges
    for edge in graph_data["edges"]:
        G.add_edge(edge["source"], edge["target"], **edge["attributes"])

    return G

def visualize_graph(G):
    """
    Visualizes the NetworkX graph.
    """
    plt.figure(figsize=(12, 12))

    # Generate layout for the graph
    pos = nx.spring_layout(G, seed=42)  # For consistent layout

    # Draw nodes with their properties
    nx.draw_networkx_nodes(G, pos, node_size=700, node_color='skyblue')

    # Draw edges
    nx.draw_networkx_edges(G, pos, edgelist=G.edges(), arrowstyle='->', arrowsize=20)

    # Draw labels
    labels = {node: f"{data.get('node_name', node)}" for node, data in G.nodes(data=True)}
    nx.draw_networkx_labels(G, pos, labels, font_size=12)

    plt.title("NetworkX Graph from Neo4j")
    plt.show()

if __name__ == "__main__":
    # Convert Neo4j graph to NetworkX
    G = neo4j_to_networkx()

    # Output for verification
    print("Nodes:", G.nodes(data=True))
    print("Edges:", G.edges(data=True))

    # Save the graph as NetworkX JSON
    save_networkx_json(G)

    # Visualize the graph
    visualize_graph(G)

    # Close the Neo4j connection
    neo4j_obj.close()

    # Example of how to load the saved graph later
    G_loaded = load_networkx_json()
    print("Loaded Graph Nodes:", G_loaded.nodes(data=True))
    print("Loaded Graph Edges:", G_loaded.edges(data=True))
