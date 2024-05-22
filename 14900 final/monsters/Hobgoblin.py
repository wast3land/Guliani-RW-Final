#Hobgoblin mob file
import random
import mob, player, global_commands
import status_effects

class Hobgoblin(mob.Mob):
    def __init__(self, id="Hobgoblin", level = (1,5)):
        super().__init__(id, level)
        self._stats = {
            "str": 12,
            "dex": 12,
            "con": 12,
            "int": 9,
            "wis": 7,
            "cha": 14,
        }

        self._max_hp = 6 + self.bonus("con")
        self._hp = self._max_hp
        self._stats["evasion"] = 8

        self._damage = 5
        self._armor = 1
        self._dc = 12 + self.bonus("cha")

        self._loot = {
            "gold": 8,
            "xp": 6,
            "drops": None
        }

        self.update()

    def trigger(self):
        """
        Conditions that trigger the mob's special
        move. 

        For Hobgoblin's it's if the player's evasion is over
        10, and that the Hobgoblin has not recently applied a
        status effect 
        """
        return self._player.evasion > 10 and len(self._applied_status_effects) == 0


    def special(self) -> bool:
        """
        Taunt: Reduces the player's evasion by 2 points for 2 turns if they fail a charisma check
        """
        if self.trigger():
            self.spend_ap()
            global_commands.type_with_lines(f"The {self.id} hurls enraging insults at you.\n")

            if self._player.roll_a_check("cha") >= self.dc:
                global_commands.type_text(f"Your mind is an impenetrable fortess. The {self.id}'s words have no effect.")

            else:
                if len(self._applied_status_effects) > 0:
                    return False
                global_commands.type_text(f"The {self.id}'s insults distract you, making you an easier target.\n")
                taunt = status_effects.Player_Stat_Debuff(self)
                taunt.set_stat("base-evasion")
                taunt.set_duration(3)
                taunt.set_potency(2)
                self._player.add_status_effect(taunt)
                self._applied_status_effects.add(taunt)
            return True
        return False 

object = Hobgoblin
