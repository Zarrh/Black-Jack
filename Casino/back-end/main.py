import requests
import random
import time

PortJS = 5555
IPTable = '192.168.4.10'
urlJS = f'http://127.0.0.1:{PortJS}/'
urlTable = f'http://{IPTable}'
pots = {"1": 500, "2": 500, "3": 500}

def send_pots_app():

    link = urlJS + "/get-pots" 

    payload = {'pots': pots}
    try:
        response = requests.post(link, params=payload)
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
