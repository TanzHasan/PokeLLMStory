import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
URL = os.environ["MODAL_URL"]
URL_GET_BATTLE = URL + "/get_battle"
URL_CHECK_HALUCINATION = URL + "/check_hallucination_test"
URL_BATTLE_CHAT_GENERATOR_TEST = URL + "/battle_chat_generator_test"

class BattleHistory: 
    def __init__(self, game_string, system_prompt, story_version_url, hallucination_check_url):
        #chat history with gpt
        self.ai_chat_history = [{"role": "system", "content": system_prompt}]
        # the story itself
        self.generated_story_history = []
        self.game_string = game_string
        #the batthe logs
        self.battle_logs = []
        #save for later
        self.game_data = {}
        self.story_version_url = story_version_url
        self.hallucination_check_url = hallucination_check_url

    def check_hallucination(self, next_part): 
        payload = { 
            "next_part": next_part,
            "story": "\n".join(self.generated_story_history),
            "battle_logs": "\n".join(self.battle_logs),
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
        response = requests.post(self.hallucination_check_url, data=json.dumps(payload), headers=headers)
        print(response.json())
        expl = response.json()["result"]
        # print(expl)
        if(expl == "" or expl == None): 
            return "Error"
        return expl
        

        


    def generate_next_move(self, prompt):
        self.ai_chat_history.append({"role": "user", "content": prompt})
        self.battle_logs.append(prompt)
        payload = {
        "messages" : self.ai_chat_history,
        "data": { 
            "pokemon": ["Darkrai", "Iron Moth", "Landorus"],
            "abilities": ["Quark Drive", "Intimidate"],
            "items": ["Booster Energy"],
            "moves": ["Dark Pulse"]
        }}
        headers = {
        "Content-Type": "application/json"
        }
        response = requests.post(self.story_version_url, data=json.dumps(payload), headers=headers)

        # print(response.json())
        expl = response.json()["result"]
        hallucination = self.check_hallucination(expl)
        self.generated_story_history.append(expl)
        self.ai_chat_history.append({"role": "assistant", "content": expl})

        return expl, hallucination
        
def commentator_generator_test(): 
    battle_logs = []

    with open('replays/cleaned_logs/1/gen1ou/gen1ou-2093289585.txt') as f:
        current_round = "The start of the battle is:\n"
        battle_start = True
        for i,line in enumerate(f): 
            if "Turn" in line:
                battle_logs.append(current_round)
                current_round = ""
                battle_start = False
            else:
                if battle_start and "Switched to" in line:
                    line = line.replace("Switched to", "Started with")
                current_round += line

        battle_logs.append(current_round)
    # print(battle_logs)
    prompt = '''pretend you are commentating a pokemon battle between two trainers. 
Describe the battle step by step but in an engaging way. 
Use dialogue to enhance game state and trash-talk. 
Make sure to align it with the battle state.
Make each prompt 50 words or less.'''
    with open('generated_stories/gen1ou/gen1ou-2093289585.txt', 'w') as f:
        battle_logs;
        battle = BattleHistory("", prompt, URL_BATTLE_CHAT_GENERATOR_TEST, URL_CHECK_HALUCINATION)
        for i, battle_line in enumerate(battle_logs):
            print("Round:",i)
            print(battle_line)
            expl, hallucination = battle.generate_next_move(battle_line)
            print(hallucination)
            print(expl)
            f.write("\n\nhallucination check (Does the move make sense?): " + str(hallucination) + "\n\n")
            f.write(expl)
    

if __name__ == "__main__":
    # commentator_generator_test()

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