import requests
import time

url = 'https://sebayt.ch/interaktiv/health'

def send_health_check():
    try:
        response = requests.get(url, timeout=5)  # Set timeout to handle unresponsive server
        if response.status_code == 200:
            # inspect the json response, should be {"status": "healthy","version": version}
            response_json = response.json()
            if response_json['status'] == 'healthy':
                print('#', end='', flush=True)  # Emit a '#' to the console without a newline
            else:
                print(f"Error: Server returned unhealthy status - {response_json}")
        else:
            print(f"Error: Received status code {response.status_code}")
    except requests.RequestException as e:
        print(f"Error: Could not connect to {url} - {e}")

def countdown():
    for i in range(10):
        print(f'.', end='', flush=True)  # Print numbers 0-9 in place
        time.sleep(1)  # Sleep for 1 second between each number

if __name__ == "__main__":
    while True:
        countdown()  # Print 0-9 in place
        send_health_check()
        time.sleep(1)  # Wait for 30 seconds before sending the next request
