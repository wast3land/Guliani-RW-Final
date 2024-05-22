#status effects file
import random
import global_commands

PLAYER = None

class Status_Effect():

    def __init__(self, src, target, id):
        #SRC is a player or mob object
        self._id = id
        self._src = src
        self._target = target
        self._potency = 1
        self._duration = 0
        self._message:str = ""
        self._cleanse_message:str = ""
        self._cleanse_stat = None
        self._active = True

    #properties
    @property
    def id(self) -> str:
        return self._id
    @property
    def src(self):
        return self._src
    @property
    def potency(self) -> int:
        return self._potency
    @property
    def duration(self) -> int:
        return self._duration
    @property
    def target(self):
        return self._target
    @property
    def message(self):
        return self._message
    @property
    def active(self):
        return self._active
    @property
    def cleanse_stat(self):
        return self._cleanse_stat
    
    #methods
    def update(self) -> None:
        self._duration -= 1
        if self._duration <= 0:
            self._duration = 0
            self._active = False

    def apply(self) -> None:
        """
        Types the effect's apply message
        """
        global_commands.type_text(self._message)

    def set_potency(self, num:int) -> None:
        self._potency = num

    def set_duration(self, num:int) -> None:
        self._duration = num

    def set_message(self, msg:str) -> None:
        self._message = msg

    def set_cleanse_message(self, msg:str) -> None:
        self._cleanse_message = msg
    
    def set_id(self, id:str="") -> None:
        self._id = id

    def set_target(self, tar):
        self._target = tar

    def cleanse(self) -> None:
        """
        Sets the effect's duration to 0, and
        sets the effect's active property to False and
        types the effect's cleans message
        """
        self._duration = 0
        self._active = False
        global_commands.type_text(self._cleanse_message)
        return None

    def attempt_cleanse(self, roll:int = 0):
        raise NotImplementedError

class On_Fire(Status_Effect):

    def __init__(self, src, target, id="On Fire"):
        super().__init__(src, target, id)
        self._message = f"The {self._target.id} is now {id}."
        self._cleanse_message = f"The {self._target.id} is not longer {id}.\n"
    
    def update(self):
        self._duration -= 1

        taken = self._target.take_damage(self._potency, True)

        global_commands.switch(self._target.header, f"The {self._target.id} took {taken} damage from from the fire.\n")
        self._target.set_header(True)

        if self._duration <= 0:
            self._active = False

    
class Player_On_Fire(On_Fire):
    """
    On Fire Status effect, but only applied to the PLAYER
    """
    def __init__(self, src, target=PLAYER, id="On Fire"):
        super().__init__(src, target, id)
        self._message = f"You are now {id}."
        self._cleanse_message = f"You are not longer {id}."

    def attempt_cleanse(self) -> bool:
        global_commands.type_text(" You put out the fire.\n")
        return self._target.remove_status_effect(self)

class Stat_Buff(Status_Effect):

    def __init__(self, src, target, id="Buff"):
        super().__init__(src, target, id)
        self._stat = ""
        self._id = self._stat +" " + id

    @property
    def stat(self) -> str:
        return self._stat

    def set_stat(self, stat:str) -> None:
        if self._target is None:
            self._target = PLAYER
        self._stat = stat
        self._id = stat + self._id
        self._message = f"The {self._target.id}'s {global_commands.TAG_TO_STAT[self._stat]} increased by {self._potency}."
        self._cleanse_message = f"The {self._target.id}'s {global_commands.TAG_TO_STAT[self._stat]} has returned to normal."

    def apply(self):
        super().apply()
        self._target.stats[self._stat] += self._potency

    def cleanse(self) -> None:
        self._target.stats[self._stat] -= self._potency
        super().cleanse()

class Stat_Debuff(Stat_Buff):
    def __init__(self, src, target, id="Debuff"):
        super().__init__(src, target, id)

    def apply(self):
        super().apply()
        self._target.stats[self._stat] -= self._potency

    def set_stat(self, stat: str) -> None:
        super().set_stat(stat)
        self._message = f"The {self._src.id}'s {self._stat} is being decreased by {self._potency} by the {self._src.id}'s {self._id}."

class Player_Stat_Buff(Stat_Buff):
    """
    Stat buff class only to be applied to PLAYER
    """
    def __init__(self, src, target=PLAYER, id="Buff"):
        super().__init__(src, target, id)

    def set_stat(self, stat: str) -> None:
        if self._target is None:
            self._target = PLAYER
        super().set_stat(stat)
        self._message = f"Your {global_commands.TAG_TO_STAT[self._stat]} is being increased by {self._potency} by the {self._src}'s {self._id}."
        self._cleanse_message = f"Your {global_commands.TAG_TO_STAT[self._stat]} has returned to normal."

class Player_Stat_Debuff(Player_Stat_Buff):
    """
    Stat debuff class only to be applied to PLAYER
    """
    def __init__(self, src, target=PLAYER, id="Debuff"):
        super().__init__(src, target, id)

    def set_stat(self, stat: str) -> None:
        super().set_stat(stat)
        self._message = f"Your {global_commands.TAG_TO_STAT[self._stat]} is being decreased by {self._potency} by the {self._src.id}'s {self._id}."
        self._cleanse_message = f"Your {global_commands.TAG_TO_STAT[self._stat]} has returned to normal."

class Player_Entangled(Status_Effect):

    def __init__(self, src, target, id="Entangled"):
        super().__init__(src, target, id)
        self._stat = "ap"
        self._message = f"You are now {id}."
        self._cleanse_message = f"You are no longer {id}."
        self._cleanse_stat = "str"

    def apply(self):
        super().apply()
        self._target.stats[self._stat] -= self._potency

    def cleanse(self):
        self._src._applied_status_effects.remove(self)
        self._target.stats[self._stat] += self._potency
        super().cleanse()

    def attempt_cleanse(self, roll: int = 0) -> bool:
        global_commands.type_with_lines("You try to break free of your entanglement...\n")
        if roll >= self._src.dc - 2:
            global_commands.type_text("You succeed!\n")
            return self._target.remove_status_effect(self)
        global_commands.type_text("You failed.\n")
        return False

class Vulnerable(Stat_Buff):
    """
    Makes the target vulnerable,
    meaning they take x2 damage for the duration
    """
    def __init__(self, src, target, id="Vulnerable"):
        super().__init__(src, target, id)
        self._message = f"The {self._target.id} is now {self._id}."
        if src == target:
            self._message = f"The {self._target.id} made itself {self._id}."
        self._cleanse_message = f"The {self._target.id} is no longer {self._id}."
        self._stat = "damage-taken-multiplier"
        self._potency = 1# this is because the apply function adds to the stat,
        #so a potency of 2 would result in a damage-taken of 3, not 2 like we want

    def apply(self) -> None:
        super().apply()

class Player_Vulnerable(Vulnerable):
    """
    Makes the PLAYER vulnerable,
    meaning they take x2 damage for the duration
    """
    def __init__(self, src, target=PLAYER, id="Vulnerable"):
        super().__init__(src, target, id)
        self._message = f"You are now {self._id}."
        self._cleanse_message = f"You are no longer {self._id}."
