import json

# Load your JSON data
with open('finetune_data_1.json', 'r') as file:
    data = json.load(file)

# Open a new file to store the JSONL output
with open('output.jsonl', 'w') as outfile:
    for entry in data:
        # Write the system message before each pair of user and assistant messages
        if entry['role'] in ['user', 'assistant']:
            # System message reinsertion
            system_message = {"role": "system", "content": "You are Gary in a Pokemon battle between you and Ash. Trash-talk Ash based on the actions in the battle. Your actions will be described in the following format \"Gary: [your action here]\". Ash actions will be described in the following format \"Ash: [Ash's action here]\". Do not say anything about the future. Only trash-talk about the current game state. Say 30 words or less."}
            json.dump(system_message, outfile)
            outfile.write('\n')
        # Write the actual entry
        json.dump(entry, outfile)
        outfile.write('\n')
