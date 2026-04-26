"""
subcharacter.py - Character classes

Different character types that players can choose from
"""

import pygame
import random
from character import Character
from settings import graphics_path


class AverageJoe(Character):
    """Average Joe - Balanced in all stats"""
    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id, is_local)
        self.character_name = "Average Joe"
        self.hp, self.max_hp = 100, 100
        self.attack, self.defense = 10, 10
        self.speed = 10

        try:
            self.image = pygame.image.load(graphics_path("characters", "AverageJoe", "average_joe.png")).convert_alpha()
            self.rect = self.image.get_rect(topleft=pos)
            self.hitbox = self.rect.inflate(0, -26)
        except:
            pass

        if is_local:
            self.import_player_assets(animate=True)

    def blank_stare(self, enemy):
        """25% chance to put the enemy to sleep permanently"""
        if random.random() < 0.25:
            enemy.speed = 0
            print("Enemy is asleep forever")
        else:
            print("Enemy was not affected by Blank Stare")

    def take_damage(self, damage):
        if damage < 0:
            print("Damage must be positive")
            return
        damage_taken = 0 if self.defense >= damage else damage - self.defense
        self.hp -= damage_taken
        if self.hp < 0:
            self.hp = 0
        print(f"{self.character_name} took {damage_taken} points, they now have {self.hp} health")

    def is_alive(self):
        return self.hp > 0

    def heal(self, amount):
        if amount < 0:
            print("Heal must be positive")
            return
        if self.is_alive():
            self.hp = min(self.hp + amount, self.max_hp)
            print(f"{self.character_name} healed by {amount}. Current Health: {self.hp}")
        else:
            print(f"{self.character_name} is dead")

    @staticmethod
    def get_display_name():
        return "Average Joe"

    @staticmethod
    def get_description():
        return "This is the basic character that the player can choose, they are average in all stats."

    @staticmethod
    def get_preview_image():
        return graphics_path("characters", "AverageJoe", "average_joe.png")


class TheEngineer(Character):
    """The Engineer - High defense and speed, low attack"""
    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id, is_local)
        self.character_name = "The Engineer"
        self.hp, self.max_hp = 80, 80
        self.attack, self.defense = 6, 15
        self.speed = 15

        try:
            self.image = pygame.image.load(graphics_path("characters", "Engineer", "engineer.png")).convert_alpha()
            self.rect = self.image.get_rect(topleft=pos)
            self.hitbox = self.rect.inflate(0, -26)
        except:
            pass

        if is_local:
            self.import_player_assets(animate=True)

    def scavenger(self):
        """The Engineer can build unique items"""
        print("The Engineer can build unique items")

    def take_damage(self, damage):
        if damage < 0:
            print("Damage must be positive")
            return
        damage_taken = 0 if self.defense >= damage else damage - self.defense
        self.hp -= damage_taken
        if self.hp < 0:
            self.hp = 0
        print(f"{self.character_name} took {damage_taken} points, they now have {self.hp} health")

    def is_alive(self):
        return self.hp > 0

    def heal(self, amount):
        if amount < 0:
            print("Heal must be positive")
            return
        if self.is_alive():
            self.hp = min(self.hp + amount, self.max_hp)
            print(f"{self.character_name} healed by {amount}. Current Health: {self.hp}")
        else:
            print(f"{self.character_name} is dead")

    @staticmethod
    def get_display_name():
        return "The Engineer"

    @staticmethod
    def get_description():
        return "The engineer studied engineering in college giving them vast knowledge, at a cost of physical ability."

    @staticmethod
    def get_preview_image():
        return graphics_path("characters", "Engineer", "engineer.png")


