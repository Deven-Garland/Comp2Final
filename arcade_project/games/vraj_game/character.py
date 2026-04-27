"""
character.py - Character classes with inventory AND networking support

Integrated version combining:
- lab-03's Character class (inventory, animations, stats)
- project-01's Player class (networking, multiplayer)
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
        self.status = 'down'
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
        
        # Inventory system
        self.inventory = Inventory(max_size=20)
        
        # Network properties (from project-01)
        self.player_id = player_id
        self.is_local = is_local
        self.name = ""
        self.other_players = []
        
        # For smooth network interpolation (remote players only)
        if not is_local:
            self.target_x = pos[0]
            self.target_y = pos[1]
            self.interpolation_speed = 0.3
        
        # Color tint for other players
        if not is_local:
            self.image = self.image.copy()
            self.image.fill((100, 100, 255, 128), special_flags=pygame.BLEND_RGBA_MULT)

    def import_player_assets(self, animate=True):
        """Load character animations using unified sprite system"""
        from sprite_loader import SpriteLoader
        
        # Use the unified sprite loader
        self.animations = SpriteLoader.load_character_sprites(self.character_name)
        
        # Debug: Print sprite loading info
        sprite_info = SpriteLoader.get_sprite_info(self.character_name, "../../graphics/characters")
        print(f"Loaded {sprite_info['type']} sprites for {self.character_name}: {sprite_info}")
        
        # Ensure we have all required animations, add idle versions
        required_animations = ['up', 'down', 'left', 'right']
        for direction in required_animations:
            if direction not in self.animations:
                # Create default if missing
                surf = pygame.Surface((64, 64))
                surf.fill((255, 0, 255))
                self.animations[direction] = [surf]
            
            # Create idle version if not present (same as movement)
            idle_key = f"{direction}_idle"
            if idle_key not in self.animations:
                self.animations[idle_key] = self.animations[direction].copy()

    def input(self):
        """Handle input - only for local player"""
        if not self.is_local:
            return
            
        if not self.attacking:
            keys = pygame.key.get_pressed()

            # Movement input
            if keys[pygame.K_UP]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_DOWN]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0

            if keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.status = 'right'
            elif keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.status = 'left'
            else:
                self.direction.x = 0

            # Attack input 
            if keys[pygame.K_SPACE]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()

    def get_status(self):
        """Update animation status"""
        # Idle status
        if self.direction.x == 0 and self.direction.y == 0:
            if not 'idle' in self.status and not 'attack' in self.status:
                self.status = self.status + '_idle'

        if self.attacking:
            self.direction.x = 0
            self.direction.y = 0
            if not 'attack' in self.status:
                if 'idle' in self.status:
                    self.status = self.status.replace('_idle','_attack')
                else:
                    self.status = self.status + '_attack'
        else:
            if 'attack' in self.status:
                self.status = self.status.replace('_attack','')
    
    def move(self, speed):
        """Move the character"""
        if self.is_local:
            # Local player: physics-based movement
            if self.direction.magnitude() != 0:
                self.direction = self.direction.normalize()

            self.hitbox.x += self.direction.x * speed
            self.collision('horizontal')
            self.hitbox.y += self.direction.y * speed
            self.collision('vertical')
            
            self.rect.center = self.hitbox.center
        else:
            # Remote players: smooth interpolation
            self.interpolate_to_target()
    
    def set_position(self, x, y):
        """Set position (network update)"""
        if self.is_local:
            self.rect.x = x
            self.rect.y = y
            self.hitbox.center = self.rect.center
        else:
            self.target_x = x
            self.target_y = y
    
    def interpolate_to_target(self):
        """Smoothly move towards target position"""
        dx = self.target_x - self.rect.x
        dy = self.target_y - self.rect.y
        
        self.rect.x += dx * self.interpolation_speed
        self.rect.y += dy * self.interpolation_speed
        self.hitbox.center = self.rect.center
    
    def collision(self, direction):
        """Handle collision with obstacles"""
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                # Check if sprite has hitbox attribute
                sprite_box = sprite.hitbox if hasattr(sprite, 'hitbox') else sprite.rect
                if sprite_box.colliderect(self.hitbox):
                    if self.direction.x > 0:
                        self.hitbox.right = sprite_box.left
                    if self.direction.x < 0:
                        self.hitbox.left = sprite_box.right

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                sprite_box = sprite.hitbox if hasattr(sprite, 'hitbox') else sprite.rect
                if sprite_box.colliderect(self.hitbox):
                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite_box.top
                    if self.direction.y < 0:
                        self.hitbox.top = sprite_box.bottom
        
        # Player collision (only for local player)
        if self.is_local:
            self.collision_with_players(direction)
    
    def collision_with_players(self, direction):
        """Prevent overlap with other players"""
        if direction == 'horizontal':
            for other_player in self.other_players:
                if other_player.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:  # moving right
                        self.hitbox.right = other_player.hitbox.left
                    if self.direction.x < 0:  # moving left
                        self.hitbox.left = other_player.hitbox.right
        
        if direction == 'vertical':
            for other_player in self.other_players:
                if other_player.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0:  # moving down
                        self.hitbox.bottom = other_player.hitbox.top
                    if self.direction.y < 0:  # moving up
                        self.hitbox.top = other_player.hitbox.bottom
    
    def cooldowns(self):
        """Handle attack cooldowns"""
        current_time = pygame.time.get_ticks()

        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.attacking = False

    def animate(self):
        """Animate the character"""
        if self.animations is None:
            return
            
        # Get current animation
        anim_key = self.status.replace("_idle", "").replace("_attack", "")
        if anim_key not in self.animations:
            anim_key = 'down'
        
        animation = self.animations[anim_key]
        
        # Safety check: if animation list is empty, skip
        if not animation or len(animation) == 0:
            return

        # Loop over the frame index 
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        # Set the image
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center = self.hitbox.center)
        
        # Apply tint for remote players
        if not self.is_local:
            self.image = self.image.copy()
            self.image.fill((100, 100, 255, 128), special_flags=pygame.BLEND_RGBA_MULT)

    def update(self):
        """Update character state"""
        self.input()
        self.cooldowns()
        self.get_status()
        if self.animations:
            self.animate()
        self.move(self.speed)

    def special_ability(self):
        """Special ability - override in subclasses"""
        pass
    
    @staticmethod
    def get_display_name():
        return "Unknown"
    
    @staticmethod
    def get_description():
        return "A mysterious character"
    
    @staticmethod
    def get_preview_image():
        return '../../graphics/test/player.png'
