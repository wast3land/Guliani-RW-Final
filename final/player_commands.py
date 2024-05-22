import random
import csv
import sys
import global_commands
import global_variables
import mob
import items
import narrator
import status_effects

GOD_MODE = False
TEST = None

ENEMY:mob.Mob = None
ENEMY_TURN = None
END_SCENE = None

PLAYER = global_variables.PLAYER
PLAYER_TURN = None
PLAYER_DEATH = None

NEXT_SCENE = None

def turn_options():
    global_commands.type_with_lines(f"What would you like to do? Action Points: {PLAYER.ap}/{PLAYER.max_ap}\n")
    options = "\t Attack - (a) | Check HP - (hp) | Flee - (f) | Inventory - (i) | Pass Turn - (p) | Cleanse a Status Effect - (c)"
    print(options)

def cleanse_an_effect():
    global_commands.type_with_lines("Select an effect to cleanse OR Cancel - (c)\n")
    for idx, effect in enumerate(PLAYER.status_effects):
        effect: status_effects.Status_Effect = effect
        print(f"{idx+1}. {effect.id}\n")

    cmd = input(">> ").lower()
    print("")
    try:
        num = int(cmd)
        effect: status_effects.Status_Effect = PLAYER.status_effects[num-1]
        PLAYER.spend_ap()
        if effect.attempt_cleanse(PLAYER.roll_a_check(effect.cleanse_stat)) is True:
            if PLAYER.can_act is True:
                turn_options()
                return None
            ENEMY_TURN()
            return None
        else:
            raise Exception("attempt failed")

    except ValueError:
        if cmd == "exit":
            global_commands.exit()
        elif cmd == "c":
            turn_options()
        else:
            #invalid entry
            pass 
  
def attack(run_on_hit=None, run_on_miss=None) -> None:
    """
    Attacks an enemy. 

    enemy: a Mob object, the target

    end_scene: function to run if the player kills the enemy

    Returns nothing
    """
    if PLAYER.can_act is False:
        global_commands.type_text("No AP available.")
        turn_options()
        return None

    if run_on_miss is None:
        run_on_miss = ENEMY_TURN
    if run_on_hit is None:
        run_on_hit = ENEMY_TURN

    if GOD_MODE is True:
        attack_roll = 1000000
    else:
        attack_roll = PLAYER.roll_attack() if TEST is False else 1
        PLAYER.spend_ap()

    global_commands.type_with_lines(f"You attack the {ENEMY.id}, rolling a {attack_roll}.\n")

    if attack_roll == 0:
        global_commands.type_text("Critical Hit!\n")
        taken = ENEMY.take_damage(PLAYER.roll_damage() * PLAYER.weapon.crit)

    if attack_roll == 1:
        global_commands.type_text("Crtical Fail!\n")

    if attack_roll >= ENEMY.evasion:
        if GOD_MODE is True:
            taken = ENEMY.take_damage(1000)
        else:
            taken = ENEMY.take_damage(PLAYER.roll_damage())

        if ENEMY.dead is False and PLAYER.can_act is False:
            global_commands.type_text(f"You hit the {ENEMY.id} for {taken} damage.") #last thing printed = no \n
            run_on_hit()
        elif ENEMY.dead is True:
            global_commands.type_text(f"You hit the {ENEMY.id} for {taken} damage.\n")
            END_SCENE()
        else:
            turn_options()

    elif attack_roll < ENEMY.evasion:
        global_commands.type_text("You missed.") #last thing printed = no \n
        if PLAYER.can_act is False:
            run_on_miss()
        else: 
            turn_options()

def show_hp() -> None:
    """
    Prints the player's HP then runs the given function
    """
    global_commands.print_with_lines(f' HP: {PLAYER.hp}/{PLAYER.max_hp}')
    print(" ["+"/"*PLAYER.hp+" "*(PLAYER.max_hp-PLAYER.hp)+"]")
    turn_options()

def show_inventory() -> None:
    """
    Prints the player's inventory then runs the given function
    """
    global_commands.print_with_lines(f"Gold: {PLAYER.gold}\n")
    PLAYER.print_inventory()
    select_an_item()

def select_an_item() -> None:
    global_commands.type_with_lines("Enter an Item's number to use it | Go Back - (b)\n")
    command = input(">> ")
    print("")

    if command.lower() == "b":
        PLAYER_TURN()
        return None
    try:
        command = int(command)
        try:
            item = PLAYER.inventory[command - 1]
        except IndexError:
            print(" Please enter a valid item number.")
            select_an_item()
            return None
    except ValueError:
        print(" Please enter a valid command.")
        select_an_item()
        return None
    use_an_item(item, ENEMY)

def use_an_item(item: items.Consumable, target=None) -> None:
    """
    Uses an item on the Player, if the player has the item in their inventory
    """
    if PLAYER.can_act is False:
        global_commands.type_text("No AP available.")
        PLAYER_TURN()
        return None
    if item is None:
        global_commands.type_text("Invalid item selected. Please try again.")
        PLAYER_TURN()
        return None
    if PLAYER.has_item(item) is True:#check the player has the item
        if item.is_consumable is True:
            item = PLAYER.find_item_by_name(item.name)
            held_item:items.Consumable = item
            if held_item.quantity == 0: #if the items quantity is 0, remove it
                PLAYER.inventory.remove(held_item)
                held_item.set_owner(None)
                global_commands.type_with_lines(f"No {item.name} avaliable!")
                select_an_item()
                return None
            held_item.use(target)

            if PLAYER.can_act is False:
                #PLAYER.reset_ap()
                ENEMY_TURN()
            else:
                turn_options()
        else:
            global_commands.type_text(f"{item.name} is not a consumable.")
            select_an_item()
    else:
        global_commands.type_with_lines(f"No {item.name} avaliable!")
        turn_options()

def stop_flee_attempt() -> None:
    """
    Checks to see if an enemy is able to successfuly interrupt
    a player's attempt to flee
    """
    global_commands.type_text(f"The {ENEMY.id} attempts to stop you!")
    if ENEMY.attack_of_oppurtunity(PLAYER) is True:
        global_commands.type_text("It caught up with you! You escape but not unscathed.")
        #player.lose_some_items
        narrator.exit_the_dungeon()
    else:
        global_commands.type_text("It failed. You've escaped.")

def flee() -> None:
    """
    Attempts to run away from the current encounter
    """
    if PLAYER.can_act is False:
        global_commands.type_text("No AP available.")
        turn_options()

    global_commands.type_with_lines("You attempt to flee...\n")
    
    if global_commands.probability(90 - int((PLAYER.hp / PLAYER.max_hp) * 100)):
        #higher HP == lower chase chance
        stop_flee_attempt()
    else:
        global_commands.type_text(f"The {ENEMY.id} lets you go.")
        narrator.exit_the_dungeon()

def load():
    PLAYER.load("player.csv", "inventory.csv")

def reset():
    with open('player.csv', "r+") as file:
        file.truncate(0)
        file.close()

    with open('inventory.csv', "r+") as file:
        file.truncate(0)
        file.close()