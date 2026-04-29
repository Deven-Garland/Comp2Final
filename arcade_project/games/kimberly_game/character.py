"""
character.py - Character classes for the game
Students create 4 unique character classes, each with:
- Different stats (hp, attack, defense, speed) 
- Unique special ability 
- Character sprite image
Author: [Kimberly Olea] 
Date: [1/25/26] 
Lab: Lab 2 - Character Classes 
"""

import pygame
from settings import *

class Character(pygame.sprite.Sprite):
    """Base Character class with inventory and networking"""
    
    def __init__(self, pos, groups, obstacle_sprites, player_id = None, is_local=True):
        super().__init__(groups)

        # Stats (override in subclasses)
        self.character_name = "Unknown"
        self.hp = 100
        self.max_hp = 100
        self.attack = 10
        self.defense = 5
        self.speed = 5

        # DO NOT EDIT
        self.image = pygame.Surface((64, 64))
        self.image.fill((255, 0, 255))
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -26)

        # Movement
        self.direction = pygame.math.Vector2()
        self.obstacle_sprites = obstacle_sprites

        # Validation
        self.__validate_name()
        self._validate_stats()

    # ---------- Validation ----------
    def __validate_name(self):
        if not isinstance(self.character_name, str) or not self.character_name.strip():
            raise ValueError("Character name must be a non-empty string.")

    def _validate_stats(self):
        for stat in (self.hp, self.max_hp, self.attack, self.defense, self.speed):
            if not isinstance(stat, int) or stat < 0:
                raise ValueError("Stats must be non-negative integers.")

    # ---------- Movement ----------
    def input(self):
        keys = pygame.key.get_pressed()

        self.direction.y = -1 if keys[pygame.K_UP] else 1 if keys[pygame.K_DOWN] else 0
        self.direction.x = 1 if keys[pygame.K_RIGHT] else -1 if keys[pygame.K_LEFT] else 0

    def move(self, speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')
        self.rect.center = self.hitbox.center

    def collision(self, direction):
        for sprite in self.obstacle_sprites:
            if sprite.hitbox.colliderect(self.hitbox):
                if direction == 'horizontal':
                    if self.direction.x > 0:
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:
                        self.hitbox.left = sprite.hitbox.right
                if direction == 'vertical':
                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:
                        self.hitbox.top = sprite.hitbox.bottom

    def update(self):
        self.input()
        self.move(self.speed)

    # ---------- Combat ----------
    def take_damage(self, damage):
        actual_damage = max(0, damage - self.defense)
        self.hp = max(0, self.hp - actual_damage)
        return actual_damage

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    def is_alive(self):
        return self.hp > 0

    def special_ability(self):
        pass

    @staticmethod
    def get_display_name():
        return "Unknown"

    @staticmethod
    def get_description():
        return "A mysterious character."

    @staticmethod
    def get_preview_image():
        return '../../graphics/test/player.png'
