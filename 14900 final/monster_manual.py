import random
import mob
import global_variables
from monsters import Goblin, Hobgoblin, Bandit, Goblin_Gang
from monsters import Land_Shark, Clockwork_Hound

LEVELCAP = 7

PLAYER = global_variables.PLAYER

mobs = [
    Goblin.object, Hobgoblin.object, Bandit.object,
    Goblin_Gang.object, Land_Shark.object, Clockwork_Hound.object,
]

def spawn_mob(name:str):
    for entry in mobs:
        mob_object: mob.Mob = entry()
        if mob_object.id == name:
            return mob_object
    raise ValueError(f"No mob by id '{name}'.")

def spawn_random_mob():
    """
    Spawns a random mob.

    If the given level is not within the mob's level range, it picks a different random mob
    """
    if PLAYER.level >= LEVELCAP:
        raise ValueError("Player level too high!")

    enemy:mob.Mob = random.choice(mobs)()

    if PLAYER.level in range(enemy.range[0],enemy.range[1]):
        return enemy

    spawn_random_mob()
    #might be a more efficient way to do all this, but it's fine for now