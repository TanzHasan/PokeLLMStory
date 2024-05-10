import requests
import json
import os
from dotenv import load_dotenv
from replays.parse_log import parse_log_file, action_to_string
from replays.data_model import Battle, Turn, Action, ActionResult, Pokemon

load_dotenv()
URL = os.environ["MODAL_URL"]
URL_GET_BATTLE = URL + "/get_battle"
URL_CHECK_HALLUCINATION = URL + "/check_hallucination_test"
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

    
    def check_hallucination_multiple(self , next_part, action_prompt):
        battle_logs = "\n".join(self.battle_logs)
        hallucination_check_asks = [f'''This is your response: \n {next_part} \n Answer Yes or No. Does your response make sense to the battle state? Only say Yes or No, nothing else. Only say Yes or No, nothing else. Only Say Yes or No, nothing else.''',
                                    f'''This is your response: \n {next_part} \n Answer Yes or No. Does your response contain the correct pokemon? Only say Yes or No, nothing else. Only say Yes or No, nothing else. Only Say Yes or No, nothing else.''',
                                    f'''This is your response: \n {next_part} \n Answer Yes or No. Does your response contain the correct move? Only say Yes or No, nothing else. Only say Yes or No, nothing else. Only Say Yes or No, nothing else.''',
                                    f'''This is your response: \n {next_part} \n Answer Yes or No. Are the description of the move correct? Only say Yes or No, nothing else. Only say Yes or No, nothing else. Only Say Yes or No, nothing else.''',
                                    f'''This is your response: \n {next_part} \n, Here is the whole battle log: \n {battle_logs} \n Answer Yes or No. Does your response make sense to the battle state? Only say Yes or No, nothing else. Only say Yes or No, nothing else. Only Say Yes or No, nothing else.''',
        ]
        for hallucination_check_ask in hallucination_check_asks:
            payload = { 
                "prompt": hallucination_check_ask,
                "hallucination_ask": action_prompt,
                "data": self.game_data
            }
            headers = {
                "Content-Type": "application/json"
            }
            #returns a yes or no, to the quesiton "Does the move make sense?"
            response = requests.post(self.hallucination_check_url, data=json.dumps(payload), headers=headers)
            # print(response.json())
        
            expl = response.json()["result"]
            expl = expl.lower()
            if("no" in expl):
                return False
            if("yes" in expl):
                continue
            return False
        return True
        

    def check_hallucination(self, next_part, action_prompt, info):         
        story = "\n".join(self.generated_story_history)
        battle_logs = "\n".join(self.battle_logs)
        prompt = f"You are Gary in a pokemon battle against Ash, You are responding to the actions in the battle in a disrespectful/trash talking tone. This is the current round of the battle: \n\n {action_prompt}"
        hallucination_ask = f'''This is your response: \n {next_part} \n Answer Yes or No. Does your response make sense to the battle state? Only say Yes or No, nothing else. Only say Yes or No, nothing else. Only Say Yes or No, nothing else.'''
        payload = { 
            "prompt": prompt,
            "hallucination_ask": hallucination_ask,
            "data": info
        }
        headers = {
            "Content-Type": "application/json"
        }
        #returns a yes or no, to the quesiton "Does the move make sense?"
        response = requests.post(self.hallucination_check_url, data=json.dumps(payload), headers=headers)
        # print(response.json())
    
        expl = response.json()["result"]
        expl = expl.lower()
        if("no" in expl):
            return False
        if("yes" in expl):
            return True

        return False
    def check_hallucination_with_reason(self, next_part, action_prompt, info): 
        story = "\n".join(self.generated_story_history)
        battle_logs = "\n".join(self.battle_logs)
        # print(battle_logs)

#         prompt = f"You are currently player 2 (p2), Your response to the player 1 (p1) actions is:\n\n{next_part}\n\n What you have said so far is:\n\n{story}\n\n The battle logs are:\n\n{battle_logs}"
#         hallucination_ask = '''Yes or No to the following question: Does your response make sense to player 1's (p1) actions?
#  Only say Yes or No, nothing else. Only say Yes or No, nothing else. Only Say Yes or No, nothing else.'''
        prompt = f"You are Gary in a pokemon battle against Ash, You are responding to the actions in the battle in a disrespectful/trash talking tone. This is the current round of the battle: \n\n {action_prompt}"
        hallucination_ask = f'''This is your response: \n {next_part} \n Answer Yes or No and give a reason. Does your response make sense to the battle state? '''
        payload = { 
            "prompt": prompt,
            "hallucination_ask": hallucination_ask,
            "data": info
        }
        headers = {
            "Content-Type": "application/json"
        }
        #returns a yes or no, to the quesiton "Does the move make sense?"
        response = requests.post(self.hallucination_check_url, data=json.dumps(payload), headers=headers)
        # print(response.json())
    
        expl = response.json()["result"]
        expl = expl.lower()
        print('\n')
        print(expl)
        print('\n')

        if expl.startswith("no"):
            return False
        if expl.startswith("yes"):
            return True

        return False
        

    """ 
    Generates the next part of the story 

    all parts of the story are stored 

    self.ai_chat_history: the chat history with gpt
    self.battle_logs: the battle logs
    self.generated_story_history: the story itself


    prompt: the string text of the current round of the battle 
    """
    def generate_next_move(self, prompt, info):

        self.ai_chat_history.append({"role": "user", "content": prompt})
        self.battle_logs.append(prompt)

        payload = {
            "messages" : self.ai_chat_history,
            "data": info
        }  
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(self.story_version_url, data=json.dumps(payload), headers=headers)

        expl = response.json()["result"]
        prev_message = response.json()["prev_message"]
        self.ai_chat_history[-1]['content'] = prev_message
        
        checks = []
        for _ in range(self.chain_count):
            checks.append(self.check_hallucination(expl, prompt, info))
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

    def generate_next_move_with_checks(self, prompt, info):
        expl, checks = self.generate_next_move(prompt, info)
        print(checks)
        hallucinations = checks.count(False)
        for _ in range(self.rewind_limit):
            if hallucinations/self.chain_count >= 0.5: 
                print(expl)
                self.rewind(1)
                expl, checks = self.generate_next_move(prompt, info)
                print(checks)
                hallucinations = checks.count(False)
            else: 
                break
        # print(expl)
        return expl

