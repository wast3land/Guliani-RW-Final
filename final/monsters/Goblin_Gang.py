#Goblin Gang mob file
import random
import mob, player, global_commands

class Goblin_Gang(mob.Mob):
    def __init__(self, id="Goblin Gang", level = (2,6)):
        super().__init__(id, level)
        self._stats = {
            "str": 14,
            "dex": 10,
            "con": 14,
            "int": 8,
            "wis": 10,
            "cha": 7,
        }

        self._max_hp = 7 + self.bonus("con")
        self._hp = self._max_hp

        self._stats["evasion"] = 6

        self._damage = 5

        self._loot = {
            "gold": 20,
            "xp": 10,
            "drops": None
        }

        self._flee_threshold = 10

        self.update()

    def special(self) -> bool:
        return False

object = Goblin_Gang