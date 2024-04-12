import requests
from bs4 import BeautifulSoup
import json

URL_BULBAPEDIA = "https://bulbapedia.bulbagarden.net"
URL_POKEDEX = "https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_National_Pok%C3%A9dex_number"
URL_BULBAPEDIA_ITEMS = "https://bulbapedia.bulbagarden.net/wiki/List_of_items_by_name"
URL_BULBAPEDIA_POKEMON_MOVES = "https://bulbapedia.bulbagarden.net/wiki/List_of_moves" 
URL_BULBAPEDIA_POKEMON_ABILITIES = "https://bulbapedia.bulbagarden.net/wiki/Ability"
scrap 
pokemon_data = {}

def parse_pokemon_entry(href, pokemon_name, pokemon_number):
    page = requests.get(URL_BULBAPEDIA + href)
    results = BeautifulSoup(page.content, "html.parser")
    biology = results.find("span", id="Biology")
    parent_header = biology.parent.next_sibling
    biology_description = ""
    while(parent_header != None and parent_header.name != "h2" and parent_header.name != "h3"):
        if(parent_header.name == "p"):
            biology_description += parent_header.text 
            
        parent_header = parent_header.next_sibling
    pokemon_data[pokemon_name] = {
        "number": pokemon_number,
        "biology": biology_description
    }

    # print(parent_header.next_elements)
    # while




def parse_pokedex():
    page = requests.get(URL_POKEDEX)

    results = BeautifulSoup(page.content, "html.parser")

    generations = results.find_all("table", class_="roundy")
    number = ""
    for generation in generations:
        for entry in generation.find_all("tr"):
            columns = entry.find_all("td")
            if(columns == []):
                continue
            #alternative forms
            if(columns[0].find("a") != None):
                pokemon_tag = columns[1]
                pokemon_a = pokemon_tag.find("a")
                ref = pokemon_a.get("href")
                pokemon_name = pokemon_a.text
                form = " "+pokemon_tag.find("small").text
                
                pokemon_name += form
                parse_pokemon_entry(ref, pokemon_name, number)
            else:
                number_tag = columns[0]
                number = number_tag.text
                pokemon_tag = columns[1]
                pokemon_a = pokemon_tag.find("a")
                ref = pokemon_a.get("href")
                pokemon_name = pokemon_a.get("title")
                parse_pokemon_entry(ref, pokemon_name, number)
            print(number, pokemon_name)
            # break
        # break
    with open('pokemon_data.json', 'w') as json_file:
        json.dump(pokemon_data, json_file, indent=4)
        # poke = comp.find("a")
        # print(poke.text)
def parse_item_table(table, items_json): 
    for i,entry in enumerate(table.find_all("tr")):
        if(i == 0):
            continue
        columns = entry.find_all("td")
        if(len(columns) != 4):
            continue
        # print(columns)
        name = columns[1].text
        description = columns[3].text
        items_json[name] = description

    #
def parse_pokemon_item():
    page = requests.get(URL_BULBAPEDIA_ITEMS)
    results = BeautifulSoup(page.content, "html.parser")
    item_table_by_alphabet = results.find_all("table", class_="roundy")
    items_json = {}
    with open('items_data.json', 'w') as json_file:
        for i,table in enumerate(item_table_by_alphabet):
            # items_json = {}
            parse_item_table(table, items_json)
            print(chr(ord('A')+i))
        json.dump(items_json, json_file, indent=4)

def parse_pokemon_move(link): 
    page = requests.get(link)
    results = BeautifulSoup(page.content, "html.parser")
    move_description = results.find("span", id="Description")
    parent = move_description.parent
    description_table = parent.next_sibling.next_sibling.find("table")
    # # print(description_table)
    # print(parent)
    move_description = [] 
    for i,entry in enumerate(description_table.find_all("tr")):
        if(i == 0):
            continue
        columns = entry.find_all("td")
        move_description.append(columns[1].text)
    return move_description

def pares_pokemon_moves():
    page = requests.get(URL_BULBAPEDIA_POKEMON_MOVES)
    # print(page.content)
    moves_json = {}
    results = BeautifulSoup(page.content, "html.parser")
    moves_table = results.find("table", class_="sortable roundy")
    # print(str(moves_table)[:200])
    moves_table_body = moves_table.find("table", class_="sortable roundy").find("tbody")

    failed = {}
    for i,entry in enumerate(moves_table_body.find_all("tr")):
        if(i == 0):
            continue
        try:
            # print(entry)
            columns = entry.find_all("td")
            # print(columns)
            number = columns[0].text
            name = columns[1].find("a").text
            link = columns[1].find("a").get("href")
            # print(name, link)
            descriptions = parse_pokemon_move(URL_BULBAPEDIA + link)
            condensed_name = name.replace(" ", "").lower()
            print(condensed_name)
            moves_json[condensed_name] = {"name": name, "number": number, "descriptions": descriptions}
        except: 
            failed[name] = link
            print("failed",name)
    with open('failed_moves.json', 'w') as json_file:
        json.dump(failed, json_file, indent=4)
        # break
    with open('moves_data.json', 'w') as json_file:
        json.dump(moves_json, json_file, indent=4)


def parse_pokemon_abilities():
    page = requests.get(URL_BULBAPEDIA_POKEMON_ABILITIES)
    results = BeautifulSoup(page.content, "html.parser")
    abilities_header = results.find("span", id="List_of_Abilities")
    abilities_table = abilities_header.parent.next_sibling.next_sibling.find("table")
    # print(abilities_table)
    abilities_json = {}
    for i,entry in enumerate(abilities_table.find_all("tr")):
        if(i == 0):
            continue
        columns = entry.find_all("td")
        # number = columns[0].text
        name = columns[1].text
        description = columns[2].text
        abilities_json[name.strip()] = description.strip()
    
    with open('abilities_data.json', 'w') as json_file:
        json.dump(abilities_json, json_file, indent=4)
        # print(name, description)
        # break;
        # abilities_json[name] = description




            





    
#problems maybe 
#niodorino is a form of nidoranf

if __name__ == "__main__":
    # parse_pokedex()
    # parse_pokemon_item()
    # pares_pokemon_moves()
    parse_pokemon_abilities()