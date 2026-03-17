"""
This script provides a simple command-line interface (CLI) to interact with the 
Flask server's /operator endpoint.

It supports:
1. Manually adding an operator via terminal prompts.
2. Testing the PUT (update) functionality for an operator.
3. Batch-adding a predefined list of operators for testing or seeding.
"""

import requests

# Section 1: Manual Operator Registration
# Prompts the user to input details for a single operator.
address = input('Please enter the pop server address:')
first_name = input('Please enter the first name of the person:')
last_name = input('Please enter the last name of the person:')
lam_1_cert = 'y' in input('Are they Lam 1 certified? (y/n):').lower()
lam_2_cert = 'y' in input('Are they Lam 2 certified? (y/n):').lower()

data = {
    'first_name': first_name,
    'last_name': last_name,
    'lam_1_certified': lam_1_cert,
    'lam_2_certified': lam_2_cert,
}

# Send POST request to create the operator.
response = requests.post(f'http://{address}:5000/operator', json=data)

# Section 2: PUT Request Test
# Example of updating an existing operator (e.g., ID 42).
# response = requests.put(f'http://{address}:5000/operator', json=data|{'id': 42, 'lam_2_certified': True})

# Section 3: Batch Seeding
# Automatically registers a predefined list of names as certified operators.
from pprint import pp

news = '''Andres Luna
Jahlill Demery
Myriam Claudio
Kasha Shakoor'''.splitlines()

for line in news:
    fname, lname = line.split(chr(32))
    print(fname, lname)
    data = {
        'first_name': fname,
        'last_name': lname,
        'lam_1_certified': True,
        'lam_2_certified': True,
    }
    pp(data)
    # Send POST request for each operator in the list.
    response = requests.post(f'http://{address}:5000/operator', json=data)
pass  # for ide debug
