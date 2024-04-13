import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

url = os.environ["MODAL_URL"]

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

response = requests.post(url, data=json.dumps(payload), headers=headers)

print(response.json())