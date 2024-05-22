#Land Shark mob file
import random
import mob, player, global_commands
import status_effects
import items

class Land_Shark(mob.Mob):
    def __init__(self, id="Land Shark", level = (3,10)):
        super().__init__(id, level)
        self._stats = {
            "str": 15,
            "dex": 9,
            "con": 16,
            "int": 7,
            "wis": 7,
            "cha": 7,
        }

        self._max_hp = 10 + self.bonus("con")
        self._hp = self._max_hp
        self._stats["evasion"] = 8

        self._damage = 8
        self._armor = 3

        self._loot = {
            "gold": 15,
            "xp": 12,
            "drops": None
        }

        if global_commands.probability(3):
            tooth = items.Item("Land Shark Tooth", "Epic")
            tooth.set_weight(0.5)
            self._loot["drops"] = [tooth]

        self._burrowed = False

        self.update()

    def trigger(self):
        """
        Conditions that trigger the mob's special
        move. 

        For Hobgoblin's it's if the player's evasion is over
        10, and that the Hobgoblin has not recently applied a
        status effect 
        """
        if self._burrowed is True and len(self._status_effects) == 0:
            return True
        
        if global_commands.probability(abs(self._hp - self._max_hp) * 10):#higher HP == lower chance of burrowing
            return True
        
        return len(self._status_effects) > 0 and self._burrowed is False#if I have status effects and not burrowed, burrow

    def special(self) -> bool:
        """
        Burrow: increases evasion temporarily

        Erupt: can only be used when 'burrowed',
        doubles all damage done and taken after use, reverts evasion
        changes made by burrow 
        """
        if self.trigger() is True:
            if self._burrowed is False:#if not burrowed, burrow
                self.spend_ap(0) #indicates a full round action
                global_commands.switch(self.header, f"The {self._id} burrows underground, making it harder to hit.")
                self._evasion += 3
                self._burrowed = True
                return True
            else:
                self.spend_ap()
                #the text variable is so the formatting of the message can be dynamically altered
                #depending on what text will come next
                text = f"The {self._id} erupts from the ground."
                if "Vulnerable" not in self._status_effects:
                    text = text + "\n"
                global_commands.switch(self.header, text)
                self._evasion -= 3
                #double all damage taken for 3 turns
                vul = status_effects.Vulnerable(self, self)
                vul.set_duration(3)
                self.add_status_effect(vul)
                self._burrowed = False
                return True
        return False

object = Land_Shark
