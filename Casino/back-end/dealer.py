import requests
import time

PortJS = 5555
IPTable = '192.168.4.12'
IPMainServer = '127.0.0.1'
urlJS = f'http://{IPMainServer}:{PortJS}'
players = [
    {"name": "John", "pot": 300, "bet": 0, "cards": [], "position": "1", "state": "playing"}, 
    {"name": "Ben", "pot": 400, "bet": 0, "cards": [], "position": "2", "state": "playing"}, 
    {"name": "Tim", "pot": 500, "bet": 0, "cards": [], "position": "3", "state": "playing"}, 
]
dealer = {"state": "playing"}
mode = None # Part of the game: 0 -> just betting; 1 -> drawing or passing; 2 -> dealer's turn; 3 -> betting computations(bank.py)

CARD_VALUES = {"A": (1, 11), "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10, "J": 10, "Q": 10, "K": 10} # TODO: remove

def hand_value(player: object):

    s = 0
    numAces = 0

    for card in player["cards"]:
        if card[0] == 'A':
            s += 11
            numAces += 1
        elif card[0] == 'K' or card[0] == 'Q' or card[0] == 'J' or card[0] == '1':
            s += 10
        else:
            s += int(card[0])

    for ace in range(numAces):
        if s > 21:
            s -= 10

    return s

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

def send_states_server():

    url = urlJS + "/get-states"

    states = {}

    for i in range(3):
        states[str(i+1)] = players[i]["state"]

    states["Dealer"] = dealer["state"]

    payload = {'states': states}

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(f"States {states} sent successfully.")
            return 1
        else:
            print(f"Failed to send states {states}. Status code: {response.status_code}")
            return 0
    except requests.exceptions.RequestException as e:
        print(f"Error sending states: {e}") 
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

    send_pots_server()
    send_states_server()

    while True:

        if mode == None or mode == 3:
            get_mode_server()
            time.sleep(3)
        else:
            if mode == 0:
                get_mode_server()
                time.sleep(.5)

            elif mode == 1:
                if get_players_server():

                    for player in players:

                        if player["state"] == "playing":
                            if hand_value(player) == 21:
                                player["state"] = "BJ"
                            if hand_value(player) > 21:
                                player["state"] = "busted"

                    if send_states_server():
                        get_mode_server() 
                time.sleep(.5)

            elif mode == 2:
                if get_players_server():

                    print(hand_value(dealer))
                    if hand_value(dealer) >= 17:

                        if hand_value(dealer) > 21:
                            dealer["state"] = "busted"
                        if hand_value(dealer) == 21:
                            dealer["state"] = "BJ"

                        for player in players:

                            if player["state"] == "playing":
                                if hand_value(player) > hand_value(dealer):
                                    player["state"] = "win"
                                if hand_value(player) < hand_value(dealer):
                                    player["state"] = "loss"
                                if hand_value(player) == hand_value(dealer):
                                    player["state"] = "push"

                        if send_states_server():
                            mode = 3
                            send_mode_server() # Activate the bank.py
                time.sleep(.5)