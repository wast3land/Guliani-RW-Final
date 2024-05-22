import random
import os
import csv
import items
import global_commands
from events import Event
import status_effects

BONUS = {
    5: -4,
    6: -3,
    7: -2,
    8: -1, 
    9: -1,
    10: 0,
    11: 0,
    12: 1,
    13: 1,
    14: 2,
    15: 2,
    16: 3,
    17: 3,
    18: 4,
    19: 4,
    20: 5
}

HP_POT = None
FIREBOMB = None

ITEM_TYPES = {
    "Weapon": items.Weapon,
    "Armor": items.Armor,
    "Item": items.Item,
    "Consumable": items.Consumable,
    "Health_Potion": items.Health_Potion,
    "Firebomb": items.Firebomb
}

class Player():

    def __init__(self, id: str="Player", name:str = "New Player"):
        self._id = id
        self._name = name
        self._level = 1
        self.story_index = 0

        self._stats = {
            "str": 10,
            "dex": 10,
            "con": 10,
            "int": 10,
            "wis": 10,
            "cha": 10,
        }

        self._max_hp = 10 + self.bonus("con")
        self._hp = self._max_hp
        self._max_ap = 1 + (self._level // 5)
        self._ap = self._max_ap
        self._damage_taken_multiplier = 1
        self._damage_multiplier = 1

        self._stats["base-evasion"] = 9
        self._stats["damage-taken-multiplier"] = self._damage_taken_multiplier
        self._stats["damage-multiplier"] = self._damage_multiplier
        self._stats["hp"] = self._hp
        self._stats["ap"] = self._max_ap
        
        #xp/gold/items
        self._xp = 0
        self._gold = 0
        self._inventory = []
        self._status_effects:dict[str, status_effects.Status_Effect] = {}
        self._level_up_function = None

        #equipment
        self._equipped = {
            "Weapon": None, 
            "Armor": None
        }

    #properties
    @property
    def dead(self) -> bool:
        """
        Checks if the player is dead (ie HP <= 0)
        """
        return self._hp <= 0
    @property
    def stats(self) -> int:
        return self._stats
    @property
    def level(self) -> int:
        return self._level
    @property
    def str(self) -> int:
        return self._stats["str"]
    @property
    def dex(self) -> int:
        return self._stats["dex"]
    @property
    def con(self) -> int:
        return self._stats["con"]
    @property
    def int(self) -> int:
        return self._stats["int"]
    @property
    def wis(self) -> int:
        return self._stats["wis"]
    @property
    def cha(self) -> int:
        return self._stats["cha"]
    @property
    def hp(self) -> int:
        return self._hp
    @property
    def xp(self):
        return self._xp
    @property
    def armor(self) -> items.Armor:
        """
        Returns player's armor value, proably should be an object too
        """
        return self._equipped["Armor"]
    @property
    def weapon(self) -> items.Weapon:
        """
        Returns player's weapon object
        """
        return self._equipped["Weapon"]
    @property
    def evasion(self):
        return self._stats["base-evasion"] + self.bonus("dex")
    @property
    def carrying_capacity(self) -> int:
        return int(5.5 * self._stats["str"])
    @property
    def current_weight(self) -> int:
        total_weight = 0
        for entry in self._inventory:
            if entry is not None:#check to make sure the entry is valid
                held_item:items.Item = entry
                total_weight += held_item.total_weight
        for item in self._equipped:
            if self._equipped[item] is not None: #check to make sure an item is equipped, add its weight to the total if it is
                total_weight += self._equipped[item].weight
        return total_weight
    @property
    def gold(self):
        return self._gold
    @property
    def inventory(self) -> dict:
        return self._inventory
    @property
    def inventory_size(self) -> int:
        return len(self._inventory) + 1
    @property
    def id(self):
        return self._id
    @property
    def name(self):
        return self._name
    @property
    def max_hp(self):
        return self._max_hp
    @property
    def threat(self):
        """
        Returns the player's current threat level which effect mob spawns
        """
        if int(self._level * 1.5) == 1:
            return 2
        return int(self._level * 1.5)
    @property
    def level_up(self):
        """
        Checks if the player has enough XP to level up
        """
        return self.xp > (15 * self._level)
    @property
    def status_effects(self):
        return self._status_effects
    @property
    def max_ap(self) -> None:
        """
        Returns max AP value
        """
        return self._max_ap
    @property
    def ap(self) -> None:
        """
        Returns current Action Point value
        """
        return self._ap
    @property
    def can_act(self) -> bool:
        """
        Checks if the player can act (ie AP > 0)
        """
        return self._ap > 0

    #STATUS
    def bonus(self, stat) -> int:
        if isinstance(stat, str):
            return BONUS[self._stats[stat]]
        return BONUS[stat]
    
    def die(self) -> None:
        """
        Kils the player. Lose gold and inventory on death
        """
        self._gold = 0
        self._inventory = []
        #other stuff to be added
    def set_level_up_function(self, func) -> None:
        self._level_up_function = func

    def set_level(self, num:int) -> None:
        self._level = num

    def set_damage_multiplier(self, num:int) -> None:
        self._damage_multiplier = num

    def reset_damage_multiplier(self) -> None:
        self.set_damage_multiplier(0)


    #ROLLS
    def roll_attack(self) -> int:
        """
        Returns an attack roll (d20 + dex bonus)
        """
        roll = random.randrange(1,20)
        if roll == 1:
            return 1
        if roll == 20:
            return 0

        weapon:items.Weapon = self._equipped["Weapon"]
        if weapon.broken is True:
            raise ValueError("Weapon is broken")

        return roll + self.bonus(self.dex)
            
    def roll_damage(self) -> int:
        """
        Returns a damage roll (weapon dice + str bonus)
        """
        weapon:items.Weapon = self._equipped["Weapon"]
        weapon.lose_durability()
        weapon_damage = 0
        for _ in range(weapon.num_damage_dice):
            weapon_damage += random.randrange(1, weapon.damage_dice)
        return weapon_damage * self._damage_multiplier + self.bonus(self.str)

    def roll_a_check(self, stat: str) -> int:
        """
        Returns a check with a given stat (d20 + stat bonus)
        """
        return random.randrange(1, 20) + BONUS[self._stats[stat]]
    
    def take_damage(self, damage: int, armor_piercing=False) -> int:
        """
        Reduces the players hp by a damage amount, reduced by armor
        """
        if armor_piercing is True:
            self._hp -= damage
            return damage
        armor:items.Armor = self._equipped["Armor"]
        damage = damage * self._damage_taken_multiplier
        if armor.broken is False:
            armor.lose_durability()
            if damage - self.armor.armor_value < 0:
                return 0 
            else:
                self._hp -= damage - self.armor.armor_value
                return damage - self.armor.armor_value
        self._hp -= damage
        return damage

    def lose_hp(self, num:int) -> None:
        self._hp -= num

    #RESOURCES
    def spend_xp(self, stat: str) -> None:
        """
        Levels up a given stat
        """
        self._stats[stat] += 1
        self._xp -= 15 * self._level
        self._level += 1
        prev_max = self._max_hp
        self._max_hp += random.randrange(1, 8) + BONUS[self.con]
        if self._hp == prev_max:
            self._hp = self._max_hp
        if self._hp < (prev_max // 2):
            self._hp = self._max_hp // 2

    def gain_xp(self, xp: int) -> None:
        """
        Increases player XP by a given amount
        """
        if xp <= 0:
            return None
        global_commands.type_text(f"{xp} XP earned.")
        self._xp += xp

        if self.level_up is True:
            self._level_up_function()
    
    def gain_gold(self, gold:int, silently:bool=False) -> None:
        """
        Increases player gold by a given amount
        """
        if gold <= 0:
            return None
        if silently is False:
            global_commands.type_text(f"{gold} Gold gained.\n")
        self._gold += gold

    def spend_gold(self, gold:int) -> bool:
        """
        Reduces player gold by a given amount

        Throws a value error if the player doesnt have enough gold to spend
        """
        if gold > self.gold:   
            return False
        self._gold -= gold
        #print(f" {gold} gold spent. {self._gold} gold remaining.\n")
        return True

    def lose_gold(self, amount:int) -> None:
        """
        Takes a certain amount of gold from the player, if the player doesnt
        have sufficient gold, sets gold to 0
        """
        
        if self._gold - amount >= 0:
            self._gold -= amount
            return amount
        else:
            all_i_have = self._gold
            self._gold = 0
            return all_i_have

    def spend_ap(self, num=1) -> None:
        """
        Spends Action points equal to num
        """
        self._ap -= num

    def reset_ap(self) -> None:
        """
        Resets Action Points to max
        """
        self._ap = self._stats["ap"]

    def change_name(self, name:str) -> None:
        self._name = name

    def heal(self, healing: int) -> None:
        """
        Heals the player for a given amount
        """
        if self._hp <= (self._max_hp - healing):
            self._hp += healing
            global_commands.type_text(f"You healed {healing} HP.")
            return None
        if self._hp + healing > self._max_hp:
            self._hp = self._max_hp
            if self._max_hp == self._hp:#if you were lready full HP, say nothing
                return None
            global_commands.type_text(f"You only healed {self._max_hp - self._hp} HP.")
            return None


    #INVENTORY STUFF
    def pick_up(self, item: items.Item | items.Consumable, silently:bool = False) -> bool:
        """
        Picks up an item if the player has inventory space for it
        """
        if item is None:
            return False
        if self.current_weight <= self.carrying_capacity and self.can_carry(item):
            if self.has_item(item) is True and item.is_consumable is True:
                index = self.find_consumable_by_id(item)
                held_item:items.Consumable = self._inventory[index]
                held_item.increase_quantity(item.quantity)
                if silently is False:
                    print(held_item.pickup_message)
                return True
            self._inventory.append(item)
            item.set_owner(self)
            if silently is False:
                print(item.pickup_message)
            return True
        else:
            if silently is False:
                global_commands.type_text("Not enough inventory space\n")
        
    def drop(self, item: items.Item) -> None:
        """
        Drops an item out of the player's inventory
        """
        if item.id in self._inventory:
            self._inventory.remove(item)
            item.set_owner(None)
        else:
            raise ValueError("Can't drop an item you don't have.\n")

    def equip(self, item: "items.Item", silently=False) -> bool:
        """
        Equips the player with a given weapon
        """
        if item.type in self._equipped:
            if self._equipped[item.type] is not None and self._equipped[item.type].id != item.id:#if its not none and not the same item, swap it to inventory
                self._inventory.append(self._equipped[item.type])
            if item in self._inventory:
                self._inventory.remove(item)
            if silently is False:
                print(f" {item.name} equipped.")
            if item.type == "Armor":
                self.equip_armor(item)
                return True
            self._equipped[item.type] = item
            return True
        return False

    def equip_armor(self, armor: "items.Armor") -> None:
        """
        Same as above but for armor
        """
        self._equipped["Armor"] = armor

        if self.bonus("str") + 1 < armor.numerical_weight_class:
            armor_debuff = status_effects.Player_Stat_Debuff(armor, self)#armor is src, self is target
            armor_debuff.set_stat("dex")
            armor_debuff.set_id("Maximum Dexterity Bonus")#placeholder id --> just a flag to find and remove it when equipped armor changes
            armor_debuff.set_potency((armor.numerical_weight_class - 2))
            armor_debuff.set_duration(1000000000000)
            self.add_status_effect(armor_debuff, True)
            self._stats["evasion"] = 9 + self.bonus("dex")

    def can_carry(self, item:items.Item) -> bool:
        """
        Checks if the player can carry item 

        Returns True if they can, False if not
        """
        return self.current_weight + item.total_weight <= self.carrying_capacity

    def has_item(self, item: items.Item) -> bool:
        """
        Checks if a player has an item in their inventory

        Return the item if its there and False if not
        """

        if item is None:
            return False

        if item.is_consumable is True:
            for entry in self._inventory:
                held_item:items.Consumable = entry
                if held_item.id == item.id:
                    return True
            return False
        if item in self._inventory:
            return True
        return False
    
    def find_item_by_name(self, name:str) -> items.Item:
        """
        Finds an item in the player's inventory by it's name

        Returns the item, None if not found
        """
        for entry in self._inventory:
            held_item: items.Item = entry
            if held_item.name == name:
                return entry
            
        return None

    def print_inventory(self) -> None:
        """
        Prints the contents of the player's inventory
        """
        for idx, item in enumerate(self._inventory):
            print(f" {idx+1}. {item}")

        print(f"Carrying Capacity: {self.current_weight}/{self.carrying_capacity}")

    def recieve_reward(self, reward:dict) -> None:
        for entry in reward:
            match entry:
                case "gold":
                    self.gain_gold(reward[entry])
                case "xp":
                    self.gain_xp(reward[entry])
                case "drop":
                    for item in reward[entry]:
                        self.pick_up(item)        
        return None

    #STATUS EFFECTS / MODIFY STAT FUNCTIONS#
    def add_status_effect(self, effect:"status_effects.Status_Effect", silent=False) -> None:
        """
        Adds a status effect to the player's status effect list
        and changes the corresponding stat
        """
        if effect.id not in self._status_effects:
            self._status_effects[effect.id] = effect
            if silent is True:
                effect.set_message("")
            effect.apply()
            self.update_stats()
        else:
            self._status_effects[effect.id] = effect
        return None

    def remove_status_effect(self, effect:"status_effects.Status_Effect") -> bool:
        if effect.id in self._status_effects:
            del self._status_effects[effect.id]
            effect.cleanse()
            return True
        else:
            raise ValueError("Stat to be removed cannot be found")

    def update(self) -> None:
        removed = []
        self.reset_ap()
        self.update_stats()
        for entry in self._status_effects:
            effect:status_effects.Status_Effect = self._status_effects[entry]
            effect.update()
            if effect.active is False:
                #removes effect
                removed.append(effect)
                #break

        for effect in removed:
            self.remove_status_effect(effect)

    def update_stats(self) -> None:
        """
        Updates player stats seperately
        """
        self._damage_multiplier = self._stats["damage-multiplier"]
        self._damage_taken_multiplier = self._stats["damage-taken-multiplier"]

    def save_to_dict(self) -> dict:
        player_tod = {
            "name": self._name,
            "level": self._level
        }
        for stat in self._stats:
            player_tod[stat] = self._stats[stat]
        player_tod["max_hp"] = self._max_hp
        player_tod["xp"] = self._xp
        player_tod["gold"] = self._gold 
        player_tod["story_index"] = self.story_index

        return player_tod
    
    def load(self, stats_file, inventory_file) -> None:
        #set values to save file values
        with open(stats_file, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                self._name = row["name"]
                self._level = int(row["level"])
                for i in range(2, 11):#magic number, the range of 
                #loaded values that corresponds to the player's stats dictionary
                    key = list(row.keys())[i]
                    self._stats[key] = int(row[key])
                self._max_hp = int(row["max_hp"])
                self._hp = int(row["hp"])
                self._xp = int(row["xp"])
                self._ap = int(row["ap"])
                self._gold = int(row["gold"])
                self.story_index = int(row["story_index"])

        self.load_inventory(inventory_file)
    
    def load_inventory(self, filename) -> None:
        self._inventory = []
        size = 0
        with open(filename, encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                size += 1
            file.close()
        with open(filename, encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for idx, row in enumerate(reader):
                if row["type"] in ITEM_TYPES:
                    item:items.Item = ITEM_TYPES[row["type"]](row["id"])
                    item.save()
                    with open("temp.csv", "w", newline='') as temp_file:
                        temp_file.truncate(0)
                        w = csv.DictWriter(temp_file, fieldnames=list(item.tod.keys()))
                        w.writeheader()
                        w.writerow(row)
                        temp_file.close()

                    item.load("temp.csv")
                if idx == size - 2 or idx == size - 1:#if item is equipped weapon or armor
                    print(f"equipping{item}")
                    self.equip(item, True)
                else:
                    print(idx, item)
                    self.pick_up(item, True)
            file.close()

        if os.path.exists("temp.csv"):
            os.remove("temp.csv")
        else:
           pass

# arush wrote this while drunk, he won't let me delete it
class bitch(Event):
    def __init__(self, num_bitches: int):
        var: str = "bitch"
        self.bitches = num_bitches
        return f"miles has {self.bitches} {var}s"
