


class AnomalyReasoner:
    def __init__(self):
        pass
    
    def min_max_serialize(self, response):
        record_dict = dict(response.items())
        min_value = record_dict['sv.cycle_state_min']
        max_value = record_dict['sv.cycle_state_max']
        return min_value, max_value
        

    def anomalous_item_serialize(self, response):

        

        return {'robot_name': '',
                'robot_function': '',
                'sensor_name': '',
                'sensor_function':''

        }


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

        anomalous_sensor_variables = []
        anomalous_sensor_variable_values = []
        sensor_variable_cycle_min = []
        sensor_variable_cycle_max = []
        sensor_names = []
        sensor_functions = []
        robot_names = []
        robot_functions = []
        cycle_states = []

        # for each row in csv or each item in the data list,
        for item in data:
            # get the cycle state
            cycle_state = data['cycle_state']

            # get the sensors involved in this cycle state
            for sensor_var in item['sensor_variables']:
                value = item['sensor_variables'][sensor_var]

                # get the expected min and max value of the sensor in this state
                query_string = """
                MATCH (c:Cycle {cycle_state:$cycle_state})-[]-(r:Robot)-[]-(g:Gripper)-[]-(s:Sensor)-[]-(sv:Sensor_Value {item_name:$sensor_var})
                RETURN sv.cycle_state_min, sv.cycle_state_max
                """
                parameters = {'cycle_state': cycle_state,
                                'sensor_var':sensor_var}
                response = neo4j_obj.query(query_string, parameters)
                min_value, max_value = self.min_max_serialize(response)
                
                # check if the values is between min and max value in the sensor
                if value > min_value and value < max_value:
                    pass
                else:
                    # Anomaly occurred. Get all possible information from the sensor
                    # Sometimes, more than one sensor could have thrown anomaly. So get all sensor with anomalous value
                    cycle_states.append(cycle_state)
                    anomalous_sensor_variables.append(sensor_var)
                    anomalous_sensor_variable_values.append(value)
                    sensor_variable_cycle_max.append(max_value)
                    sensor_variable_cycle_min.append(min_value)

                    # query to get information on the sensor and the robot
                    path_query = """
                    MATCH (c:Cycle {cycle_state:$cycle_state})-[]-(r:Robot)-[]-(g:Gripper)-[]-(s:Sensor)-[]-(sv:Sensor_Value {item_name:$sensor_var})
                    RETURN r, g, s, sv
                    """
                    parameters = {'cycle_state': cycle_state, "sensor_var": sensor_var}
                    response = neo4j_obj.query(path_query, parameters)
                    serialized_dict = self.anomalous_item_serialize(response)

                    robot_names.append(serialized_dict['robot_name'])
                    robot_functions.append(serialized_dict['robot_function'])
                    sensor_names.append(serialized_dict['sensor_name'])
                    sensor_functions.append(serialized_dict['sensor_function'])


        exp_dict = {'anomaly_name': anomaly_name,
                    'anomalous_sensor_variables': anomalous_sensor_variables,
                    'anomalous_sensor_variable_values':anomalous_sensor_variable_values,
                    'sensor_variable_cycle_min': sensor_variable_cycle_min,
                    'sensor_variable_cycle_max': sensor_variable_cycle_max,
                    'sensor_names': sensor_names,
                    'sensor_functions': sensor_functions,
                    'robot_names': robot_names,
                    'robot_functions': robot_functions,
                    'cycle_state':cycle_states,
                    'robot_function_cycle':[]}

        return exp_dict

