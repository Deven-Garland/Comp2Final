"""
subcharacters.py - Character subclasses for Lab 3
"""

import pygame
from character import Character


class Knight(Character):
    """A heavily armored frontline fighter"""

    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id=player_id, is_local=is_local)

        self.character_name = "Knight"
        self.max_hp = 140
        self.hp = 140
        self.attack = 15
        self.defense = 20
        self.speed = 5

        self.import_player_assets(animate=False)

    def special_ability(self):
        print("Knight uses Shield Wall! Incoming damage is reduced.")

    @staticmethod
    def get_display_name():
        return "Knight"

    @staticmethod
    def get_description():
        return "A heavily armored frontline fighter."

    @staticmethod
    def get_preview_image():
        return '../../graphics/characters/knight.png'


class Ranger(Character):
    """A fast and agile ranged fighter"""

    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id=player_id, is_local=is_local)

        self.character_name = "Ranger"
        self.max_hp = 100
        self.hp = 100
        self.attack = 18
        self.defense = 10
        self.speed = 12

        self.import_player_assets(animate=False)

    def special_ability(self):
        print("Ranger uses Piercing Shot! The attack ignores some defense.")

    @staticmethod
    def get_display_name():
        return "Ranger"

    @staticmethod
    def get_description():
        return "A fast and agile ranged fighter."

    @staticmethod
    def get_preview_image():
        return '../../graphics/characters/ranger.png'


class Engineer(Character):
    """A tech-savvy fighter using machines and gadgets"""

    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id=player_id, is_local=is_local)

        self.character_name = "Engineer"
        self.max_hp = 110
        self.hp = 110
        self.attack = 14
        self.defense = 12
        self.speed = 8

        self.import_player_assets(animate=False)

    def special_ability(self):
        print("Engineer deploys a Turret! It fires automatically.")

    @staticmethod
    def get_display_name():
        return "Engineer"

    @staticmethod
    def get_description():
        return "A tech-savvy fighter using machines and gadgets."

    @staticmethod
    def get_preview_image():
        return '../../graphics/characters/engineer.png'


class Mystic(Character):
    """A magical support character using Aether energy"""

    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id=player_id, is_local=is_local)

        self.character_name = "Mystic"
        self.max_hp = 90
        self.hp = 90
        self.attack = 20
        self.defense = 8
        self.speed = 9

        self.import_player_assets(animate=False)

    def special_ability(self):
        print("Mystic unleashes Aether Surge!")

    @staticmethod
    def get_display_name():
        return "Mystic"

    @staticmethod
    def get_description():
        return "A magical support character using Aether energy."

    @staticmethod
    def get_preview_image():
        return '../../graphics/characters/mystic.png'


def get_all_character_classes():
    """Auto-discover all character classes"""
    character_classes = []

    for cls in Character.__subclasses__():
        if cls.__name__ != 'Character':
            character_classes.append(cls)

    return character_classes
