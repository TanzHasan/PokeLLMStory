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
    def __init__(self, game_string, system_prompt, story_version_url, hallucination_check_url, chain_count = 3, rewind_limit = 5):
        self.ai_chat_history = [{"role": "system", "content": system_prompt}]
        # the story itself
        self.generated_story_history = []
        self.game_string = game_string
        #the batthe logs
        self.battle_logs = []
        #save for later
        self.game_data = {}
        self.chain_count = chain_count
        self.story_version_url = story_version_url
        self.hallucination_check_url = hallucination_check_url
        self.rewind_limit = rewind_limit

        

    def check_hallucination(self, next_part): 
        story = "\n".join(self.generated_story_history)
        battle_logs = "\n".join(self.battle_logs)
        prompt = f"You are Gary in a pokemon battle against Ash, Your response to Ash's actions is:\n\n{next_part}\n\n What you have said so far is:\n\n{story}\n\n The battle logs are:\n\n{battle_logs}"
        hallucination_ask = '''Yes or No to the following question: Does your response make sense to Ash's actions?
 Only say Yes or No, nothing else. Only say Yes or No, nothing else. Only Say Yes or No, nothing else.'''
        payload = { 
            "prompt": prompt,
            "hallucination_ask": hallucination_ask,
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
        #returns a yes or no, to the quesiton "Does the move make sense?"
        response = requests.post(self.hallucination_check_url, data=json.dumps(payload), headers=headers)
        # print(response.json())
    
        expl = response.json()["result"]
        expl = expl.lower()

        if(expl == "" or expl == None or (expl != "yes" and expl != "no")): 
            return False
        return expl == 'yes'
        

    """ 
    Generates the next part of the story 

    all parts of the story are stored 

    self.ai_chat_history: the chat history with gpt
    self.battle_logs: the battle logs
    self.generated_story_history: the story itself


    prompt: the string text of the current round of the battle 
    """
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
            }
        }  
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(self.story_version_url, data=json.dumps(payload), headers=headers)

        expl = response.json()["result"]
        
        checks = []
        for _ in range(self.chain_count):
            checks.append(self.check_hallucination(expl))
        self.generated_story_history.append(expl)
        self.ai_chat_history.append({"role": "assistant", "content": expl})

        return expl, checks
    def rewind(self, rounds): 
        if(len(self.battle_logs) < rounds): 
            raise Exception("Not enough rounds to rewind")
        for _ in range(rounds):
            self.ai_chat_history.pop()
            self.ai_chat_history.pop()
            self.battle_logs.pop()
            self.generated_story_history.pop()

    def generate_next_move_with_checks(self, prompt):
        expl, checks = self.generate_next_move(prompt)
        print(checks)
        hallucinations = checks.count(False)
        for _ in range(self.rewind_limit):
            if hallucinations/self.chain_count >= 0.5: 
                print(expl)
                self.rewind(1)
                expl, checks = self.generate_next_move(expl)
                print(checks)
                hallucinations = checks.count(False)
            else: 
                break
        # print(expl)
        return expl

            
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
            if "p1" in line: 
                line = line.replace("p1", "Ash")
            if "p2" in line:
                line = line.replace("p2", "Gary")
            current_round += line

        battle_logs.append(current_round)
    # print(battle_logs)
#     prompt = '''pretend you are commentating a pokemon battle between two trainers. 
# Describe the battle step by step but in an engaging way. 
# Use dialogue to enhance game state and trash-talk. 
# Make sure to align it with the battle state.
# Make each prompt 50 words or less.'''
    prompt = '''You are Gary in a pokemon battle between you and Ash. Your actions will be described in the following format 
"Gary: [your action here]". Ash actions will be described in the following format "Ash: [Ash's action here]".
Trash-talk Ash. Do not say anything about the future. Do not say anything about the future.
Only trash-talk about the current game state. Say 30 words or less.'''
    with open('hal.txt', 'w') as f:
        battle = BattleHistory("", prompt, URL_BATTLE_CHAT_GENERATOR_TEST, URL_CHECK_HALUCINATION)
        for i, battle_line in enumerate(battle_logs):
            print("Round:",i)
            print(battle_line)
            expl = battle.generate_next_move_with_checks(battle_line)
            print(expl)
            print("\n\n")
        # print(battle.generated_story_history)
        f.write("\n\n".join(battle.generated_story_history))

if __name__ == "__main__":
    commentator_generator_test()

    # story_string = '''Darkrai is sent out!

    # The opposing Landorus is sent out! 

    # The opposing Landorus's Intimidate cuts Darkrai's Attack!

    # The opposing player withdrew Landorus!

    # The opposing Iron Moth is sent out!

    # The opposing Iron Moth's Booster Energy allows it to get the Quark Drive!

    # Darkrai used Ice Beam!

    # It's not very effective...

    # The opposing Iron Moth was frozen solid!'''

    # payload = {
    #     "game_string": story_string,
    #     #"query": "You are commentating a pokemon battle between two trainers. Describe the battle succinctly but in an engaging way. Say no more than 50 words.",
    #     "query": "You are commentating a pokemon battle between two trainers. Describe the battle step by step but in an engaging way. Use dialogue to enhance game state and trash-talk. Make sure to align it with the battle state.",
    #     "data": {
    #         "pokemon": ["Darkrai", "Iron Moth", "Landorus"],
    #         "abilities": ["Quark Drive", "Intimidate"],
    #         "items": ["Booster Energy"],
    #         "moves": ["Dark Pulse"]
    #     }
    # }

    # headers = {
    #     "Content-Type": "application/json"
    # }

    # response = requests.post(URL_GET_BATTLE, data=json.dumps(payload), headers=headers)

    

    # # print(response.json())
