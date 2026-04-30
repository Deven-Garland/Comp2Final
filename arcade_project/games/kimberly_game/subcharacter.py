"""
character.py - Character classes with inventory

Lab 3 Update: Characters now have inventories using ArrayList!
"""

import pygame
from character import Character


class Character1(Character):
    def  __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id=player_id, is_local=is_local)
        self.character_name = "Technical Fighter"
        self.hp = self.max_hp = 180
        self.attack = 20
        self.defense = 15
        self.speed = 7
        self.import_player_assets()

    def special_ability(self):
        self.counter_ready = True

    @staticmethod
    def get_display_name():
        return "Technical Fighter"

    @staticmethod
    def get_description():
        return "A calm and calculated fighter who masters counters and control."

    @staticmethod
    def get_preview_image():
        return "../graphics/characters/technical_fighter.png"


class Character2(Character):
    def  __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id=player_id, is_local=is_local)
        self.character_name = "Mystic Warrior"
        self.hp = self.max_hp = 200
        self.attack = 17
        self.defense = 20
        self.speed = 9
        self.import_player_assets()

    def special_ability(self):
        self.attack += 7

    @staticmethod
    def get_display_name():
        return "Mystic Warrior"

    @staticmethod
    def get_description():
        return "Channels ancient energy through powerful martial techniques."

    @staticmethod
    def get_preview_image():
        return "../graphics/characters/mystic_warrior.png"


class Character3(Character):
    def  __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id=player_id, is_local=is_local)
        self.character_name = "Balanced Prodigy"
        self.hp = self.max_hp = 105
        self.attack = 15
        self.defense = 11
        self.speed = 8
        self.import_player_assets()

    def special_ability(self):
        self.attack += 2
        self.defense += 2
        self.speed += 1

    @staticmethod
    def get_display_name():
        return "Balanced Prodigy"

    @staticmethod
    def get_description():
        return "A rising fighter who adapts quickly to any opponent."

    @staticmethod
    def get_preview_image():
        return "../graphics/characters/balanced_prodigy.png"


class Character4(Character):
    def  __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id=player_id, is_local=is_local)
        self.character_name = "Heavy Enforcer"
        self.hp = self.max_hp = 200
        self.attack = 23
        self.defense = 18
        self.speed = 6
        self.unbreakable = False
        self.import_player_assets()

    def special_ability(self):
        self.unbreakable = True
        self.defense += 5

    @staticmethod
    def get_display_name():
        return "Heavy Enforcer"

    @staticmethod
    def get_description():
        return "A towering fighter who dominates space and shrugs off attacks."

    @staticmethod
    def get_preview_image():
        return "../graphics/characters/heavy_enforcer.png"


def get_all_character_classes():
    """Auto-discover all character classes"""
    character_classes = []
    for cls in Character.__subclasses__():
        if cls.__name__ != 'Character':
            character_classes.append(cls)
    return character_classes
