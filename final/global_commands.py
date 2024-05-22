import time
import sys
import csv
import random
import global_variables

TAG_TO_STAT = {
    "str": "Strength",
    "dex": "Dexterity",
    "con": "Constitution",
    "int": "Intelligence",
    "wis": "Wisdom",
    "cha": "Charisma",
    "base-evasion": "Evasion",
    "damage-taken-multiplier": "Vulnerability",
    "damage-multiplier": "Damage"
}

end_line = [
    ".", "!"
]


#print(TAG_TO_STAT["base-evasion"])
print("")

def exit():
    global_variables.RUNNING = False
    save()
    sys.exit()

def save():
    player_dict = global_variables.PLAYER.save_to_dict()
    with open('player.csv', "w", newline='') as file:
        w = csv.DictWriter(file, player_dict.keys())
        w.writeheader()
        w.writerow(player_dict)
        file.close()

    item_dict_list = []

    #append all inventory item_to_dicts to list
    for item in global_variables.PLAYER.inventory:
        print(item)
        item.save()
        item_dict_list.append(item.tod)

    #append equipped weapon and armor as dicts to the list
    global_variables.PLAYER.weapon.save()
    global_variables.PLAYER.armor.save()
    item_dict_list.append(global_variables.PLAYER.weapon.tod)
    item_dict_list.append(global_variables.PLAYER.armor.tod)

    #create fieldnames list from item_to_dict keys
    fields = list(global_variables.PLAYER.weapon.tod.keys())
    with open("inventory.csv", "w", newline='') as file:
            file.truncate(0)
            w = csv.DictWriter(file, fieldnames=fields)
            w.writeheader()
            w.writerows(item_dict_list)
            file.close()

def switch(header, text):
    """
    Prints the given text with lines if header is false
    and without lines if header is true
    """
    if header is True:
        type_text(text)
    elif header is False:
        type_with_lines(text)
    else:
        raise ValueError("header val not a boolean")

def generate_item_rarity() -> str:
    """
    Generates item rarity based on player level
    """
    if probability(10+global_variables.PLAYER.level):
        return "Epic"
    
    if probability(15+global_variables.PLAYER.level * 1.25):
        return "Rare"
    
    if probability(33+global_variables.PLAYER.level // 2):
        return "Uncommon"
    
    return "Common"

def probability(chance):
    return random.random() < (chance / 100)

def type_with_lines(text:str, num:int=1, speed:int = 0.03, delay=True) -> None:
    print("_"*110+"\n")
    type_text(text, speed, delay)
    if num > 1:
        print("_"*110+"\n")

def print_with_lines(text:str, num:int=1) -> None:
    print("_"*110+"\n")
    print(text)
    if num > 1:
        print("_"*110+"\n")

def type_list(text:str, speed:int = .03, delay=False) -> None:

    text = text.split(' ')
    #print(text)
    if delay is True:
        time.sleep(.2)
    for word in text:
        if word != "" and word != " ":
            time.sleep(speed)
        print(word + " ", end="", flush=True)

def type_text(text: str, speed: int = .03, delay=True) -> None:
    """
    Adds "typing" effect to text

    speed: an integer denoting the delay between characters
    """
    text = " " + text
    count = 0
    
    if delay is True:
        time.sleep(.2)

    if len(text) > 30:
        speed = 0.01
    elif len(text) > 20:
        speed = 0.02
    else: 
        speed = 0.03
        
    for idx, char in enumerate(text):
        
        time.sleep(speed)
        print(char, end='', flush=True)
        count += 1
        if (count >= 120) and char in end_line:
            print("\n")
            count = 0
        
    print("")#newline after typing text
