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


def ping_server():
    

    # Connect to the MongoDB database
    client = MongoClient(os.environ["MONGO_URL"])


    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)