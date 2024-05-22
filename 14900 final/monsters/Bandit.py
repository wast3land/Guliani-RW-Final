#Bandit mob file
import random
import mob

class Bandit(mob.Mob):
    def __init__(self, id="Bandit", level = (2,7)):
        super().__init__(id, level)
        self._stats = {
            "str": 14,
            "dex": 12,
            "con": 12,
            "int": 14,
            "wis": 8,
            "cha": 10,
        }

        self._max_hp = 8 + self.bonus("con")
        self._hp = self._max_hp

        self._stats["evasion"] = 9

        self._damage = 5
        self._armor = 2
        self._loot = {
            "gold": 15,
            "xp": 8,
            "drops": None
        }

        self.update()

    def special(self) -> bool:
        return False

object = Bandit
