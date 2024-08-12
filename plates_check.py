import requests
import os
import json
import time

# Define the URL and headers for the POST request
url = 'https://account.ezyreg.sa.gov.au/r/veh/an/checkRegistration'
headers = {
    'Content-Type': 'application/json',
}

# Create the directory to store the response files if it doesn't exist
os.makedirs('plates', exist_ok=True)

# Function to generate plate numbers from ABR000 to ABR999
def generate_plate_numbers():
    # Load the current prefix from the file
    with open('current_prefix.txt', 'r') as file:
        prefix = file.read().strip()
    for number_part in range(0, 1000):  # From '000' to '999'
        yield f'{prefix}{number_part:03d}'

# Function to send POST request with retry logic
def send_request_with_retry(plate_number, retries=3):
    payload = {"plateNumber": plate_number, "registrationType": "VEHICLE"}
    attempt = 0
    while attempt < retries:
        try:
            response = requests.post(url, json=payload, headers=headers, verify=False)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 400:
                print(f'HTTP 400 error encountered for {plate_number}, giving up.')
                return None  # Stop retrying and give up
            else:
                print(f'Received status code {response.status_code} for {plate_number}')
        except requests.exceptions.RequestException as e:
            print(f'Attempt {attempt + 1} failed for {plate_number}: {e}')
        attempt += 1
        if attempt < retries:
            time.sleep(5)  # Wait before retrying
    return None  # Return None if all retries fail

# Function to check registration for each plate number and save the response
def check_registration():
    for plate_number in generate_plate_numbers():
        response_json = send_request_with_retry(plate_number)
        if response_json:
            # Save the response only if the status code was 200
            with open(f'plates/{plate_number}.json', 'w') as f:
                json.dump(response_json, f, indent=4)
            print(f'Saved response for {plate_number}')
        else:
            print(f'Failed to retrieve or save data for {plate_number} after multiple attempts.')
        time.sleep(5)  # Add a delay between requests to avoid overwhelming the server

if __name__ == '__main__':
    check_registration()
