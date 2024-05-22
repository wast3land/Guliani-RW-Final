#enemy commands file
import global_commands
import global_variables
import narrator
import player_commands
import mob

ENEMY:mob.Mob = None
ENEMY_TURN = None
END_SCENE = None

PLAYER = None
PLAYER_TURN = None
PLAYER_DEATH = None

NEXT_SCENE = None

def turn_options():
    if ENEMY.dead:
        END_SCENE()
    if ENEMY.fleeing:
        enemy_flee_attempt()
        return None
    #if trigger is active, 75% chance of special
    if ENEMY.trigger() is True:
        if global_commands.probability(75) is True:#75
            if ENEMY.special() is True:
                run_enemy_next()
                return None
        else:
            enemy_attack()
            return None
    else: #if trigger not active, 25% of doing special
        if global_commands.probability(25) is True:
            if ENEMY.special() is True:
                run_enemy_next()
                return None
        enemy_attack()
        return None

def enemy_flee_attempt():
    """
    Runs when the enemy tries to escape. Lets the player
    choose whether to let them go or pursue them.

    next = the function to run if the player stops them successfully
    """
    def enemy_flee_success():
        global_commands.type_text("It got away.")
        narrator.continue_run(NEXT_SCENE)
    def enemy_flee_failure():
        global_commands.type_text(f"You stopped the {ENEMY.id}. It is forced to continue fighting.")
        PLAYER_TURN()
    global_commands.switch(ENEMY.header, f"The {ENEMY.id} attempts to flee...\n")
    print(" Try to stop them? y/n\n")
    command = input(">").lower()
    #print("")#newline after cmd prompt
    if command == "y":
        PLAYER.reset_ap()
        player_commands.attack(enemy_flee_failure, enemy_flee_success)
    if command == "n":
        global_commands.type_text(f"You let the {ENEMY.id} go.")
        narrator.continue_run(NEXT_SCENE)

def run_enemy_next():
    """
    Checks if the enemy can still act and passes the 
    turn to the appropriate actor

    PLAYER_TURN = function to run if the player goes next
    enemy_next = ditto but for enemy
    """
    if ENEMY.can_act is False:
        #ENEMY.reset_ap()
        PLAYER_TURN()
    else:
        turn_options()

def enemy_attack():
    """
    Runs the enemy attack
    """
    ENEMY.spend_ap()
    attack = ENEMY.roll_attack()
    global_commands.switch(ENEMY.header, f"The {ENEMY.id} attacks you, rolling a {attack}\n")
    if attack == 0:
        global_commands.type_text(f"A critical hit! Uh oh.\n")
        taken = global_variables.PLAYER.take_damage(ENEMY.roll_damage() * 2)
        global_commands.type_text(f"The {ENEMY.id} hit you for {taken} damage!\n")
        if global_variables.PLAYER.dead is False:
            run_enemy_next()
        else:
            PLAYER_DEATH()
    elif attack == 1:
        global_commands.type_text(f"It critically failed!\n")
        if ENEMY.fumble_table() is True:
            taken = ENEMY.take_damage(ENEMY.roll_damage())
            global_commands.type_text(f"The {ENEMY.id} hit itself for {taken} damage!")
        else:
            global_commands.type_text(f"It missed.")
        if ENEMY.dead is True:
            END_SCENE()
        else:
            run_enemy_next()
    else: 
        if attack >= global_variables.PLAYER.evasion:
            taken = global_variables.PLAYER.take_damage(ENEMY.roll_damage())
            global_commands.type_text(f"The {ENEMY.id} hit you for {taken} damage.")
            if global_variables.PLAYER.dead is True:
                PLAYER_DEATH()
            else:
                run_enemy_next()
        else:
            global_commands.type_text(f"The {ENEMY.id} missed.")
            run_enemy_next()