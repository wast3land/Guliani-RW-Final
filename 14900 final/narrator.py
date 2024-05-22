import time
import sys
import random
import global_commands
import global_variables
import player_commands

SCENE_CHANGE = [
    "You press towards your goal...\n",
    "Your resolve steeled, you continue forwards...\n",
    "Your weary legs carry you on...\n",
    "You venture deeper into the dungeon...\n"
]

EXIT_DUNGEON = [
    "You climb out of the darkness.",
    "You take your first breath of fresh in what feels like an eternity.",
    "Finally, out...",
    "The soft moonlight bathes the world in a gentle glow.",
    "The sky above you seems real enough to touch. You barely remember what it looked like...",
    "As you breathe a sigh of relief, you can't help but wonder if you'll make it out the next time...",
    "The openess of the Overworld is a stark contrast to the confines of the Dungeon.",
    "As you emerge from the Dungeon's darkness, the harsh light of day stings your eyes."
]

STORY_LINES = [
    ("Your friend entered the dungeon two weeks ago. He was supposed to be back on Tuesday but it's now Saturday " 
        "and you haven't heard from him. Do you enter the dungeon to find him?"
    ),

    "You see your friend's shoe ahead of you. Keep following the trail?",

    ("You find a wounded Gnome along the path. He says to you, "
     '"Someone just like you came through this dungeon two weeks ago. He helped me fight off a gang of goblins, '
     "but I haven't seen him in a while, and I'm sure he's "
     'been hurt!" '
     "Investigate the Gnome's story?"),

    ("You stop to ask the Shopkeeper about your friend. He says no one has come "
     "to buy anything from him in months before you did. He suggests the Gnome might have been lying to you. Continue your investigation?"),

    ("Still unsure if your friend is along this trail, you stop to think and recharge. "
     "Was the Gnome or the Shopkeeper lying? Perhaps the Gnome was talking about someone else? Continue?"),

    ("You stare at the dead monsters behind you. Your friend was strong enough to have defeated everything "
    "until this point. If he's in this dungeon, he'll be further ahead. Keep searching?"),

    ('You come upon a dejected Gnome. She asks: "Have you seen my child? '
     "He's ill "
     'and wandered off." You shake your head. Continue searching?'),

    "You notice a backpack up ahead. It looks suspicously like your friend's, and you suspect you are on the right path. Keep going?",

    ("You've been in this dungeon so long you almost forgot why you came here. You pull out a photo of your friend you brought "
     "with you and look it at while you sit down and catch your breath. Get back to finding him?"),

    ("You don't know why, but you have a feeling that your journey will be ending soon. You feel the presence of your friend. "
     "You don't know if he's safe or even alive, but he is nearby. Follow your gut?"),

    "You see a figure running some distance away from you, but you cannot make out who exactly it is. Try and catch them?",

    ("As you overcome this challenge, you walk forward, and turn the corner to see your friend waiting on the other side. "
     "He's sitting down next to a fire, cooking some sort of food. By his side is a sickly baby Gnome. "
     "You sit down by your friend and he explains to you that he got held up trying to nurse the baby Gnome back to health before "
     "contuining on with his quest. As you two are having this conversation, you are faced with your next obstacle. Brave the challenge?"),

    ("Having completed the challenge you were faced with, you return to your conversation. You ask your friend why he didn't just purchase "
     "a healing potion from the Shopkeeper to cure the baby's sickness. "
     "Your friend admits that he accidentally mistook the Shopkeeper's mother for a pet Orangutan in a family photo on the wall, "
     "and now the Shopkeeper won't sell to him. The Shopkeeper must have been trying to throw you off; he didn't want your friend found. "
     "\n You ask your friend for some gold, purchase a healing potion from the shopkeeper, and give it to the baby Gnome. After returning "
     "him to his mother, you two are free to continue through the rest of dungeon.\n"
     "Enter Free Play mode? \n ...")
]

ENTER_THE_SHOP = [
    "The Shopkeep eyes you sleepily.",
    "The Shopkeep glances at you warmly.",
    "The Shopkeep glares at you.",
    "The Shopkeep shoots you a friendly look.",
    "The Shopkeep barely notices you.",
    "The Shopkeep seems to look right through you.",
    "The Shopkeep eyes you eagerly.",
    "The Shopkeep grunts at your approach.",
    "The Shopkeep eyes you wearily."
]

EXIT_THE_SHOP = [
    "You go on your way.",
    "Your business is concluded.",
    "You slink out of the Shop.",
    "As you leave, you wonder if you'll see this place again...",
]

def next_scene_options():
    global_commands.type_text(random.choice(SCENE_CHANGE))
    ominous = f'    ...\n'
    for i in range(5):
        time.sleep(.5)
        print('\t'*i + ominous)

def level_up_options():
    global_commands.type_with_lines(' You have gained enough XP to level up! Which stat would you like to level up?\n')
    print("\t Strength - (str) | Dexterity - (dex) | Constitution - (con) | Intelligence - (int) | Wisdom - (wis) | Charisma - (cha)\n")

