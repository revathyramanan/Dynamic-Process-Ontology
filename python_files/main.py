import os
import pandas as pd
import time
from dotenv import load_dotenv
from classes import Ontology, Neo4jConnection

load_dotenv()
URI = 'bolt://localhost:7687'
USER = os.getenv("NEO4J_USER_NAME")
PASSWORD = os.getenv("NEO4J_PASSWD")
AUTH = (os.getenv("NEO4J_USER_NAME"), os.getenv("NEO4J_PASSWD"))



def test_ontology_insertion(conn):
    # Let's check if the data is inserted
    # number of nodes (should be 85-90)
    res=conn.query('MATCH (n) RETURN count(n)')
    print("Number of nodes:",res)

    # number of relationships
    res=conn.query('MATCH (n)-[r]-(m) RETURN count(r)')
    print("Number of Relationships:",res)

    # number of robots (should be 4)
    res=conn.query('MATCH (n:Robot) RETURN count(n)')
    print("Number of Robots",res)

    
def main():
    conn = Neo4jConnection(uri=URI, 
                       user=USER,
                       pwd=PASSWORD)
    filepath = "ontology.txt"
    ont = Ontology()
    res = ont.create(filepath, conn)
    test_ontology_insertion(conn)

def test():
    conn = Neo4jConnection(uri=URI, 
                    user=USER,
                    pwd=PASSWORD)
    query_str = """
        MATCH (node:Label)
        WHERE node.name CONTAINS $partial_string
        RETURN node
    """
    parameters = {
        'partial_string':'R02_BJointAngle'
    }
    res = conn.query(query_str, parameters)
    print(res)
    for ele in res:
        # print(ele['labels'])
        pass


test()

# main()