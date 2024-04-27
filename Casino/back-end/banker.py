import requests
import time

PortJS = 5555
resetKey = "7hAs$"
IPMainServer = '127.0.0.1'
urlJS = f'http://{IPMainServer}:{PortJS}'
players = [
    {"name": "John", "pot": 300, "bet": 0, "cards": [], "position": "1", "state": None}, 
    {"name": "Ben", "pot": 400, "bet": 0, "cards": [], "position": "2", "state": None}, 
    {"name": "Tim", "pot": 500, "bet": 0, "cards": [], "position": "3", "state": None}, 
]
dealer = {"state": None}
mode = None

def send_pots_server():

    url = urlJS + "/get-pots"

    pots = {}

    for i in range(3):
        pots[str(i+1)] = players[i]["pot"]

    payload = {'pots': pots}

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(f"Pots {pots} sent successfully.")
            return 1
        else:
            print(f"Failed to send pots {pots}. Status code: {response.status_code}")
            return 0
    except requests.exceptions.RequestException as e:
        print(f"Error sending pots: {e}") 
        return 0

def get_players_server():

    global players, dealer

    url = urlJS + "/send-players"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Players received successfully.")
            dealer = response.json()['dealer']
            players = response.json()['players']
            print(dealer)
            print(players)
            return 1
        else:
            print(f"Failed to receive players. Status code: {response.status_code}")
            return 0
    except requests.exceptions.RequestException as e:
        print(f"Error receiving players: {e}")
        return 0

def send_reset_server():

    url = urlJS + "/reset"

    payload = {'key': resetKey}

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(f"Reset request sent successfully.")
            return 1
        else:
            print(f"Failed to send reset. Status code: {response.status_code}")
            return 0
    except requests.exceptions.RequestException as e:
        print(f"Error sending reset: {e}")
        return 0

def send_mode_server():

  url = urlJS + "/get-mode"

  payload = {'data': mode}

  try:
      response = requests.post(url, json=payload)
      if response.status_code == 200:
          print(f"Mode {mode} sent successfully.")
          return 1
      else:
          print(f"Failed to send mode {mode}. Status code: {response.status_code}")
          return 0
  except requests.exceptions.RequestException as e:
      print(f"Error sending mode: {e}")
      return 0 

def get_mode_server():

    global mode

    url = urlJS + "/send-mode"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Mode received successfully.")
            mode = response.json()['mode']
            print(mode)
            return 1
        else:
            print(f"Failed to receive mode. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error receiving mode: {e}")

if __name__ == "__main__":

    while True:

        if mode == None or mode == 0:
            get_mode_server()
            time.sleep(.5)
        else:
            if mode == 3:
                if get_players_server():
                    if dealer["state"] == "busted":
                        for player in players:
                            player["pot"] += 2 * player["bet"]
                    elif dealer["state"] == "BJ":
                        for player in players:
                            if player["state"] == "BJ":
                                player["pot"] += player["bet"]
                    else:
                        for player in players:
                            if player["state"] == "win":
                                player["pot"] += 2 * player["bet"]
                            if player["state"] == "push":
                                player["pot"] += player["bet"]
                    for player in players:
                        player["bet"] = 0
                        player["state"] = "playing"
                    dealer["state"] = "playing"
                if send_pots_server():
                    time.sleep(10)
                    send_reset_server()
                    mode = int(0)
                    send_mode_server()
            else:
                get_mode_server()
            time.sleep(.5)

