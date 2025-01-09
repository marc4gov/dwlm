import requests
from datetime import datetime, timedelta
import pydgraph
import csv

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
price_per_hour: uid .

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

type PriceProfile {
    datestring
    price_per_hour
}
"""

def setup_schema(client):
    operation = pydgraph.Operation(schema=schema)
    client.alter(operation)

# Schema alteration uitvoeren
def setup_schema(client):
    operation = pydgraph.Operation(schema=schema)
    client.alter(operation)

def add_price_profile(client, datestring, hourly_prices):
    # Create a transaction
    txn = client.txn()
    
    try:
        # Construct the data
        price_profile = {
            "dgraph.type": "PriceProfile",
            "datestring": datestring,
            "price_per_hour": {
                "dgraph.type": "HourRate",
                **hourly_prices  # This unpacks all hour prices
            }
        }
        
        # Convert to JSON and create mutation
        # mutation = json.dumps(price_profile).encode('utf-8')
        response = txn.mutate(set_obj=price_profile)
        
        # Commit transaction
        txn.commit()
        
        return response
    finally:
        # Clean up by discarding transaction
        txn.discard()


def get_frank_prices(datestring):
    url = 'https://graphql.frankenergie.nl/'
    
    query = f"""
    query MarketPrices {{
        marketPrices(date: "{datestring}") {{
            electricityPrices {{
                from
                till
                marketPrice
                perUnit
            }}
        }}
    }}
    """
    
    response = requests.post(url, json={
        'query': query,
        # 'variables': variables
    })
    
    return response.json()

# Voorbeeld gebruik
start_date = datetime(2025, 1, 7)
datestring = start_date.strftime("%Y-%m-%d")

prices = get_frank_prices(datestring)
hourly = prices['data']['marketPrices']['electricityPrices']
js = []
js2 = {}
i = 0
for hour in hourly:
    p = round(hour['marketPrice'] * 1000, 3)
    js2['datum'] = datestring
    js2['uur'] = i
    js2['waarde'] = p
    js.append(js2)
    js2 = {}
    i += 1
print(js)

# Gebruik de sleutels van het eerste item als kolomnamen
keys = ['datum', 'uur', 'waarde']
filename = 'price_profile_'+ datestring +'.csv'
with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
    dict_writer = csv.DictWriter(csvfile, fieldnames=keys)
    dict_writer.writeheader()
    dict_writer.writerows(js)

print('Opgeslagen in ' + filename)


# setup_schema(client)
# result = add_price_profile(client, datestring, js)
# print(result)