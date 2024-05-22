import random
import csv
import global_commands
import status_effects

RARITY = {
    "Common": 1,
    "Uncommon": 2,
    "Rare": 3,
    "Epic": 4,
    "Legendary": 5,
    "Unique": 6 
}

WEIGHT_CLASS = {
    "None": 0,
    "Light": 2,
    "Medium": 4,
    "Heavy": 6,
    "Superheavy": 8
}

def numerical_rarity_to_str(rare:int):
    return list(RARITY.keys())[rare-1]

class Item():

    def __init__(self, id:str, rarity=None):
        """
        Init function for the base Item class

        id = the item's rarity + item's name
        rarity = rarity as a string (ie common, uncommon, etc)
        numerical_rarity = rarity as an integer value, used in calculations
        name property = the item's name without rarity tag attached
        (
            ie. 'Uncommon Sword'[id] vs 'Sword'[name]
        )
        """
        self._id = id
        self._name = id
        if rarity is None:
            self._rarity = global_commands.generate_item_rarity()
        else:
            self._rarity = rarity
        self._numerical_rarity = RARITY[self._rarity]
        self._value = 10 * self._numerical_rarity
        self._max_durability = 10 * self._numerical_rarity
        self._durability = self._max_durability
        self._is_consumable = False
        self._weight = 0
        self._pickup_message = f"You picked up a {self._id}."
        self._description = ""
        self._broken = False
        self._type = "Item"

        self._owner = None

        self._tod = {}
    #properties
    @property
    def id(self) -> str:
        return f"{self._rarity} {self._id}"
    @property
    def name(self) -> str:
        return self._name
    @property
    def value(self) -> int:
        return self._value
    @property
    def total_value(self) -> int:
        return self._value
    @property
    def owner(self) -> int:
        return self._owner
    @property
    def broken(self) -> bool:
        return self._durability <= 0
    @property
    def durability(self) -> tuple[int, int]:
        return (self._durability, self._max_durability)
    @property
    def rarity(self) -> str:
        return self._rarity
    @property
    def numerical_rarity(self) -> int:
        return self._numerical_rarity
    @property
    def stats(self):
        raise NotImplementedError
    @property
    def is_consumable(self) -> bool:
        return self._is_consumable
    @property
    def weight(self) -> int:
        return self._weight
    @property
    def quantity(self) -> int:
        return self._quantity
    @property
    def total_weight(self) -> int:
        return self._weight
    @property
    def pickup_message(self) -> str:
        return self._pickup_message
    @property
    def description(self) -> str:
        return self._description
    @property
    def broken(self) -> bool:
       return self._durability <= 0
    @property
    def type(self) -> str:
        return self._type
    @property
    def pickup_message(self) -> str:
        return self._pickup_message
    @property
    def tod(self) -> dict:
        return self._tod
    #methods
    def lose_durability(self) -> None:
        prob = random.randrange(100)
        #weapon only loses durability occasionally, probability decreases with rarity
        if prob < (60 // self._numerical_rarity):
            self._durability -= 1
            if self.broken is True:
                self.item_has_broken()

    def remove_durability(self, num:int) -> None:
        self._durability -= num
        if self.broken is True:
            self._durability = 0
            self.item_has_broken()

    def repair(self) -> None:
        """
        Repairs weapon, returning its current durability to max value
        """
        self._durability = self._max_durability

    def set_weight(self, num:int) -> None:
        self._weight = num

    def set_stats(self, stats: tuple[int, int, int]):
        raise NotImplementedError

    def set_pickup_message(self, msg:str) -> None:
        self._pickup_message = msg

    def item_has_broken(self) -> None:
        print(f"Your {self._id} has broken!")
    
    def set_description(self, words:str) -> None:
        self._description = words

    def set_owner(self, owner) -> None:
        self._owner = owner

    def update(self) -> None:
        """
        Recalculates numerical rarity, value and max durability
        Only intended to be used after loading an item from
        a save file
        """
        self._numerical_rarity = RARITY[self._rarity]
        self._value = 10 * self._numerical_rarity
        self._max_durability = 10 * self._numerical_rarity

    def save(self) -> dict:
        self._tod = {
            "type": self._type,
            "id": self._id,
            "name": self._id,
            "rarity": self._rarity,
            "durability": self._durability,
        }
        #weapons special stats
        self._tod["damage_dice"] = None
        self._tod["num_damage_dice"] = None
        self._tod["crit"] = None
        #armor special stats
        self._tod["weight_class"] = None
        #consumable special stats
        self._tod["quantity"] = None
        self._tod["unit_weight"] = None
        self._tod["unit_value"] = None

    def load(self, stats_file) -> None:
        with open(stats_file, encoding = 'utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                self._id = row["id"]
                self._name = row["name"]
                self._type = row["type"]
                self._rarity = row["rarity"]
                self._durability = int(row["durability"])
            file.close()
        self.update()

    def __str__(self) -> str:
        return f"{self.id}\n Rarity: {self._rarity}\n Value: {self._value}g\n Durability: {self._durability}/{self._max_durability}\n"

class Weapon(Item):

    def __init__(self, id, rarity=None):
        super().__init__(id, rarity)
        self._value = 15 * self._numerical_rarity
        self._max_durability = 10 * self._numerical_rarity
        self._durability = self._max_durability
        self._damage_dice = 0
        self._num_damage_dice = 0
        self._crit = 0
        self._type = "Weapon"

    #properties
    @property
    def damage_dice(self) -> int:
        """
        Returns damage dice
        """
        return self._damage_dice
    @property
    def num_damage_dice(self) -> int:
        return self._num_damage_dice
    @property
    def stats(self) -> int:
        return f"{self._num_damage_dice}d{self._damage_dice}, x{self._crit}"
    @property
    def crit(self) -> int:
        return self._crit
    @property
    def type(self) -> str:
        return self._type
    
    def set_stats(self, statblock: str):
        """
        Sets a weapons stats based on a tuplized statblock

        Returns nothing
        """
        #finds the index of each piece of info
        num_idx = statblock.index('d')
        num = eval(statblock[0:num_idx])
        dice_idx = statblock.index(",")
        dice = eval(statblock[num_idx+1: dice_idx])
        crit = eval(statblock[dice_idx+2: len(statblock)])

        #sets the appropriate stats
        self.set_damage_dice((num, dice))
        self.set_crit_multiplier(crit)
        self._weight = int(2.5 * self._num_damage_dice + (self._damage_dice // 2))

    def set_damage_dice(self, dice:tuple[int,int]) -> None:
        num, type = dice
        self._damage_dice = type
        self._num_damage_dice = num

    def set_crit_multiplier(self, crit)->None:
        self._crit = crit

    def update(self) -> None:
        self._value = 15 * self._numerical_rarity
        self._max_durability = 10 * self._numerical_rarity
        self._weight = int(2.5 * self._num_damage_dice + (self._damage_dice // 2))

    def save(self) -> dict:
        super().save()
        self._tod["damage_dice"] = self._damage_dice
        self._tod["num_damage_dice"] = self._num_damage_dice
        self._tod["crit"] = self._crit

    def load(self, stats_file, ) -> None:
        super().load(stats_file, )
        with open(stats_file, encoding = 'utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                self._damage_dice = int(row["damage_dice"])
                self._num_damage_dice = int(row["num_damage_dice"])
                self._crit = int(row["crit"])
            file.close()
        self.update()
    
    def __str__(self) -> str:
        return (f"""{self.id}\n Value: {self._value}g\n Durability: {self._durability}/{self._max_durability}\n Damage Dice: {self._num_damage_dice}d{self._damage_dice}\n Weight: {self.weight} lbs\n""")


class Armor(Item):

    def __init__(self, id, weight_class:int="Light", rarity=None):
        super().__init__(id, rarity)
        self._weight_class = weight_class
        self._numerical_weight_class = WEIGHT_CLASS[self._weight_class]
        self._armor_value = int(self._numerical_weight_class + self._numerical_rarity - (self._numerical_weight_class / 2))
        self._value = (25 * self._numerical_rarity) + (10 * self.numerical_weight_class)
        self._broken = False
        self._type = "Armor"

    #properties
    @property
    def armor_value(self) -> int:
        """
        Return the value of the armor
        """
        return self._armor_value
    @property
    def stats(self) -> str:
        return f"{self.weight_class}, {self.armor_value}P"
    @property
    def weight_class(self) -> str:
        return self._weight_class
    @property
    def numerical_weight_class(self) -> int:
        return self._numerical_weight_class

    #methods
    def set_armor_value(self, armor) -> None:
        self._armor_value = armor

    def set_stats(self, stats) -> None:
        """
        Sets armor weight class and armor value (if given),
        then re-calculates value and armor value as necessary
        """
        if stats is None or len(stats) == 0:
            return None

        weight, armor = stats
        self._weight_class = weight
        self._numerical_weight_class = WEIGHT_CLASS[self._weight_class]
        if armor is not None:
            self.set_armor_value(armor)
        else:
            self.set_armor_value(int(self._numerical_weight_class + self._numerical_rarity - (self._numerical_weight_class / 2)))
        self._value = (25 * self._numerical_rarity) + (10 * self.numerical_weight_class)
        self._weight = (10 * self._numerical_weight_class) + self._armor_value

    def update(self) -> None:
        super().update()
        self._numerical_weight_class = WEIGHT_CLASS[self._weight_class]
        self._armor_value = int(self._numerical_weight_class + self._numerical_rarity - (self._numerical_weight_class / 2))
        self._value = (25 * self._numerical_rarity) + (10 * self.numerical_weight_class)

    def save(self) -> dict:
        super().save()
        self._tod["weight_class"] = self._weight_class

    def load(self, stats_file) -> None:
        super().load(stats_file)
        with open(stats_file, encoding = 'utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                self._weight_class = row["weight_class"]
            file.close()
        self.update()

    def __str__(self) -> str:
        return f"{self.id}\n Weight: {self.weight_class}\n Rarity: {self._rarity}\n Value: {self._value}g\n Durability: {self._durability}/{self._max_durability}\n Armor Value: {self._armor_value}\n"

class Consumable(Item):

    def __init__(self, id:str, rarity="Common",quantity:int=0):
        super().__init__(id, rarity)
        self._quantity = quantity
        self._strength = self._numerical_rarity * 2
        self._is_consumable = True
        self._type = "Consumable"
        self._target = None
        self._unit_weight = 1
        self._unit_value = 8 * self._numerical_rarity
        self._value = self._unit_value * self._quantity

    #properties
    @property
    def quantity(self) -> int:
        return self._quantity
    @property
    def stats(self) -> str:
        return self._quantity
    @property
    def weight(self) -> int:
        return self._unit_weight
    @property
    def value(self) -> int:
        return self._unit_value
    @property
    def target(self):
        return self._target

    #methods
    def use(self, target):
        raise ValueError("Unimplemented")

    def increase_quantity(self, num:int) -> None:
        self._quantity += num
        self.update()

    def decrease_quantity(self, num:int) -> None:
        self._quantity -= num
        self.update()
    
    def set_quantity(self, num:int) -> None:
        self._quantity = num
        self.update()
    
    def set_target(self, tar) -> None:
        self._target = tar

    def update(self) -> None:
        if self._quantity > 1:
            self._pickup_message = f"You picked up {self._quantity} {self._name}."
            self._name = self._id +"s"
        else:
            self._pickup_message = f"You picked up a {self._id}."
            if self._name[-1] == "s":
                self._name = self._name.rstrip(self._name[-1])

        self._value = self._unit_value * self._quantity
        self._weight = self._unit_weight * self._quantity

    def save(self) -> dict:
        super().save()
        self._tod["quantity"] = self._quantity
        self._tod["unit_weight"] = self._unit_weight
        self._tod["unit_value"] = self._unit_value

    def load(self, stats_file) -> None:
        super().load(stats_file)
        with open(stats_file, encoding = 'utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                self._quantity = int(row["quantity"])
                self._unit_weight = float(row["unit_weight"])
                self._unit_value = float(row["unit_value"])
            file.close()
        self.update()

    def __str__(self) -> str:
        return f"{self.id}\n Rarity: {self._rarity}\n Value: {self._unit_value}g/each\n Quantity: {self._quantity}\n"
    
class Health_Potion(Consumable):

    def __init__(self, id="Health Potion", rarity="Common", quantity=0):
        super().__init__(id, rarity, quantity)
        self._unit_weight = 0.5
        self._target = status_effects.PLAYER
        self._type = "Health_Potion"

    def use(self, target=None) -> bool:
        """
        Heals the target for a given amount
        """
        if self._target.hp < self._target.max_hp:
            self.decrease_quantity(1)
            global_commands.type_with_lines(f"{self.id} used. {self._quantity} remaining.\n")
            self._target.heal(self._strength*2)
            self._owner.spend_ap(1)
            return True
        global_commands.type_with_lines("You are already full HP.")
        return False
    
class Repair_Kit(Consumable):

    def __init__(self, id="Repair Kit", rarity="Uncommon", quantity=0):
        super().__init__(id, rarity, quantity)
        self._unit_value = 10 * self._numerical_rarity
        self._unit_weight = .5
        self._type = "Repair_Kit"

    def use(self, target: Item) -> bool:
        """
        Repairs the item to full durability
        """
        if target.durability[0] < target._durability[1]:#ie item is damaged
            self.decrease_quantity(1)
            global_commands.type_with_lines(f"{self.id} used. {self._quantity} remaining.\n")
            target.repair()
            return True
        return False

class Firebomb(Consumable):
    
    def __init__(self, id="Firebomb", rarity="Uncommon", quantity=0):
        super().__init__(id, rarity, quantity)
        self._unit_value = 20 * self._numerical_rarity
        self._unit_weight = 1 
        self._target = None
        self._damage = self._strength
        self._type = "Firebomb"

    def use(self, target=None):
        self._target = target
        throw = self._owner.roll_a_check("dex")
        dodge = target.roll_a_check("dex")

        self._owner.spend_ap()
        self._quantity -= 1

        global_commands.type_with_lines(f"You throw a {self._id} at the {self._target.id}.\n")

        if dodge >= throw + 10:
            global_commands.type_text(f"The {self._target.id} dodged your {self._id} entirely!")
            return True
        
        if dodge >= throw:
            global_commands.type_text(f"The {self._target.id} partially dodged your {self._id}.\n")
            taken = self._target.take_damage(int(self._damage / 2))
            if global_commands.probability(50 - dodge): #--> if statement is a formattting thing the message doesn't change 
                global_commands.type_text(f"The {self._id} did {taken} damage to the {self._target.id}.\n")
                self.set_on_fire()
            else:
                global_commands.type_text(f"The {self._id} did {taken} damage to the {self._target.id}.")
            return True
        
        if throw > dodge:
            global_commands.type_text(f"You hit the {self._target.id}.\n")
            taken = self._target.take_damage(int(self._damage))
            if global_commands.probability(75):#--> if statement is a formattting thing the message doesn't change 
                global_commands.type_text(f"Your {self._id} did {taken} damage to the {self._target.id}.\n")
                self.set_on_fire()
            else:
                global_commands.type_text(f"Your {self._id} did {taken} damage to the {self._target.id}.")
            return True

    def set_on_fire(self) -> None:
        if self.target == None:
            firebomb = status_effects.Player_On_Fire(self._owner)
        else:
            firebomb = status_effects.On_Fire(self._owner, self._target)
        firebomb.set_duration(3)
        firebomb.set_potency(self._numerical_rarity)
        self._target.add_status_effect(firebomb)
       
    def update(self) -> None:
        super().update()
        self._damage = self._strength
        self._unit_value = 20 * self._numerical_rarity
        self._unit_weight = 1