
from neo4j import GraphDatabase

# class to establish connection to neo4j
class Neo4jConnection:
    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
        except Exception as e:
            print("Failed to create the driver:", e)
            
    def close(self):
        if self.__driver is not None:
            self.__driver.close()
            
    def query(self, query, parameters=None, db=None):
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try: 
            session = self.__driver.session(database=db) if db is not None else self.__driver.session() 
            #response = (session.run(query, parameters))
            response = list(session.run(query, parameters))
        except Exception as e:
            print("Query failed:", e)
        finally: 
            if session is not None:
                session.close()
        
        #return pd.DataFrame([r.values() for r in response], columns=response.keys())
        return response
        
    def multi_query(self, multi_line_query, parameters=None, db=None):
        for li in multi_line_query.splitlines():
                print(li)
                result=self.query(li, parameters=None, db=None)
                print(result)



# class to inject the ontology to neo4j
class Ontology:
    def __init__(self):
        pass

    def create(self, neo4j_obj, filepath):
        f = open(filepath, "r")
        insert_query = f.read()
        res = neo4j_obj.query(insert_query)
        return res
    
    def serialize(self, response):
        sensor_variables = []
        for r in response:
            record_dict = dict(r.items())
            sensor_variables.append(record_dict['sv.item_name'])
        return list(set(sensor_variables))
    
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