




# class to inject the ontology to neo4j
class Ontology:
    def __init__(self):
        pass

    def create_constraint(self, neo4j_obj):
        constraint_query = """
        CREATE CONSTRAINT cycle_id FOR (cycle:Cycle) REQUIRE cycle.cycle_state IS UNIQUE;
        CREATE CONSTRAINT marker_name FOR (marker:Marker) REQUIRE marker.marker_name IS UNIQUE;
        CREATE CONSTRAINT sensor_name FOR (sensor:Sensor) REQUIRE sensor.item_name IS UNIQUE;
        CREATE CONSTRAINT sensor_val_name FOR (sensor_val:Sensor_Value) REQUIRE sensor_val.item_name IS UNIQUE;
        CREATE CONSTRAINT robot_name FOR (robot:Robot) REQUIRE robot.item_name IS UNIQUE;
        CALL db.awaitIndexes();
        """
        res = neo4j_obj.query(constraint_query)
        print("Constraint Added")

    def create(self, neo4j_obj, filepath):
        # res = neo4j_obj.query("SHOW CONSTRAINT")
        # if len(res) == 0:
        #     self.create_constraint(neo4j_obj) # NOTE: this constraint needs to be modified if the names are modified in process_ontology.txt
        # else:
        #     pass
        f = open(filepath, "r")
        insert_query = f.read()
        res = neo4j_obj.query(insert_query)
        return "Successful"

    def serialize(self, response):
        sensor_variables = []
        for r in response:
            record_dict = dict(r.items())
            sensor_variables.append(record_dict['sv.item_name'])
        return list(set(sensor_variables))
    
    # TODO - add a check before returning "successful"
    def update_min_max(self, neo4j_obj, data):
        """
        data: list of dict that consits of expected min and max values of each sensor for each cycle state

        Expected data format:
        [
        {'cycle_state':1,
        '<sensor_variable_name>: {'min':<value>, 'max':<value>},
        '<sensor_varaibale_name>: {'min':<value>, 'max':<value},
        ...
        }, ...
        ]
        """
        print("Updating min and max values for given sensor variables..")
        for item in data:
            state = item['cycle_state']
            query_string = """
            MATCH (c:Cycle {cycle_state:$state})-[]-(r:Robot)-[]-(g:Gripper)-[]-(s:Sensor)-[]-(sv:Sensor_Value) RETURN sv.item_name
            """
            parameters = {"state": state}
            response = neo4j_obj.query(query_string, parameters)

            # serialize neo4j response to get sensor variables associated with each state
            sensor_variables = self.serialize(response)

            for sensor_var in sensor_variables:
                query_string = """
                MATCH (c:Cycle {cycle_state:$state})-[]-(r:Robot)-[]-(g:Gripper)-[]-(s:Sensor)-[]-(sv:Sensor_Value {item_name:$sensor_var})
                SET sv.cycle_state_min = $min , sv.cycle_state_max = $max
                RETURN sv
                """
                parameters = {
                    'state': state,
                    'sensor_var':sensor_var,
                    'min': item[sensor_var]['min'],
                    'max': item[sensor_var]['max']
                }
                response = neo4j_obj.query(query_string, parameters)

        return "Update Successful"
    
    # TODO - add a check before returning "successful"
    def add_cycle_functions(self, neo4j_obj, data):
        """
        data = a list of dict specifying cycle state, function and robots involved for each state

        data = 
        [{'cycle_state': 1, 'robot_names': 'Robot-1', 'function': 'Robot-1 Picks Tray from MHS'}, 
        {'cycle_state': 2, 'robot_names': 'Robot-1', 'function': 'Robot-1 Places Tray on Conveyor'}, 
        {'cycle_state': 3, 'robot_names': 'Robot-1', 'function': 'Robot-1 Goes Back to Home Position and Conveyors On'}, 
        . . . 
        ]
        """

        for item in data:
            query_str = """ MATCH (n:Cycle {cycle_state:$state})
                        SET n.cycle_function = $function
                        """
            parameters = {'state': item['cycle_state'],
                          'function': item['function']}
            response = neo4j_obj.query(query_str, parameters)


        return "Cycle state functions Added"
    

    def add_anomaly_types(self, neo4j_obj, data_df):
        """
        NoBody1 : Cycle State 4 to 21
        NoBody2 : Cycle State 6 to 21
        NoNose : Cycle State 8 to 21
        """
        for i in range(0,len(data_df)):
            cycle_state = data_df['cycle_state'][i]
            anomaly = data_df['anomaly_type'][i]
            anomalies = anomaly.split(",")
            query_str = """
            MATCH (n:Cycle {cycle_state:$state}) SET n.anomaly_types = $anomaly_list
            """
            parameters = {'state': cycle_state, 'anomaly_list':anomalies}
            response = neo4j_obj.query(query_str, parameters)
        
        return "Anomaly types added"
        
        



    ####################### FUNCTIONS TO EXPLORE OR ACCESS ONTOLOGY #############

    def get_min_max(self, neo4j_obj, cycle_state, sensor_variable):

        query_string = """
        MATCH (c:Cycle {cycle_state:$state})-[]-(r:Robot)-[]-(g:Gripper)-[]-(s:Sensor)-[]-(sv:Sensor_Value {item_name:$sensor_variable}) RETURN sv.cycle_state_max, sv.cycle_state_min
        """
        parameters = {
            'state': cycle_state,
            'sensor_variable': sensor_variable
        }

        res = neo4j_obj.query(query_string, parameters)
        if res == []: # if a variable is not present in a given cycle state, return none
            return {'min': None, 'max': None}
        else:
            record_dict = dict(res[0].items())
            return {'min':record_dict['sv.cycle_state_min'], 'max':record_dict['sv.cycle_state_max']}