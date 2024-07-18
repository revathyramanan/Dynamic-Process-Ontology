import os
import pandas as pd
import csv
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
    df = df.drop(labels=['Description', '_time'], axis=1) #0-rows, 1-columns
    headers = df.columns.tolist()
    for i in range(0,len(df)):
        data_dict = {}
        sensor_dict = {}
        for header in headers:
            if header == 'CycleState':
                data_dict['cycle_state'] = df[header][i]
            else: 
                sensor_dict[str(header)] = df[header][i]
        data_dict['sensor_variables'] = sensor_dict
        data_list.append(data_dict)

    return data_list


def get_cycle_function_data(filepath) -> list[dict]:
    data_list = []
    df = pd.read_csv(filepath)

    for i in range(0,len(df)):
        row_dict = {'cycle_state': df['Cycle State'][i],
                    'robot_names': df['Robot Names'][i],
                    'function': df['Function'][i]
        }
        data_list.append(row_dict)
    return data_list


    
def load_ontology():
    # Instantiate Neo4j connection
    neo4j_obj = Neo4jConnection(uri=URI, 
                       user=USER,
                       pwd=PASSWORD)
    # Specify the filepaths
    ontology_filepath = "../mfg-data/process_ontology.txt" # filepath that consists of ontology creation query
    min_max_filepath = '../mfg-data/cycle_state_values.csv' # filepath that consists of min and max values of sensors as per cycle state
    cycle_function_path = '../mfg-data/cycle_state_function.csv'
    # create an object for ontology class
    ont = Ontology()
    
    # First clear the database, then run the tests, load the ontology
    res = neo4j_obj.query("MATCH (n) DETACH DELETE (n)")

    # Inject ontology to Neo4j when empty
    nodes = neo4j_obj.query("MATCH (n) RETURN n")
    if len(nodes) == 0:
        # TODO - create constraint
        res = ont.create(neo4j_obj, ontology_filepath)
        print("Result of Ontology Creation:", res)

        # get the data in required format to update ontology
        min_max_data = get_min_max_data(filepath=min_max_filepath)
        # call the update function for min max
        res = ont.update_min_max(neo4j_obj, min_max_data)
        print("Min Max value Update:", res)
        
        # get the cycle functions and load it into the ontology
        cycle_function_data = get_cycle_function_data(filepath=cycle_function_path)
        # call the required function
        res = ont.add_cycle_functions(neo4j_obj, cycle_function_data)
        print("Adding Cycle Functions:", res)

        # Add anomaly types
        anomaly_df = pd.read_csv('../mfg-data/anomaly_type.csv')
        res = ont.add_anomaly_types(neo4j_obj, anomaly_df)
        print(res)
    else:
        pass

# load_ontology()




# ---------------------------------------------------------------------
# CHATHURANGI"S IMAGE USE CASE
# Instantiate Neo4j connection
neo4j_obj = Neo4jConnection(uri=URI, 
                    user=USER,
                    pwd=PASSWORD)
# create an object for ontology class
ont = Ontology()

# open file
df = pd.read_csv('../mfg-data/Chathurangi/final_df_image_detection.csv')
nobody1 = 0
nobody2 = 0
nonose = 0
for i in range(0,len(df)):
    cycle_state = df['cycle_state'][i]
    predicted = df['predicted_label'][i]
    predicted = predicted.split(",")
    if "NoBody1" in predicted:
        nobody1 += 1
    if "NoBody2" in predicted:
        nobody2 += 1
    if "NoNose" in predicted:
        nonose += 1
    
print(nobody1, nobody2, nonose)

    
    # query_str = """
    # MATCH (n:Cycle {cycle_state:$state}) RETURN n.anomaly_types
    # """
    # parameters = {'state': cycle_state}
    # res = neo4j_obj.query(query_str, parameters)
    # data_dict = dict(res[0].items())
    # print(type(data_dict['n.anomaly_types']))
    # exit(0)
    
# ---------------------------------------------------------------------


# ----------------------------------------------------------------------
# get the min and max values of sensors for each cycle state - CHATHURANGI
# Instantiate Neo4j connection
neo4j_obj = Neo4jConnection(uri=URI, 
                    user=USER,
                    pwd=PASSWORD)
# create an object for ontology class
ont = Ontology()
cycle_state = 1
sensor_variable = "I_R03_Gripper_Load"
values_dict = ont.get_min_max(neo4j_obj, cycle_state, sensor_variable)
print(values_dict)
# ---------------------------------------------------------------------



############## ONTOLOGY USAGE: Fadi's use case ##########
"""
The following code will generate reasoning. Now that the ontology is created, you can use 
it for explanations
"""

# # get the data for anomalous cycle
# # NOTE: Input file must contain only the cycle state and sensor values
# anomalous_data_filepath = '../mfg-data/anomaly_data/fadi2.csv'
# anomalous_data = get_formatted_data(anomalous_data_filepath)


# # get the explanation for anomaly
# # Instantiate Reasoner class
# reasoner = AnomalyReasoner()
# exp_dict = reasoner.get_explanation(neo4j_obj, anomalous_data)

# # store the values in a csv file
# df = pd.DataFrame.from_dict(exp_dict)
# output_filepath = '../mfg-data/results/fadi2_resoning.csv'
# df.to_csv(output_filepath, index=False)










