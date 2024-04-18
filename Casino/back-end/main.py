import requests
import random
import time

def send_random_number():
    url = 'http://localhost:5555/get-number-py'
    number = random.randint(1, 10)
    payload = {'number': number}
    try:
        response = requests.post(url, params=payload)
        if response.status_code == 200:
            print(f"Number {number} sent successfully.")
        else:
            print(f"Failed to send number {number}. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending number: {e}")

if __name__ == "__main__":
    while True:
        send_random_number()
        time.sleep(5)
