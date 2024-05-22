#Goblin mob file
import random
import mob, global_commands

class Goblin(mob.Mob):
    def __init__(self, id="Goblin", level=(1,3)):
        super().__init__(id, level)
        self._stats = {
            "str": 10,
            "dex": 14,
            "con": 10,
            "int": 9,
            "wis": 7,
            "cha": 6,
        }

        self._max_hp = 5 + self.bonus("con")

        self._stats["evasion"] = 9

        self._damage = 5
        self._loot = {
            "gold": 10,
            "xp": 5,
            "drops": None
        }
    
    def trigger(self):
        """
        Conditions that trigger the mob's special
        move. 

        For the Goblin, if the player has more gold than
        it does.
        """
        return self._player.gold >= self._loot["gold"]

    def special(self) -> bool:
        """
        Rob: Steals a random amount of gold from the player if they fail a dex check
        """
        if self.trigger():
            self.spend_ap(1)
            global_commands.type_with_lines(f"The {self._id} makes a grab at your gold pouch.\n")
            if self._player.roll_a_check("dex") >= self.roll_attack():
                global_commands.type_text(" It missed.")
            else:
                prospective = random.randrange(1,20)
                actual = self._player.lose_gold(prospective)
                global_commands.type_text(f"The {self._id} stole {actual} gold from you!")
                self._loot["gold"] += actual
            return True
        return False

object = Goblin
