


class AnomalyReasoner:
    def __init__(self):
        pass
    
    def min_max_serialize(self, response):
        record_dict = dict(response.items())
        min_value = record_dict['sv.cycle_state_min']
        max_value = record_dict['sv.cycle_state_max']
        return min_value, max_value
        

    def anomalous_item_serialize(self, response):


        return 0


    def get_explanation(self, neo4j_obj, data, anomaly_name = None):
        """
        neo4j_obj: Neo4j object
        data: data of one complete cycle of the assembly system that threw anomaly
        anomaly_name: name of the anomaly in the dataset, if present

        Expected format for data:
        [ {'cycle_state': <value>, 
          'sensor_variables':{'I_R01_Gripper_Load':<value>, 
                             'I_R02_Gripper_Load':<value>, 
                             'I_R04_Gripper_Load':<value>,...}
        }, {'cycle_state':<value>, "",..}..]
        # number of dict = number of rows in csv/df
        """

        data_list = []
        for item in data:
            cycle_state = data['cycle_state']
            # get the sensors involved in this cycle state
            for sensor_var in item['sensor_variables']:
                value = item['sensor_variables'][sensor_var]
                
                query_string = """
                MATCH (c:Cycle {cycle_state:$cycle_state})-[]-(r:Robot)-[]-(g:Gripper)-[]-(s:Sensor)-[]-(sv:Sensor_Value {item_name:$sensor_var})
                RETURN sv.cycle_state_min, sv.cycle_state_max
                """
                parameters = {'cycle_state': cycle_state,
                                'sensor_var':sensor_var}
                response = neo4j_obj.query(query_string, parameters)

                min_value, max_value = self.min_max_serialize(response)
                
                if value > min_value and value < max_value:
                    pass
                else:
                    anomalous_state = cycle_state
                    anomalous_sensor_variable = sensor_var
                    anomalous_sensor_value = value
                    path_query = """
                    MATCH (c:Cycle {cycle_state:$cycle_state})-[]-(r:Robot)-[]-(g:Gripper)-[]-(s:Sensor)-[]-(sv:Sensor_Value {item_name:$sensor_var})
                    RETURN r, g, s, sv
                    """
                    parameters = {'cycle_state': cycle_state, "sensor_var": sensor_var}
                    response = neo4j_obj.query(path_query, parameters)
                    serialized_dict = self.anomalous_item_serialize(response)
                    




                exp_dict = {'anomaly_name': '',
                            'anomalous_sensor_variables': [],
                            'sensor_variable_values':[],
                            'sensor_names':[],
                            'robot_names': [],
                            'robot_functions': [],
                            'cycle_state':[],
                            'robot_function_cycle':[]
                }

        return exp_dict
# Get the dataset. Specify expected format
# List of dict for each row in csv
#

# For each cycle state, query the ontology to check the expected values for each sensor

# Get the cycle state and sensor variable name that has anomalous value

# Return all info about the sensor. List down the questions and answer them