def event_options():
    global_commands.type_with_lines("Which stat would you like to roll?\n")
    print("\t Strength - (str) | Dexterity - (dex) | Constitution - (con) | Intelligence - (int) | Wisdom - (wis) | Charisma - (cha)\n")

def continue_run(next):
    if global_variables.PLAYER.story_index < len(STORY_LINES):
        global_commands.type_with_lines(STORY_LINES[global_variables.PLAYER.story_index] + " y/n\n") 
    else:
        global_commands.type_with_lines("Continue? y/n\n")
    command = input(">> ").lower()
    print("")#newline after cmd prompt
    if command == "y":   
        next_scene_options()
        next()
        command = None
        return None
    elif command == "n":
        exit_the_dungeon()
    elif command == "exit":
        global_commands.exit()
    else:
        global_commands.type_text("Invalid command. Please try again.\n")
        continue_run(next)

def exit_the_dungeon():
    global_variables.RUNNING = False
    global_commands.type_with_lines(random.choice(EXIT_DUNGEON))
    global_variables.restock_the_shop()
    menu_options()

def buy_something():
    global_commands.type_with_lines("Enter an item's number to purchase it OR (c) - Cancel Order\n")
    command = input(">> ").lower()
    print("")#newline after cmd prompt

    if command == "exit":
        global_commands.exit()
    elif command == "c":
        shopkeep_options()
    else:
        try:
            stock_num = int(command)
            item = global_variables.SHOPKEEP.inventory[stock_num-1]
        except ValueError:
            print("Invalid option, please try again.\n")
            buy_something()
        if stock_num <= global_variables.SHOPKEEP.stock_size+1:
            if item.is_consumable is False:
                if global_variables.SHOPKEEP.sell(item, global_variables.PLAYER) is False:
                    buy_something()
                else:
                    shopkeep_options()
            else:
                def ask_quantity():
                    global_commands.type_text(f"Please enter desired quantity:\n")
                    command = input(">> ").lower()
                    print("")#newline after... you get the idea
                    if command == "exit":
                        sys.exit()
                    try:
                        if global_variables.SHOPKEEP.sell(item, global_variables.PLAYER, int(command)) is False:
                            buy_something()
                        else:
                            shopkeep_options()
                    except TypeError:
                        print(f" Invalid quantity '{command}'. Please enter a valid quantity.\n")
                        ask_quantity()

                ask_quantity()
        else:
            print(f" Invalid item number '{int(command)}'. Please try again.\n")
            buy_something()

def leave_the_shop():
    global_commands.type_with_lines(random.choice(EXIT_THE_SHOP))
    menu_options()

def shopkeep_options():
    global_commands.type_with_lines(random.choice(ENTER_THE_SHOP))
    global_commands.type_with_lines("What would you like to do?\n")
    print("\t Buy Something - (b) | Leave - (l) | Sell something - (s) | Inventory - (i)\n")
    command = input(">> ").lower()
    print("")
    if command == "b":
        global_variables.SHOPKEEP.print_inventory()
        buy_something()
    elif command == "l":
        leave_the_shop()
    elif command == "i":
        check_player_inventory(shopkeep_options)
    elif command == "exit":
        global_commands.exit()
    else: 
        print("Invalid command, please try again")
        shopkeep_options()

def rest():
    global_commands.type_text("Plenty of time to rest when you're dead.\n", 2)
    menu_options()

def check_player_inventory(next):
    global_commands.type_with_lines("Inventory:\n")
    print(f"Gold: {global_variables.PLAYER.gold}\n")
    global_variables.PLAYER.print_inventory()
    def select_item():
        global_commands.type_with_lines("Enter an item's number to equip it OR (b) - Go Back\n")
        command = input(">> ").lower()
        print("")#newline after cmd prompt
        if command == "b":
            next()
        elif command == "exit":
            global_commands.exit()
        else:
            try:
                x = int(command)
            except ValueError:
                print("Invalid command, please try again.\n")
                select_item()
            item = global_variables.PLAYER.inventory[int(command)-1]
            if global_variables.PLAYER.equip(item) is True:
                check_player_inventory(next)
            else:
                print("Can't equip that.")
                select_item()
    select_item()

def menu_options():
    global_commands.type_with_lines("What would you like to do?\n")
    print("\t Enter the Dungeon - (e) | Rest - (r) | Visit the Shop - (v) | Inventory - (i) \n")
    command = input(">> ").lower()
    print("")#newline after cmd prompt
    match command:
            case "e": #enter the dungeon again
                global_variables.START_CMD = True
            case "r": #rest text
                rest()
            case "v": #visit the shop
                shopkeep_options()
            case "i": #check inventory
                check_player_inventory(menu_options)
            case "exit":
                global_commands.exit()
            case _:
                print(f"Invalid command: '{command}'. please try again\n")
                menu_options()

