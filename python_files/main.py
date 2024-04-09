import os
import pandas as pd
import time
from dotenv import load_dotenv
from classes.neo4j_connection import Neo4jConnection
from classes.ontology import Ontology
from classes.reasoner import AnomalyReasoner

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



def get_min_max_data(filepath):
    """
    conn: Neo4j object
    filepath: csv file path that consists of expected min and max values of each sensor per cycle state
    (sample file can be found at mfg-data/cycle_state_values.csv)

    Expected data format that needs to be sent:
    [
    {'cycle_state':1,
    '<sensor_variable_name>: {'min':<value>, 'max':<value>},
    '<sensor_varaibale_name>: {'min':<value>, 'max':<value},
    ...
    }, ...
    ]
    """
    df = pd.read_csv(filepath)
    headers = df.columns.tolist()
    data_list = []
    for i in range(0,len(df)):
        each_row = {}
        for header in headers:
            if header == 'cycle_state':
                each_row[str(header)] = int(df[header][i])
            else:
                cell_value = str(df[header][i])
                if "-" in cell_value:
                    min = cell_value.split("-")[0]
                    max = cell_value.split("-")[1]
                else:
                    min = "NA"
                    max = "NA"
                each_row[str(header)] = {'min': min, 'max':max}
        data_list.append(each_row)
    
    return data_list



def get_formatted_data(filepath):
    """
    Return the data in the following format
    [ {'cycle_state': <value>, 
    'sensor_variables':{'I_R01_Gripper_Load':<value>, 
                        'I_R02_Gripper_Load':<value>, 
                        'I_R04_Gripper_Load':<value>,...}
    }, {'cycle_state':<value>, "",..}..]
    # number of dict = number of rows in csv/df
    """
    data_list = []
    df = pd.read_csv(filepath)
    headers = df.columns.tolist()
    for i in range(0,len(df)):
        pass

    return data_list




    
def main():
    # Instantiate Neo4j connection
    neo4j_obj = Neo4jConnection(uri=URI, 
                       user=USER,
                       pwd=PASSWORD)
    # Specify the filepaths
    ontology_filepath = "ontology.txt" # filepath that consists of ontology creation query
    min_max_filepath = '../mfg-data/cycle_state_values.csv' # filepath that consists of min and max values of sensors as per cycle state
    
    # create an object for ontology class
    ont = Ontology()
    
    # Inject ontology to Neo4j
    # res = ont.create(neo4j_obj, ontology_filepath)
    # print("Result of Ontology Creation:", res)

    # update ontology with min and max values
    # get the data in required format
    min_max_data = get_min_max_data(filepath=min_max_filepath)
    
    # call the update function
    res = ont.update_min_max(neo4j_obj, min_max_data)
    print("Result of Ontology Update:", res)

    # get the data for anomalous cycle
    anomalous_data_filepath = ''
    anomalous_data = get_formatted_data()

    # get the explanation for anomaly
    # Instantiate Reasoner class
    reasoner = AnomalyReasoner()


main()














# def test():
#     neo4j_obj = Neo4jConnection(uri=URI, 
#                     user=USER,
#                     pwd=PASSWORD)
                    
    # query_str = """
    #     MATCH path = ((node:Sensor_Value)-[r1]-(m)-[r2]-(l)-[r3]-(t))
    #     WHERE node.item_name CONTAINS $partial_string
    #     RETURN node, path
    # """
    # parameters = {
    #     'partial_string':'I_R03_Gripper_Pot'
    # }
    # res = neo4j_obj.query(query_str, parameters)
    # # print(res)
    # for ele in res:
    #     print(ele)
    #     # print
    #     pass


# main()

# List of sensor value
# check for anomalous values
