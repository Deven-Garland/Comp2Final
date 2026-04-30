"""
subcharacter.py - Character classes

Different character types that players can choose from
"""

import pygame
from character import Character

class WaterScarab(Character):
    """Water Scarab - Hapi's manifestation"""
    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id, is_local)
        self.character_name = "WaterScarab"
        self.hp, self.max_hp = 500, 500
        self.attack, self.defense = 200, 300
        self.speed = 5

        try:
            self.image = pygame.image.load('../graphics/characters/WaterScarab.png').convert_alpha()
            self.rect = self.image.get_rect(topleft=pos)
            self.hitbox = self.rect.inflate(0, -26)
        except:
            pass

        self.import_player_assets(animate=True)

    @staticmethod
    def get_display_name():
        return "Water Scarab"

    @staticmethod
    def get_description():
        return "manifestation of Hapi's power, player obtains the Secrets of the Nile and it's Gods, only unlocked after completing Hapi's side mission when he's resurrected"

    @staticmethod
    def get_preview_image():
        return '../graphics/characters/WaterScarab.png'


class SkyScarab(Character):
    """Sky Scarab - Nut's manifestation"""
    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id, is_local)
        self.character_name = "SkyScarab"
        self.hp, self.max_hp = 500, 500
        self.attack, self.defense = 400, 100
        self.speed = 2

        try:
            self.image = pygame.image.load('../graphics/characters/SkyScarab.png').convert_alpha()
            self.rect = self.image.get_rect(topleft=pos)
            self.hitbox = self.rect.inflate(0, -26)
        except:
            pass

        self.import_player_assets(animate=True)

    @staticmethod
    def get_display_name():
        return "Sky Scarab"

    @staticmethod
    def get_description():
        return "manifestation of Nut's power, only unlocked if player finds the Sun & Moon amulets hidden in the map"

    @staticmethod
    def get_preview_image():
        return '../graphics/characters/SkyScarab.png'


class BattleScarab(Character):
    """Battle Scarab - Sekhmet's manifestation"""
    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id, is_local)
        self.character_name = "BattleScarab"
        self.hp, self.max_hp = 700, 700
        self.attack, self.defense = 400, 200
        self.speed = 5

        try:
            self.image = pygame.image.load('../graphics/characters/BattleScarab.png').convert_alpha()
            self.rect = self.image.get_rect(topleft=pos)
            self.hitbox = self.rect.inflate(0, -26)
        except:
            pass

        self.import_player_assets(animate=True)

    @staticmethod
    def get_display_name():
        return "Battle Scarab"

    @staticmethod
    def get_description():
        return "manifestation of Sekhmet's ability, unlocked when one weapen is upgraded to maximum level"

    @staticmethod
    def get_preview_image():
        return '../graphics/characters/BattleScarab.png'


class DeathScarab(Character):
    """Death Scarab - Anubis's manifestation"""
    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id, is_local)
        self.character_name = "DeathScarab"
        self.hp, self.max_hp = 600, 600
        self.attack, self.defense = 900, 100
        self.speed = 8

        try:
            self.image = pygame.image.load('../graphics/characters/DeathScarab.png').convert_alpha()
            self.rect = self.image.get_rect(topleft=pos)
            self.hitbox = self.rect.inflate(0, -26)
        except:
            pass

        self.import_player_assets(animate=False)

    @staticmethod
    def get_display_name():
        return "Death Scarab"

    @staticmethod
    def get_description():
        return "manifestation of Anubis's ability, only unlocked if players manages to kill the entire Sea People army"

    @staticmethod
    def get_preview_image():
        return '../graphics/characters/DeathScarab.png'


def get_all_character_classes():
    """Auto-discover all character classes"""
    character_classes = []
    for cls in Character.__subclasses__():
        if cls.__name__ != 'Character':
            character_classes.append(cls)
    return character_classes