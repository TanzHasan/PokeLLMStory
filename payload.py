import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
URL = os.environ["MODAL_URL"]
URL_GET_BATTLE = URL + "/get_battle"
URL_CHECK_HALUCINATION = URL + "/check_halucination"

class BattleHistory: 
    def __init__(self, game_string):
        self.ai_chat_history = [] 
        self.game_string = game_string
    def generate_next_move(self, prompt):
        self.ai_chat_history.append({"role": "user", "content": prompt})
        response = requests.post(URL_GET_BATTLE, data=json.dumps(self.ai_chat_history), headers=headers)
        print(response.json())
        expl = response.json()["result"]
        return expl
        



story_string = '''Darkrai is sent out!

The opposing Landorus is sent out!

The opposing Landorus's Intimidate cuts Darkrai's Attack!

The opposing player withdrew Landorus!

The opposing Iron Moth is sent out!

The opposing Iron Moth's Booster Energy allows it to get the Quark Drive!

Darkrai used Ice Beam!

It's not very effective...

The opposing Iron Moth was frozen solid!'''
payload = {
    "game_string": story_string,
    #"query": "You are commentating a pokemon battle between two trainers. Describe the battle succinctly but in an engaging way. Say no more than 50 words.",
    "query": "You are commentating a pokemon battle between two trainers. Describe the battle step by step but in an engaging way. Use dialogue to enhance game state and trash-talk. Make sure to align it with the battle state.",
    "data": {
        "pokemon": ["Darkrai", "Iron Moth", "Landorus"],
        "abilities": ["Quark Drive", "Intimidate"],
        "items": ["Booster Energy"],
        "moves": ["Dark Pulse"]
    }
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(URL_GET_BATTLE, data=json.dumps(payload), headers=headers)

print(response.json())