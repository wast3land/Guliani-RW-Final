#Clockwork Hound mob file
import mob, global_commands, items

class Clockwork_Hound(mob.Mob):
    def __init__(self, id="Clockwork Hound", level = (6,13)):
        super().__init__(id, level)
        self._stats = {
            "str": 16,
            "dex": 14,
            "con": 14,
            "int": 18,
            "wis": 10,
            "cha": 8,
        }

        self._max_hp = 12 + self.bonus("con")
        self._hp = self._max_hp

        self._stats["evasion"] = 10

        self._damage = 8
        self._armor = 3
        self._loot = {
            "gold": 30,
            "xp": 15,
            "drops": []
        }

        if global_commands.probability(50):
            scrap:items.Item = items.Item("Clockwork Scrap", "Uncommon")
            scrap.set_weight(1.5)
            self._loot["drops"].append(scrap)

        if global_commands.probability(3):
            heart = items.Item("Clockwork Heart", "Epic")
            heart.set_weight(2)
            self._loot["drops"].append(heart)

        self.update()
    
    def trigger(self) -> None:
        return self._hp < self._max_hp / 2

    def special(self, target=None) -> bool:
        
        if target is None:
            raise ValueError("No Target.\n")
        
        weapon = target.equipped["weapon"]
        armor = target.equipped["armor"]

        meal:items.Item = weapon
        if weapon.durability < armor.durability:
            meal = armor
        
        if self.roll_attack() > target.evasion:
            #add print statements
            meal.remove_durability(self.bonus("str"))
            self.heal(self.bonus("str"))
        else:
            #add print statements
            pass

object = Clockwork_Hound
