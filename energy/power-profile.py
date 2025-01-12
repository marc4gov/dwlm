import requests
from datetime import datetime, timedelta
import pydgraph
import csv
import pandas as pd

client_stub = pydgraph.DgraphClientStub.from_cloud("https://nameless-brook-630049.grpc.eu-central-1.aws.cloud.dgraph.io:443/graphql", "YzIzNDA0NGIwZDkyMzdlOWNhYzU1ZGUxYzZhMGY2ZTc=")
client = pydgraph.DgraphClient(client_stub)

import json

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

type HourRate {
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

type FlowProfile {
    datestring
    flow_per_hour
}
"""

def setup_schema(client):
    operation = pydgraph.Operation(schema=schema)
    client.alter(operation)

# Schema alteration uitvoeren
def setup_schema(client):
    operation = pydgraph.Operation(schema=schema)
    client.alter(operation)


def add_power_profile(client, datestring, hourly_rates):
    # Create a transaction
    txn = client.txn()
    try:
        # Convert hourly rates list to proper format
        hours_dict = {}
        for rate in hourly_rates:
            hour_key = f"h{rate['uur']}"  # Convert hour to h0, h1, h2 format
            hours_dict[hour_key] = rate['waarde']
        
        # Construct the data
        power_profile = {
            "dgraph.type": "`FlowProfile",  # Fixed typo in type name
            "datestring": datestring,
            "flow_per_hour": {
                "dgraph.type": "HourRate",
                **hours_dict  # This unpacks all hour values in h0, h1, h2 format
            }
        }
        
        response = txn.mutate(set_obj=power_profile)
        txn.commit()
        return response
    finally:
        txn.discard()

# Main processing
df = pd.read_csv("debiet_gouda_stripped.csv")
setup_schema(client)

current_date_rates = []
current_date = None

for index in df.index:
    row = df.loc[index]
    row_date = str(row['datum'])
    
    if current_date and row_date != current_date:
        # Send the completed day's data
        result = add_power_profile(client, current_date, current_date_rates)
        print(f"Added profile for {current_date}: {result}")
        current_date_rates = []  # Reset for new date
    
    # Store the current row's data
    current_date = row_date
    current_date_rates.append({
        'uur': int(row['uur']),
        'waarde': float(round(row['gemiddelde'], 3))
    })

# Don't forget to process the last day
if current_date_rates:
    result = add_power_profile(client, current_date, current_date_rates)
    print(f"Added profile for {current_date}: {result}")