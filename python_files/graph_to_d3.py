import os
import json
from dotenv import load_dotenv
from classes.neo4j_connection import Neo4jConnection  # Import your Neo4j connection class
import networkx as nx

# Load environment variables
load_dotenv()
URI = 'bolt://localhost:7687'
USER = os.getenv("NEO4J_USER_NAME")
PASSWORD = os.getenv("NEO4J_PASSWD")

# Instantiate the Neo4j connection
neo4j_obj = Neo4jConnection(uri=URI, user=USER, pwd=PASSWORD)

# Define colors based on node type
NODE_COLORS = {
    "Cycle": "#FF5733",
    "Gripper": "#33FF57",
    "Marker": "#3388FF",
    "Robot": "#F4D03F",
    "Sensor": "#8E44AD",
    "Sensor_Value": "#1ABC9C",
    "default": "#CCCCCC"  # Default color for unknown types
}

def extract_neo4j_data():
    """
    Extract nodes and relationships from Neo4j.
    Returns a dictionary of nodes and a list of edges.
    """
    query = """
    MATCH (n)-[r]->(m)
    RETURN n, labels(n)[0] AS type, r, m, labels(m)[0] AS target_type
    """
    result = neo4j_obj.query(query)

    nodes = {}
    edges = []

    for record in result:
        node1 = record['n']
        node2 = record['m']
        rel = record['r']

        node1_type = record['type']
        node2_type = record['target_type']

        # Get element_id instead of deprecated id
        node1_id = node1.element_id
        node2_id = node2.element_id

        # Assign color based on type
        node1_color = NODE_COLORS.get(node1_type, NODE_COLORS["default"])
        node2_color = NODE_COLORS.get(node2_type, NODE_COLORS["default"])

        # Add nodes with properties
        if node1_id not in nodes:
            nodes[node1_id] = {"id": node1_id, "type": node1_type, "color": node1_color, **dict(node1.items())}
        if node2_id not in nodes:
            nodes[node2_id] = {"id": node2_id, "type": node2_type, "color": node2_color, **dict(node2.items())}

        # Add edges
        edges.append({
            "source": node1_id,
            "target": node2_id,
            "relationship": rel.type,
            **dict(rel.items())
        })

    return nodes, edges

def save_d3_json(filename="d3_graph.json"):
    """
    Converts the Neo4j graph into a D3.js compatible format and saves it.
    """
    nodes, edges = extract_neo4j_data()

    d3_data = {
        "nodes": list(nodes.values()),  # Convert dict to list for D3.js
        "links": edges
    }

    with open(filename, "w") as f:
        json.dump(d3_data, f, indent=4)

    print(f"D3.js graph saved as {filename}")

if __name__ == "__main__":
    # Save graph as D3 JSON
    save_d3_json()

    # Close the Neo4j connection
    neo4j_obj.close()
