        # self.stub = pydgraph.DgraphClientStub.from_cloud("https://nameless-brook-630049.grpc.eu-central-1.aws.cloud.dgraph.io:443/graphql", "YzIzNDA0NGIwZDkyMzdlOWNhYzU1ZGUxYzZhMGY2ZTc=")
        # self.client = pydgraph.DgraphClient(self.stub)
 
import json
import pydgraph
import datetime
import unittest
from typing import List

class PumpingStation:
    def __init__(self, xid, name, profiles):
        self.xid = xid
        self.name = name
        self.profiles = profiles

class Profile:
    def __init__(self, xid, datestring, flow_per_hour, price_per_hour, action_per_hour):
        self.xid = xid
        self.datestring = datestring
        self.flow_per_hour = flow_per_hour
        self.price_per_hour = price_per_hour
        self.action_per_hour = action_per_hour

class HourRate:
    def __init__(self, xid, hours):
        self.xid = xid
        self.hours = hours

class PumpingStationMutations:
    def setUp(self):
        # Create a client stub
        self.stub = pydgraph.DgraphClientStub.from_cloud("https://nameless-brook-630049.grpc.eu-central-1.aws.cloud.dgraph.io:443/graphql", "YzIzNDA0NGIwZDkyMzdlOWNhYzU1ZGUxYzZhMGY2ZTc=")
        self.client = pydgraph.DgraphClient(self.stub)
        
        # Clean up any existing test data
        self.cleanup_test_data()
        
        # Set schema
        schema = """
h0: float .
h1: float .
h2: float .
h3: float .
h4: float .
h5: float .
h6: float .
h7: float .
h8: float .
h9: float .
h10: float .
h11: float .
h12: float .
h13: float .
h14: float .
h15: float .
h16: float .
h17: float .
h18: float .
h19: float .
h20: float .
h21: float .
h22: float .
h23: float .

datestring: string @index(hash) .
flow_per_hour: uid . 
price_per_hour: uid . 
action_per_hour: uid . 
xid: string @index(exact) .
name: string .
profiles: [uid] .

type HourRate {
    xid
    h0
    h1
    h2
    h3
    h4
    h5
    h6
    h7
    h8
    h9
    h10
    h11
    h12
    h13
    h14
    h15
    h16
    h17
    h18
    h19
    h20
    h21
    h22
    h23
}


type Profile {
    datestring
    flow_per_hour
    price_per_hour
    action_per_hour
}

type PumpingStation {
    xid
    name
    profiles
}
"""
        self.client.alter(pydgraph.Operation(schema=schema))

    def cleanup_test_data(self):
        query = """
        {
          stations(func: type(PumpingStation)) @filter(eq(xid, "PS001") OR eq(xid, "PS002")) {
            uid
            profiles {
              uid
              flow_per_hour {
                uid
              }
              price_per_hour {
                uid
              }
              action_per_hour {
                uid
              }
            }
          }
        }
        """
        
        txn = self.client.txn()
        try:
            result = txn.query(query)
            stations = json.loads(result.json).get('stations', [])
            print("Clean station: ", stations)
            # Delete in reverse order: hour_rates -> flow_profiles -> stations
            for station in stations:
                # First delete hour rates
                for profile in station.get('profiles', []):
                    if profile.get('flow_per_hour'):
                        txn.mutate(del_obj={
                            'uid': profile['flow_per_hour']['uid'],
                            'dgraph.type': None
                        })
                    if profile.get('price_per_hour'):
                        txn.mutate(del_obj={
                            'uid': profile['price_per_hour']['uid'],
                            'dgraph.type': None
                        })
                    if profile.get('action_per_hour'):
                        txn.mutate(del_obj={
                            'uid': profile['action_per_hour']['uid'],
                            'dgraph.type': None
                        })
                # Then delete profiles
                for profile in station.get('profiles', []):
                    txn.mutate(del_obj={
                        'uid': profile['uid'],
                        'dgraph.type': None
                    })

                # Finally delete station
                txn.mutate(del_obj={
                    'uid': station['uid'],
                    'dgraph.type': None
                })
            
            txn.commit()
        finally:
            txn.discard()

    def create_pumping_station(self, xid, name):
        # Create a new transaction
        txn = self.client.txn()
        try:
            # Create mutation
            station = {
                'xid': xid,
                'name': name,
                'dgraph.type': 'PumpingStation'
            }
            
            # Run mutation
            response = txn.mutate(set_obj=station)
            
            # Commit transaction
            txn.commit()
            
            # Return the UID of the created pumping station
            return response.uids
            
        finally:
            txn.discard()

    def set_rates(self, rates: List[float]):
        return rates
    

    def add_profile(self, station_uid, datestring, profile_dict):
        txn = self.client.txn()
        try:
            # Create HourRate object
            hour_rate = {
                'dgraph.type': 'HourRate',
                'xid': datestring,
            }
            
            # Add hourly values
            for hour in range(24):
                hour_key = f'h{hour}'
                hour_rate[hour_key] = profile_dict['flow_per_hour'][hour]
            
            # Create Profile object
            profile = {
                'dgraph.type': 'Profile',
                'datestring': datestring,
                # 'flow_per_hour': hour_rate,
                # 'price_per_hour': hour_rate,
                # 'action_per_hour': hour_rate
            }
            
            # Run mutation and print the results
            response = txn.mutate(set_obj=profile)
            print("Created profile with UIDs:", response.uids)
            
            # Get the profile UID
            profile_uid = list(response.uids.values())[0]
            print("Profile UID:", profile_uid)

            # Create Profile mutation to link the profiles
            profile_mutation = {
                'uid': profile_uid,
                'flow_per_hour': [hour_rate]  # As an array
            }
            response = txn.mutate(set_obj=profile_mutation)
            print("Linked profile mutation response:", response.uids)

            # Add hourly values
            for hour in range(24):
                hour_key = f'h{hour}'
                hour_rate[hour_key] = profile_dict['price_per_hour'][hour]

            # Create Profile mutation to link the profiles
            profile_mutation = {
                'uid': profile_uid,
                'price_per_hour': [hour_rate]  # As an array
            }
            response = txn.mutate(set_obj=profile_mutation)
            print("Linked profile mutation response:", response.uids)

            # Add hourly values
            for hour in range(24):
                hour_key = f'h{hour}'
                hour_rate[hour_key] = profile_dict['action_per_hour'][hour]

            # Create Profile mutation to link the profiles
            profile_mutation = {
                'uid': profile_uid,
                'action_per_hour': [hour_rate]  # As an array
            }
            response = txn.mutate(set_obj=profile_mutation)
            print("Linked profile mutation response:", response.uids)

            # Create Station mutation to link the profile
            station_mutation = {
                'uid': station_uid,
                'profiles': [{'uid': profile_uid}]  # As an array
            }

            # Link and print results
            response = txn.mutate(set_obj=station_mutation)
            print("Linked station mutation response:", response.uids)

            # Query to verify the link was created
            verify_query = f"""
            {{
                station(func: uid({station_uid})) {{
                    uid
                    xid
                    name
                    profiles {{
                        uid
                        flow_per_hour {{
                            uid
                        }}
                        price_per_hour {{
                            uid
                        }}
                        action_per_hour {{
                            uid
                        }}
                    }}
                }}
            }}
            """
            verify_result = txn.query(verify_query)
            print("Verification query result:", verify_result.json)
            
            # Commit transaction
            txn.commit()
            
            return response.uids
            
        finally:
            txn.discard()


    # def test_create_pumping_station(self):
    #     # Test creating a pumping station
    #     uids = self.create_pumping_station('PS001', 'Test Pumping Station')
    #     self.assertIsNotNone(uids)
        
    #     # Query to verify creation
    #     query = """
    #     {
    #         station(func: type(PumpingStation)) @filter(eq(xid, "PS001")) {
    #             uid
    #             xid
    #             name
    #         }
    #     }
    #     """
        
    #     result = self.client.txn().query(query)
    #     stations = json.loads(result.json)['station']
    #     self.assertEqual(len(stations), 1)
    #     self.assertEqual(stations[0]['name'], 'Test Pumping Station')

    def add_profiles_and_pumpingstation(self):
        # First create a pumping station
        station_uids = self.create_pumping_station('PS002', 'Flow Test Station')
        station_uid = list(station_uids.values())[0]
        
        # Create sample hourly flow data
        profile_dict = {
            'flow_per_hour': [float(i) for i in range(24)],
            'price_per_hour': [float(i+i) for i in range(24)],
            'action_per_hour': [float(i+i+i) for i in range(24)],
        }
        
        # Add flow profile
        datestring = datetime.datetime.now().strftime('%Y-%m-%d')
        flowprofile_uids = self.add_profile(station_uid, datestring, profile_dict)
        
        # Verify the link
        query = """
        {
            station(func: type(PumpingStation)) @filter(eq(xid, "PS002")) {
                uid
                xid
                name
                profiles {
                    uid
                    datestring
                    flow_per_hour {
                        h0
                        h1
                        h23
                    }
                    price_per_hour {
                        h0
                        h1
                        h23
                    }
                    action_per_hour {
                        h0
                        h1
                        h23
                    }
                }
            }
        }
        """
        
        txn = self.client.txn()
        result = txn.query(query)
        print("Full Query Result:", result.json)  # Detailed debug output
        
    def tearDown(self):
        self.stub.close()

if __name__ == '__main__':
    ps = PumpingStationMutations()
    ps.setUp()
    ps.add_profiles_and_pumpingstation()
    ps.tearDown