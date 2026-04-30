"""
character.py - Character classes with inventory AND networking support
"""

import pygame
from settings import *
from support import import_folder
from inventory import Inventory


class Character(pygame.sprite.Sprite):
    """Base Character class with inventory and networking"""

    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(groups)

        # Basic sprite setup
        self.image = pygame.Surface((64, 64))
        self.image.fill((255, 0, 255))
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-48, -40)

        # Character stats
        self.character_name = "Unknown"
        self.hp, self.max_hp = 100, 100
        self.attack, self.defense = 10, 5

        # Graphics setup
        self.status = "down"
        self.frame_index = 0
        self.animation_speed = 0.15
        self.animations = None

        # Movement
        self.direction = pygame.math.Vector2()
        self.speed = 5
        self.attacking = False
        self.attack_cooldown = 400
        self.attack_time = None
        self.obstacle_sprites = obstacle_sprites

        # Combat callbacks set by level
        self.create_attack_callback = None
        self.destroy_attack_callback = None

        # Damage / invulnerability
        self.vulnerable = True
        self.hurt_time = 0
        self.invulnerability_duration = 500

        # Equipped weapon / experience
        self.equipped_weapon = None
        self.exp = 0

        # Inventory + networking fields expected by level/network code
        self.inventory = Inventory(max_size=20)
        self.player_id = player_id
        self.is_local = is_local
        self.name = ""
        self.other_players = []

        if not is_local:
            self.target_x = pos[0]
            self.target_y = pos[1]
            self.interpolation_speed = 0.3
            self.image = self.image.copy()
            self.image.fill((100, 100, 255, 128), special_flags=pygame.BLEND_RGBA_MULT)

    def import_player_assets(self, animate=True):
        from sprite_loader import SpriteLoader
        self.animations = SpriteLoader.load_character_sprites(self.character_name)
        required = ["up", "down", "left", "right"]
        for direction in required:
            if direction not in self.animations:
                surf = pygame.Surface((64, 64))
                surf.fill((255, 0, 255))
                self.animations[direction] = [surf]
            idle_key = f"{direction}_idle"
            if idle_key not in self.animations:
                self.animations[idle_key] = self.animations[direction].copy()

    def input(self):
        if not self.is_local:
            return
        if not self.attacking:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                self.direction.y = -1
                self.status = "up"
            elif keys[pygame.K_DOWN]:
                self.direction.y = 1
                self.status = "down"
            else:
                self.direction.y = 0
            if keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.status = "right"
            elif keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.status = "left"
            else:
                self.direction.x = 0
            if keys[pygame.K_SPACE]:
                self.attack()

    def attack(self):
        self.attacking = True
        self.attack_time = pygame.time.get_ticks()
        self.direction.x = 0
        self.direction.y = 0
        self.status = self.status.split("_")[0] + "_attack"
        if self.create_attack_callback:
            self.create_attack_callback()

    def get_full_weapon_damage(self):
        if self.equipped_weapon:
            return self.attack + self.equipped_weapon.attack_bonus
        return self.attack

    def cooldowns(self):
        if self.attacking:
            current = pygame.time.get_ticks()
            if current - self.attack_time >= self.attack_cooldown:
                self.attacking = False
                if self.destroy_attack_callback:
                    self.destroy_attack_callback()
        if not self.vulnerable:
            current = pygame.time.get_ticks()
            if current - self.hurt_time >= self.invulnerability_duration:
                self.vulnerable = True

    def get_status(self):
        if self.direction.x == 0 and self.direction.y == 0:
            if "_idle" not in self.status and "_attack" not in self.status:
                self.status = self.status + "_idle"
        if self.attacking and "_attack" not in self.status:
            self.status = self.status.split("_")[0] + "_attack"
        elif not self.attacking and "_attack" in self.status:
            self.status = self.status.replace("_attack", "")

    def animate(self):
        if self.animations and self.status in self.animations:
            animation = self.animations[self.status]
            self.frame_index += self.animation_speed
            if self.frame_index >= len(animation):
                self.frame_index = 0
            self.image = animation[int(self.frame_index)]
            self.rect = self.image.get_rect(center=self.hitbox.center)
        if not self.vulnerable:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

    def wave_value(self):
        value = pygame.math.Vector2()
        return 255 if value else 0

    def move(self, speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()
        self.hitbox.x += self.direction.x * speed
        self.collision("horizontal")
        self.hitbox.y += self.direction.y * speed
        self.collision("vertical")
        self.rect.center = self.hitbox.center

    def collision(self, direction):
        for sprite in self.obstacle_sprites:
            if sprite.hitbox.colliderect(self.hitbox):
                if direction == "horizontal":
                    if self.direction.x > 0:
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:
                        self.hitbox.left = sprite.hitbox.right
                if direction == "vertical":
                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:
                        self.hitbox.top = sprite.hitbox.bottom

    def set_position(self, x, y):
        if hasattr(self, "target_x"):
            self.target_x = x
            self.target_y = y
        else:
            self.rect.x = x
            self.rect.y = y
            self.hitbox.center = self.rect.center

    def interpolate_position(self):
        if not hasattr(self, "target_x"):
            return
        dx = self.target_x - self.rect.x
        dy = self.target_y - self.rect.y
        if abs(dx) > 1:
            self.rect.x += dx * self.interpolation_speed
        else:
            self.rect.x = self.target_x
        if abs(dy) > 1:
            self.rect.y += dy * self.interpolation_speed
        else:
            self.rect.y = self.target_y
        self.hitbox.center = self.rect.center

    def update(self):
        if self.is_local:
            self.input()
            self.cooldowns()
            self.get_status()
            self.move(self.speed)
            self.animate()
        else:
            self.interpolate_position()
            self.animate()

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
        return "../../graphics/test/player.png"
