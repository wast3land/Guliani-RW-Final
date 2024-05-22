import random
from typing import Union
import global_variables, global_commands
import player
import status_effects

class Mob():

    def __init__(self, id:str="Anonymous_Mob", level:tuple= (1, 20)):
        #identification
        self._id = id
        self._name = self._id
        self._level = random.randrange(min(level), max(level))
        self._range = level

        self._stats = {
            "str": 10,
            "dex": 10,
            "con": 10,
            "int": 10,
            "wis": 10,
            "cha": 10,
            "damage-taken-multiplier": 1
        }

        self._max_hp = 8 + self.bonus("con")
        self._hp = self._max_hp

        self._max_ap = 1 + (self._level // 5)
        self._ap = self._max_ap

        self._damage_taken_multiplier = 1
        self._damage_multiplier = 1
        self._stats["evasion"] = 9

        #calculated stats
        self._max_hp = 8 + self.bonus("con")
        self._hp = self._max_hp

        self._max_ap = 1 + self._level // 5
        self._ap = self._max_ap

        self._damage = 0
        self._armor = 0
        self._dc = 10

        self._loot = {
            "gold": 0,
            "xp": 0,
            "drops": None
        }

        # %hp threshold at which the enemy flees, higher == more cowardly
        self._flee_threshold = 15 - self.bonus("cha") * 2
        self._player = global_variables.PLAYER

        self._status_effects: dict[str, status_effects.Status_Effect] = {}
        self._applied_status_effects = set()

        #tracks if the header for the turn has been printed yet
        self._header_printed = False

        self.update()

    #properties
    @property
    def id(self) -> str:
        return self._id
    @property
    def dead(self) -> bool:
        return self.hp <= 0
    @property
    def level(self) -> int:
        return self._level
    @property
    def damage(self) -> int:
        return self._damage
    @property
    def evasion(self) -> int:
        return self._evasion
    @property
    def armor(self) -> int:
        return self._armor
    @property
    def hp(self) -> int:
        return self._hp
    @property
    def loot(self):
        return self._loot
    @property
    def name(self) -> str:
        return self._name
    @property
    def dc(self) -> int:
        return self._dc
    @property
    def max_ap(self) -> int:
        return self._max_ap
    @property
    def ap(self) -> int:
        return self._ap
    @property
    def can_act(self) -> int:
        return self._ap > 0
    @property
    def fleeing(self) -> bool:
        return self._hp <= self._max_hp * (self._flee_threshold / 100)
    @property
    def range(self) -> int:
        return self._range
    @property
    def stats(self) -> dict:
        return self._stats
    @property
    def header(self) -> bool:
        return self._header_printed
    #methods

    #SETTERS
    def set_level(self, level:int)-> None:
        """
        Sets the mobs levels then calculates HP and loot based on level
        """
        self._level = level
        self.level_up()

    def set_damage_multiplier(self, num:int) -> None:
        self._damage_multiplier = num

    def reset_damage_multiplier(self) -> None:
        self.set_damage_multiplier(0)

    def set_header(self, val:bool) -> None:
        self._header_printed = val

    #ROLLS
    def roll_attack(self) -> int:
        """
        Rolls an attack (d20)
        """
        roll = random.randrange(1,20)

        if roll == 1:
            return 1
        if roll == 20:
            return 0
        
        return roll + self.bonus("dex") + self._level // 5

    def roll_a_check(self, stat:str):
        return random.randrange(1, 20) + self.bonus(stat)
    
    def roll_damage(self) -> int:
        """
        Rolls damage (damage dice)
        """
        return random.randrange(1, self._damage) * self._damage_multiplier + self.bonus("str")
    
    def take_damage(self, damage:int, armor_piercing=False) -> int:
        """
        Takes a given amount of damage, reduced by armor
        """
        damage *= self._damage_taken_multiplier
        if armor_piercing:
            self._hp -= damage
            return damage

        if (damage - self._armor) < 0:
            return 0
        else:
            self._hp -= damage - self._armor
            return damage - self._armor
        
    def fumble_table(self) -> Union[str, bool]:
        """
        Determines if a mob sufferes a negative effect upon rolling a nat 1.
        """
        return global_commands.probability(50)
        
    def attack_of_oppurtunity(self) -> bool:
        """
        Rolls an attack of opportuity against the player
        """
        if self.roll_attack() - 2 >= self._player.evasion:
            return True
        return False
    
    def heal(self, num:int) -> None:
        #heals for the given amount up to max hp value
        self._hp += self._hp + num if (self._hp + num <= self._max_hp) else self._max_hp
    
    #AP
    def spend_ap(self, num:int=1) -> None:
        """
        Spend an amount of AP
        """
        if num == 0:#spend_ap(0) indicates a full round action, uses all AP
            self._ap = 0
            return None
        if self.can_act is True:
            self._ap -= 1
        else:
            raise ValueError("No AP to spend")
        
    def reset_ap(self):
        """
        Resets mob's AP to max value
        """
        self._ap = self._max_ap
    
    #STATUS EFFECTS
    def add_status_effect(self, effect:status_effects.Status_Effect) -> None:
        """
        Adds a status effect to the mob
        """
        if effect.id in self._status_effects:
            #if we have the effect already, kick out of the function
            return None
        self._status_effects[effect.id] = effect
        effect.apply()

        self.update_stats()

    def remove_status_effect(self, effect:status_effects.Status_Effect) -> None:
        """
        Removes a status effect from the mob
        """
        del self._status_effects[effect.id]
        effect.cleanse()
        return None

    #MISC.
    def update(self):
        """
        Updates all relevant stats when a mob's level is changed,
        updates status effects and removes them when their duration
        expires. 
        """
        self.reset_ap()

        self.update_stats()
       
        #update all status effects
        inactive = []
        for entry in self._status_effects:
            effect: status_effects.Status_Effect = self._status_effects[entry]
            effect.update()
            if effect.active is False:
                inactive.append(effect)
        for effect in inactive:
            self.remove_status_effect(effect)
        inactive = []

    def update_stats(self) -> None:
        """
        Updates mobs stats seperately
        """
         #update calculated stats
        self._loot["gold"] = self._loot["gold"] * max(self._level // 2, 1)
        self._loot["xp"] = self._loot["xp"] * max(self._level // 2, 1)
        try:
            self._damage_taken_multiplier = self._stats["damage-taken-multiplier"]
        except KeyError:
            self._stats["damage-taken-multiplier"] = 1
            self._damage_taken_multiplier = self._stats["damage-taken-multiplier"]
        self._evasion = self._stats["evasion"] + self.bonus("dex")

    def level_up(self):
        #print("leveling up...")
        for _ in range(self._level-1):
            self._max_hp += random.randrange(1, self._max_hp) + round(self._level + 0.1 / 2)
            self._hp = self._max_hp
        self._max_ap = 1 + self._level // 5
        self._ap = self._max_ap
        self.update()
    
    def bonus(self, stat:str) -> int:
        return player.BONUS[self._stats[stat]]

    def special(self):
        raise NotImplementedError
    
    def trigger(self):
        return False
