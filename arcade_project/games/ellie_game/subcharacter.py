"""
subcharacter.py - Character subclasses (Lab 04)

Lab 04 Update:
- constructors accept player_id and is_local
- paths are absolute based on this file's location
"""

import os
import pygame
from character import Character

# Base path for graphics — always points to the right folder
# regardless of where the game is launched from
GAME_DIR = os.path.dirname(os.path.abspath(__file__))
CHARS = os.path.join(GAME_DIR, "graphics", "characters", "characters")

class Character1(Character):
    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id=player_id, is_local=is_local)

        self.character_name = "eli"
        self.hp = 100
        self.max_hp = 100
        self.attack = 15
        self.defense = 10
        self.speed = 20
        self.skywarp_charges = 2

        self.image = pygame.image.load(os.path.join(CHARS, "eli.png")).convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -26)

        self.import_player_assets()

    def special_ability(self):
        if self.skywarp_charges <= 0:
            return 0
        self.skywarp_charges -= 1
        return self.attack + 10

    @staticmethod
    def get_display_name():
        return "Eli"

    @staticmethod
    def get_description():
        return "Fierce and driven, she'll do anything to protect her family."

    @staticmethod
    def get_preview_image():
        return os.path.join(CHARS, "eli.png")


class Character2(Character):
    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id=player_id, is_local=is_local)

        self.character_name = "mayde"
        self.hp = 150
        self.max_hp = 150
        self.attack = 20
        self.defense = 15
        self.speed = 25
        self.mindread_uses = 1

        self.image = pygame.image.load(os.path.join(CHARS, "mayde.png")).convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -26)

        self.import_player_assets()

    def special_ability(self):
        if self.mindread_uses <= 0:
            return False
        self.mindread_uses -= 1
        return True

    @staticmethod
    def get_display_name():
        return "Mayde"

    @staticmethod
    def get_description():
        return "The Queen's guard—strong, fast, and watching everything."

    @staticmethod
    def get_preview_image():
        return os.path.join(CHARS, "mayde.png")


class Character3(Character):
    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id=player_id, is_local=is_local)

        self.character_name = "quinne"
        self.hp = 100
        self.max_hp = 100
        self.attack = 20
        self.defense = 5
        self.speed = 15
        self.teleport_cooldown = 0

        self.image = pygame.image.load(os.path.join(CHARS, "quinne.png")).convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -26)

        self.import_player_assets()

    def special_ability(self):
        if self.teleport_cooldown > 0:
            return False
        self.teleport_cooldown = 3
        return True

    @staticmethod
    def get_display_name():
        return "Quinne"

    @staticmethod
    def get_description():
        return "Hyper and bold—she can blink short distances to outplay enemies."

    @staticmethod
    def get_preview_image():
        return os.path.join(CHARS, "quinne.png")


class Character4(Character):
    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id=player_id, is_local=is_local)

        self.character_name = "jay"
        self.hp = 100
        self.max_hp = 100
        self.attack = 15
        self.defense = 20
        self.speed = 10
        self.strength_boost_active = False

        self.image = pygame.image.load(os.path.join(CHARS, "jay.png")).convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -26)

        self.import_player_assets()

    def special_ability(self):
        if not self.strength_boost_active:
            self.attack += 8
            self.strength_boost_active = True
        return self.attack

    @staticmethod
    def get_display_name():
        return "Jay"

    @staticmethod
    def get_description():
        return "Mellow but powerful—his raw strength makes him hard to stop."

    @staticmethod
    def get_preview_image():
        return os.path.join(CHARS, "jay.png")


def get_all_character_classes():
    character_classes = []
    for cls in Character.__subclasses__():
        if cls.__name__ != "Character":
            character_classes.append(cls)
    return character_classes