class Athlete(Character):
    """Athlete - High HP, attack, and speed, but low defense"""
    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id, is_local)
        self.character_name = "The Athlete"
        self.hp, self.max_hp = 130, 130
        self.attack, self.defense = 20, 3
        self.speed = 20
        self.base_attack = self.attack
        self.buff_active = False
        self.buff_end_time = 0

        try:
            self.image = pygame.image.load(graphics_path("characters", "Athlete", "athlete.png")).convert_alpha()
            self.rect = self.image.get_rect(topleft=pos)
            self.hitbox = self.rect.inflate(0, -26)
        except:
            pass

        if is_local:
            self.import_player_assets(animate=True)

    def pumped_up(self):
        """Boost attack by 50% for 3 minutes"""
        if not self.buff_active:
            self.buff_active = True
            self.attack = self.base_attack * 1.5
            self.buff_end_time = pygame.time.get_ticks() + 180000
            print("Pumped Up activated")

    def handle_buff(self):
        if self.buff_active and pygame.time.get_ticks() >= self.buff_end_time:
            self.buff_active = False
            self.attack = self.base_attack
            print("Pumped Up has expired!")

    def take_damage(self, damage):
        if damage < 0:
            print("Damage must be positive")
            return
        damage_taken = 0 if self.defense >= damage else damage - self.defense
        self.hp -= damage_taken
        if self.hp < 0:
            self.hp = 0
        print(f"{self.character_name} took {damage_taken} points, they now have {self.hp} health")

    def is_alive(self):
        return self.hp > 0

    def heal(self, amount):
        if amount < 0:
            print("Heal must be positive")
            return
        if self.is_alive():
            self.hp = min(self.hp + amount, self.max_hp)
            print(f"{self.character_name} healed by {amount}. Current Health: {self.hp}")
        else:
            print(f"{self.character_name} is dead")

    @staticmethod
    def get_display_name():
        return "The Athlete"

    @staticmethod
    def get_description():
        return "The Athlete was a D1 player who spent all of their time focused on becoming the best they could, however they were always injury prone."

    @staticmethod
    def get_preview_image():
        return graphics_path("characters", "Athlete", "athlete.png")


class TheInsomniac(Character):
    """The Insomniac - High attack and speed, with a speed/defense buff"""
    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id, is_local)
        self.character_name = "The Insomniac"
        self.hp, self.max_hp = 95, 95
        self.attack, self.defense = 18, 8
        self.speed = 18
        self.base_speed = self.speed
        self.base_defense = self.defense
        self.buff_active = False
        self.buff_end_time = 0

        try:
            self.image = pygame.image.load(graphics_path("characters", "Insomniac", "insomniac.png")).convert_alpha()
            self.rect = self.image.get_rect(topleft=pos)
            self.hitbox = self.rect.inflate(0, -26)
        except:
            pass

        if is_local:
            self.import_player_assets(animate=True)

    def wide_awake(self):
        """Boost speed and defense by 25% for 3 minutes"""
        if not self.buff_active:
            self.buff_active = True
            self.speed = int(self.base_speed * 1.25)
            self.defense = int(self.base_defense * 1.25)
            self.buff_end_time = pygame.time.get_ticks() + 180000
            print("Wide Awake activated")

    def handle_buff(self):
        if self.buff_active and pygame.time.get_ticks() >= self.buff_end_time:
            self.buff_active = False
            self.speed = self.base_speed
            self.defense = self.base_defense
            print("Wide Awake has expired!")

    def take_damage(self, damage):
        if damage < 0:
            print("Damage must be positive")
            return
        damage_taken = 0 if self.defense >= damage else damage - self.defense
        self.hp -= damage_taken
        if self.hp < 0:
            self.hp = 0
        print(f"{self.character_name} took {damage_taken} points, they now have {self.hp} health")

    def is_alive(self):
        return self.hp > 0

    def heal(self, amount):
        if amount < 0:
            print("Heal must be positive")
            return
        if self.is_alive():
            self.hp = min(self.hp + amount, self.max_hp)
            print(f"{self.character_name} healed by {amount}. Current Health: {self.hp}")
        else:
            print(f"{self.character_name} is dead")

    @staticmethod
    def get_display_name():
        return "The Insomniac"

    @staticmethod
    def get_description():
        return "Years of sleepless nights have hardened the Insomniac. The fog's whispers don't faze them—they've already heard worse in their own head."

    @staticmethod
    def get_preview_image():
        return graphics_path("characters", "Insomniac", "insomniac.png")


def get_all_character_classes():
    """Auto-discover all character classes"""
    character_classes = []
    for cls in Character.__subclasses__():
        if cls.__name__ != 'Character':
            character_classes.append(cls)
    return character_classes