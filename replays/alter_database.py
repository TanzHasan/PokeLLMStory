# This code is mainly to alter the database for various reasons, and there is no reason to run this code
# multiple times. 

from dotenv import load_dotenv
from pymongo import MongoClient
import os

# Load environment variables from .env file
load_dotenv()

def back_up_moves():
    

    client = MongoClient(os.environ["MONGO_URL"])
    db = client['Data']
    collection = db['moves'] 

    print(collection.find_one())


# Grabs all the move names and descriptions
# and puts in file
def write_out_moves():

    moves = [
    "Agility", "Amnesia", "Ancient Power", "Baton Pass", "Belly Drum",
    "Blizzard", "Body Slam", "Clamp", "Confuse Ray", "Confusion",
    "Cross Chop", "Crunch", "Curse", "Double-Edge", "Drill Peck",
    "Dynamic Punch", "Earthquake", "Encore", "Explosion", "Fire Blast",
    "Flamethrower", "Giga Drain", "Growth", "Hidden Power", "Hydro Pump",
    "Hyper Beam", "Hypnosis", "Ice Beam", "Ice Punch", "Lovely Kiss",
    "Mean Look", "Mega Drain", "Mimic", "Moonlight", "Pain Split",
    "Perish Song", "Protect", "Psychic", "Rapid Spin", "Razor Leaf",
    "Recover", "Reflect", "Rest", "Return", "Roar", "Rock Slide",
    "Seismic Toss", "Self-Destruct", "Shadow Ball", "Sing", "Sleep Powder",
    "Sleep Talk", "Sludge Bomb", "Soft-Boiled", "Spikes", "Stun Spore",
    "Substitute", "Sunny Day", "Surf", "Swords Dance", "Thief", "Thunder",
    "Thunder Punch", "Thunder Wave", "Thunderbolt", "Toxic", "Transform",
    "Whirlpool", "Whirlwind", "Wrap"
    ]

    # Connect to the MongoDB database
    client = MongoClient(os.environ["MONGO_URL"])
    db = client['Data']
    collection = db['moves'] 

    # Open a file for writing
    with open('moves.txt', 'w') as file:
        # Iterate over all documents in the collection
        for document in collection.find():
            move_name = document['name']
            if move_name not in moves:
                continue
            move_descriptions = document['descriptions']

            # Write the move name and descriptions to the file
            file.write(f"Move: {move_name}\n")
            file.write("Descriptions:\n")
            file.write("Summarize:")
            for description in move_descriptions:
                file.write(f"{description}")
            file.write("\n")


def write_db():
            
     # Connect to the MongoDB database
    client = MongoClient(os.environ["MONGO_URL"])
    db = client['Data']
    collection = db['moves'] 
    read_descript = False

    all_moves = []



    with open('cleaned_moves.txt', 'r') as file:
        lines = file.readlines()

    for line in lines:
        if read_descript:
            descriptions = line
            read_descript = False

            quick_dict = {'name': move_name, 'descriptions': descriptions}

            all_moves.append(quick_dict)



        if line.startswith("Move:"):
            move_name = line.split(":")[1].strip()
        elif line.startswith("Descriptions:"):
            read_descript = True
            

            
        elif line == "\n":
           continue

    # print(all_moves)

    # Update all documents where the name is in the moves_data list
    for move in all_moves:
        result = collection.update_one(
            {'name': move['name']},
            {'$set': {'descriptions': [move['descriptions']]}}
        )
        print(f"Matched {result.matched_count} document(s) for move: {move['name']}")
        print(f"Modified {result.modified_count} document(s) for move: {move['name']}")

    # result = collection.update_one(
    #         {'name': "Sunny Day"},
    #         {'$set': {'descriptions': ["This move intensifies the sunlight for five turns, powering up and boosting the strength of the user's Fire-type attacks"]}}
    #     )
        # print(f"Matched {result.matched_count} document(s) for move: {move['name']}")
        # print(f"Modified {result.modified_count} document(s) for move: {move['name']}")


def ping_server():
    

    # Connect to the MongoDB database
    client = MongoClient(os.environ["MONGO_URL"])


    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)



def summarize():
    def replace_word(file_path, old_word, new_word):
        try:
            # Read the contents of the file
            with open(file_path, 'r') as file:
                content = file.read()

            # Replace all occurrences of the old word with the new word
            content = content.replace(old_word, new_word)

            # Write the modified content back to the file
            with open(file_path, 'w') as file:
                file.write(content)

            print(f"All instances of '{old_word}' have been replaced with '{new_word}' in the file.")
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except IOError:
            print(f"An error occurred while processing the file: {file_path}")

    # Example usage
    file_path = './moves.txt'
    old_word = 'Summarize'
    new_word = 'Summarize in 600 characters or less:'

    replace_word(file_path, old_word, new_word)