import requests
import json

# Test data
test_data = {
    "profiles": [0.0, 0.1, 0.2, 0.3, 0.2, 0.1, 0.0, -0.1, -0.2, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.2, 0.1, 0.0, -0.1, -0.2, -0.3, -0.2, -0.1],
    "prices": [50, 45, 40, 35, 30, 25, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 75, 70, 65, 60, 55]
}

# Make the request
response = requests.post(
    'https://marc4gov.pythonanywhere.com/predict',
    headers={'Content-Type': 'application/json'},
    json=test_data
)

# Print the response
print(f"Status Code: {response.status_code}")
print("\nResponse:")
print(json.dumps(response.json(), indent=2))