def get_turn_info(turn: Turn):
    info = {"pokemon": [], "moves": [], "items": [], "abilities": []}
    for action in turn.actions:
        if action.type == "switch":
            info["pokemon"].append(action.name)
        if action.type == "move":
            info["moves"].append(action.name)

    return info
def generate_story_with_file(prompt, file, p_name_mapping = {"p1a": "Ash", "p2a": "Gary"}):
    battle_logs = parse_log_file(file)
    battle = BattleHistory("", prompt, URL_BATTLE_CHAT_GENERATOR_TEST, URL_CHECK_HALLUCINATION)
    
    for i, turn in enumerate(battle_logs.turns):
        print("Round: ", i)
        turn_info = get_turn_info(turn)
        turn_text = ""
        active_pokemon = {}
        if turn.turn_num != 0:
            active_pokemon = {
                "p1a": turn.pokemon["p1a"].pokemon_name,
                "p2a": turn.pokemon["p2a"].pokemon_name,
            }
        # print("Testing: ", len(turn.actions))
        for action in turn.actions:
            turn_text += action_to_string(turn, action, p_name_mapping, active_pokemon)+'\n'
        print(turn_text)
        print(str(turn_info)+"\n")
        # print(json.dumps(turn_info))
        expl = battle.generate_next_move_with_checks(turn_text, turn_info)
        print(expl)
        print('\n\n')
    
    with open('rewind_test.txt', 'w') as f:
        f.write("\n\n".join(battle.generated_story_history))
    with open("rewind_test.json", "w") as f:
        f.write(json.dumps(battle.ai_chat_history, indent=4))

def wooper_hallucination_test(prompt):
    battle = BattleHistory("", prompt, URL_BATTLE_CHAT_GENERATOR_TEST, URL_CHECK_HALLUCINATION)
    turn_text = ''' Gary: Wooper used Ice punch on Dragonite for 100 damage it was super effective
Ash: Dragonite Roost and healed for 50
'''
    turn_info = {"pokemon": ["Dragonite", "Tauros", "Wooper"], "moves": ["Ice Punch"], "items": [], "abilities": []}
    expl = battle.generate_next_move_with_checks(turn_text, turn_info)
    print(expl)

def hallucination_check_test(prompt): 
    battle = BattleHistory("", prompt, URL_BATTLE_CHAT_GENERATOR_TEST, URL_CHECK_HALLUCINATION)
    story = '''Ash: Alakazam can't move
Gary: Tauros used Hyper Beam on Alakazam for 100 damage
Ash: Alakazam fainted
Ash: Alakazam switched out for Exeggutor
'''
    generated_text = '''HA! Starmie stood no chance! and now your Exeggutor is next!'''
    turn_info = {"pokemon": ["Alakazam", "Tauros", "Exeggutor"], "moves": ["Hyper Beam"], "items": [], "abilities": []}
    expl = battle.check_hallucination_with_reason(generated_text, story, turn_info)
    print(expl)

if __name__ == "__main__":
#     prompt = '''Pretend you are player 2 in a pokemon battle between two trainers. 
# Trash talk player 1 in an engaging and entertaining way.
# Make sure to align it with the battle state. sat 30 words or less.'''
    prompt = '''You are Gary in a pokemon battle between you and Ash. Trash-talk Ash based on the actions in the battle. Your actions will be described in the following format 
"Gary: [your action here]". Ash actions will be described in the following format "Ash: [Ash's action here]". Do not say anything about the future. Do not say anything about the future.
Only trash-talk about the current game state. Say 30 words or less.'''

    file = "replays/logs/gen1ou/gen1ou-2093371513.log"
    # wooper_hallucination_test(prompt)
    # print("\n\n")
    # for i in range(3):
    #     hallucination_check_test(prompt)
    #     print("\n\n")
    



    generate_story_with_file(prompt, file, p_name_mapping = {"p1a": "Ash", "p2a": "Gary"})



def commentator_generator_test_old(prompt): 
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
    with open('hal.txt', 'w') as f:
        battle = BattleHistory("", prompt, URL_BATTLE_CHAT_GENERATOR_TEST, URL_CHECK_HALLUCINATION)
        for i, battle_line in enumerate(battle_logs):
            print("Round:",i)
            print(battle_line)
            expl = battle.generate_next_move_with_checks(battle_line)
            print(expl)
            print("\n\n")
        # print(battle.generated_story_history)
        f.write("\n\n".join(battle.generated_story_history))