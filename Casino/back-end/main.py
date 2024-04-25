import requests
import random
import time

PortJS = 5555
IPTable = '192.168.4.4'
IPMainServer = '127.0.0.1'
urlJS = f'http://{IPMainServer}:{PortJS}'
urlTable = f'http://{IPTable}'
pots = {"1": 300, "2": 400, "3": 500}

def send_pots_app():

    url = urlJS + "/get-pots-py"

    payload = {'pots': pots}

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(f"Pots {pots} sent successfully.")
        else:
            print(f"Failed to send pots {pots}. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending pots: {e}") 

if __name__ == "__main__":
    while True:
        send_pots_app()
        time.sleep(5)
