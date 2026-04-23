"""
enemy.py - Enemy characters that patrol or wander the world

Patrol enemies use linked list patrol paths (lab exercise).
Random enemies wander freely without a patrol path.

Lab: Lab 6 - Sparse World Map
"""

import pygame
import math
import random
from datastructures.patrol_path import PatrolPath

# Enemy spawn data
ENEMY_SPAWN_DATA = [
    {
        "name": "Desert Guard",
        "spawn": (10, 20),
        "waypoints": [(5, 20), (15, 20), (15, 30), (5, 30)],
        "patrol_type": "circular",
        "speed": 1,
        "description": "Patrols the desert perimeter",
        "health": 60, "exp": 30, "attack_damage": 8,
        "notice_radius": 150, "attack_radius": 60,
    },
    {
        "name": "Forest Guard",
        "spawn": (25, 20),
        "waypoints": [(22, 20), (35, 20)],
        "patrol_type": "back_and_forth",
        "speed": 0.9,
        "description": "Patrols the forest",
        "health": 40, "exp": 20, "attack_damage": 5,
        "notice_radius": 150, "attack_radius": 50,
    },
    {
        "name": "Stone Sentinel",
        "spawn": (50, 20),
        "waypoints": [(45, 10), (55, 10), (55, 30), (45, 30)],
        "patrol_type": "one_way",
        "speed": 0.8,
        "description": "Guards the stone ruins",
        "health": 80, "exp": 40, "attack_damage": 12,
        "notice_radius": 150, "attack_radius": 60,
    },
    {
        "name": "Wandering Goblin",
        "spawn": (10, 10),
        "waypoints": [],
        "patrol_type": "random",
        "speed": 1.2,
        "description": "Roams the desert unpredictably",
        "health": 50, "exp": 25, "attack_damage": 10,
        "notice_radius": 150, "attack_radius": 70,
    },
]


class Enemy(pygame.sprite.Sprite):
    """
    Enemy character that follows a patrol path or wanders randomly.

    Patrol enemies (one_way / circular / back_and_forth) use a PatrolPath
    linked list to determine movement — that is the lab exercise.

    The random enemy type picks targets near its spawn and wanders freely;
    it does NOT use a PatrolPath so students don't need to implement anything
    special to see it move.
    """

    def __init__(self, name, start_x, start_y, patrol_path, obstacle_sprites,
                 speed=1.0, sprite_name=None, patrol_type=None,
                 health=60, exp=30, attack_damage=10,
                 notice_radius=200, attack_radius=60,
                 damage_player=None):
        super().__init__()

        self.name = name
        self.speed = speed
        self.patrol_path = patrol_path
        self.obstacle_sprites = obstacle_sprites
        self.sprite_name = sprite_name or name.lower().replace(' ', '_')

        # Determine movement mode
        if patrol_type == "random" or patrol_path is None:
            self.patrol_type = "random"
        else:
            self.patrol_type = patrol_path.patrol_type

        # Float position for sub-pixel accumulation (pygame Rects are integers)
        self.x = float(start_x * 64)
        self.y = float(start_y * 64)

        # Movement / animation
        self.direction = pygame.math.Vector2()
        self.status = 'down_idle'
        self.last_direction = 'down'

        # --- Patrol state (used by one_way / circular / back_and_forth) ---
        if self.patrol_type != "random" and patrol_path is not None:
            self.target_waypoint = self.patrol_path.get_next_waypoint()
        else:
            self.target_waypoint = None
        self.wait_timer = 0
        self.is_waiting = False
        self.patrol_active = True

        # --- Random wander state ---
        if self.patrol_type == "random":
            self.spawn_x = self.x          # pixel coords of spawn
            self.spawn_y = self.y
            self.wander_radius = 5         # tiles
            self.wander_target = None      # (pixel_x, pixel_y)
            self.wander_timer = 0.0        # seconds until forced target change

        # Sprites
        self.load_sprites()
        self.image = self.animations[self.status][0]
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.hitbox = self.rect.inflate(-10, -10)

        # Combat stats
        self.health = health
        self.max_health = health
        self.exp = exp
        self.attack_damage = attack_damage
        self.notice_radius = notice_radius
        self.attack_radius = attack_radius
        self.damage_player = damage_player   # callback: damage_player(amount)

        # Combat state
        self.combat_status = 'patrol'        # 'patrol' | 'chase' | 'attack'
        self.can_attack = True
        self.attack_time = 0
        self.attack_cooldown = 800           # ms between attacks

        # Hit invincibility
        self.vulnerable = True
        self.hit_time = 0
        self.invincibility_duration = 300    # ms

        self.frame_index = 0
        self.animation_speed = 0.15

    # ------------------------------------------------------------------
    # Sprite loading
    # ------------------------------------------------------------------

    def load_sprites(self):
        """Load directional sprite animations using the unified sprite system."""
        from sprite_loader import SpriteLoader
        self.animations = SpriteLoader.load_enemy_sprites(self.sprite_name)
        sprite_info = SpriteLoader.get_sprite_info(self.sprite_name, "../../graphics/enemies")
        print(f"  Loaded {sprite_info['type']} sprites for {self.name}: {sprite_info}")

    # ------------------------------------------------------------------
    # Update loop
    # ------------------------------------------------------------------

    def update(self):
        """Update enemy behavior each frame."""
        if self.combat_status == 'chase':
            self.move()
        elif self.combat_status == 'attack':
            self.direction.x = 0
            self.direction.y = 0
            if self.can_attack and self.damage_player:
                self.damage_player(self.attack_damage)
                self.can_attack = False
                self.attack_time = pygame.time.get_ticks()
        else:
            if self.patrol_type == "random":
                self._update_wander()
            else:
                self._update_patrol()

        self._cooldowns_combat()
        self.get_status()
        self.animate()
        self.check_death()

    # ------------------------------------------------------------------
    # Random wander logic
    # ------------------------------------------------------------------

    def _update_wander(self):
        """Wander randomly within wander_radius tiles of spawn."""
        self.wander_timer -= 1 / 60

        if self.wander_target is None or self._reached_wander_target() or self.wander_timer <= 0:
            self._pick_wander_target()
            return

        tx, ty = self.wander_target
        dx = tx - self.hitbox.centerx
        dy = ty - self.hitbox.centery
        distance = math.sqrt(dx * dx + dy * dy)

        if distance < self.speed * 2:
            self.direction.x = 0
            self.direction.y = 0
            self.wander_target = None
        else:
            self.direction.x = (dx / distance) * self.speed
            self.direction.y = (dy / distance) * self.speed
            self.move()

    def _pick_wander_target(self):
        """Choose a new random tile within wander_radius of spawn."""
        for _ in range(20):
            dx = random.randint(-self.wander_radius, self.wander_radius)
            dy = random.randint(-self.wander_radius, self.wander_radius)
            if dx != 0 or dy != 0:
                break
        self.wander_target = (self.spawn_x + dx * 64, self.spawn_y + dy * 64)
        self.wander_timer = random.uniform(4.0, 10.0)

    def _reached_wander_target(self):
        if self.wander_target is None:
            return True
        tx, ty = self.wander_target
        dx = tx - self.hitbox.centerx
        dy = ty - self.hitbox.centery
        return math.sqrt(dx * dx + dy * dy) < self.speed * 2

    # ------------------------------------------------------------------
    # Patrol logic (one_way / circular / back_and_forth)
    # ------------------------------------------------------------------

    def _update_patrol(self):
        """Move along the linked-list patrol path."""
        if not self.patrol_active or not self.target_waypoint:
            self.direction.x = 0
            self.direction.y = 0
            return

        if self.is_waiting:
            self.direction.x = 0
            self.direction.y = 0
            self.wait_timer -= 1 / 60
            if self.wait_timer <= 0:
                self.is_waiting = False
                self.target_waypoint = self.patrol_path.get_next_waypoint()
            return

        self._move_toward_target()

    def _move_toward_target(self):
        """Move toward the current waypoint."""
        if not self.target_waypoint:
            self.patrol_active = False
            self.direction.x = 0
            self.direction.y = 0
            return

        target_x = self.target_waypoint.x * 64
        target_y = self.target_waypoint.y * 64

        dx = target_x - self.hitbox.centerx
        dy = target_y - self.hitbox.centery
        distance = math.sqrt(dx * dx + dy * dy)

        if distance < self.speed * 2:
            self.direction.x = 0
            self.direction.y = 0
            if self.target_waypoint.wait_time > 0:
                self.is_waiting = True
                self.wait_timer = self.target_waypoint.wait_time
            else:
                self.target_waypoint = self.patrol_path.get_next_waypoint()
        else:
            if distance > 0:
                self.direction.x = (dx / distance) * self.speed
                self.direction.y = (dy / distance) * self.speed
            self.move()

    # ------------------------------------------------------------------
    # Movement + collision
    # ------------------------------------------------------------------

    def move(self):
        """Move using float accumulators; only update Rect when integer pixel changes."""
        if self.direction.x != 0:
            self.x += self.direction.x
            new_cx = int(self.x)
            if new_cx != self.hitbox.centerx:
                self.hitbox.centerx = new_cx
                self.collision('horizontal')
                self.x = float(self.hitbox.centerx)

        if self.direction.y != 0:
            self.y += self.direction.y
            new_cy = int(self.y)
            if new_cy != self.hitbox.centery:
                self.hitbox.centery = new_cy
                self.collision('vertical')
                self.y = float(self.hitbox.centery)

        self.rect.center = self.hitbox.center

    def collision(self, direction):
        """Collision with walls and other enemies."""
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite is self:
                    continue
                sprite_rect = getattr(sprite, 'hitbox', sprite.rect)
                if sprite_rect.colliderect(self.hitbox):
                    if self.direction.x > 0:
                        self.hitbox.right = sprite_rect.left
                    if self.direction.x < 0:
                        self.hitbox.left = sprite_rect.right

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite is self:
                    continue
                sprite_rect = getattr(sprite, 'hitbox', sprite.rect)
                if sprite_rect.colliderect(self.hitbox):
                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite_rect.top
                    if self.direction.y < 0:
                        self.hitbox.top = sprite_rect.bottom

    # ------------------------------------------------------------------
    # Animation helpers
    # ------------------------------------------------------------------

    def get_status(self):
        """Set status string for animation based on current movement direction."""
        if self.direction.x == 0 and self.direction.y == 0:
            if 'idle' not in self.status:
                self.status = self.last_direction + '_idle'
        else:
            if abs(self.direction.x) > abs(self.direction.y):
                if self.direction.x > 0:
                    self.status = 'right'
                    self.last_direction = 'right'
                else:
                    self.status = 'left'
                    self.last_direction = 'left'
            else:
                if self.direction.y > 0:
                    self.status = 'down'
                    self.last_direction = 'down'
                else:
                    self.status = 'up'
                    self.last_direction = 'up'

    def animate(self):
        """Advance the animation frame."""
        animation = self.animations[self.status]
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0
        self.image = animation[int(self.frame_index)]

        if not self.vulnerable:
            from math import sin
            self.image = self.image.copy()
            self.image.set_alpha(255 if sin(pygame.time.get_ticks() * 0.015) >= 0 else 80)

    # ------------------------------------------------------------------
    # Combat
    # ------------------------------------------------------------------

    def get_player_distance_direction(self, player):
        """Return (pixel_distance, normalized_Vector2) toward player."""
        enemy_vec  = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        distance   = (player_vec - enemy_vec).magnitude()
        direction  = (player_vec - enemy_vec).normalize() if distance > 0 else pygame.math.Vector2()
        return distance, direction

    def enemy_update(self, player):
        """Update combat AI state (called from Level with player reference)."""
        distance, direction = self.get_player_distance_direction(player)

        if distance <= self.attack_radius and self.can_attack:
            self.combat_status = 'attack'
        elif distance <= self.notice_radius:
            self.combat_status = 'chase'
            self.direction.x = direction.x * self.speed
            self.direction.y = direction.y * self.speed
        else:
            self.combat_status = 'patrol'

    def get_damage(self, player):
        """Take weapon damage from player."""
        if self.vulnerable:
            self.health -= player.get_full_weapon_damage()
            self.vulnerable = False
            self.hit_time = pygame.time.get_ticks()

    def check_death(self):
        """Remove enemy and award XP when health reaches zero."""
        if self.health <= 0:
            self.kill()

    def _cooldowns_combat(self):
        """Restore can_attack and vulnerable after their cooldowns."""
        current_time = pygame.time.get_ticks()
        if not self.can_attack:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.can_attack = True
        if not self.vulnerable:
            if current_time - self.hit_time >= self.invincibility_duration:
                self.vulnerable = True

    # ------------------------------------------------------------------
    # Debug helpers
    # ------------------------------------------------------------------

    def draw_debug_info(self, surface, camera_offset=(0, 0)):
        """Draw debug overlay: name, target line, hitbox."""
        font = pygame.font.Font(None, 20)
        text = font.render(self.name, True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.centerx = self.rect.centerx - camera_offset[0]
        text_rect.bottom = self.rect.top - camera_offset[1] - 5
        surface.blit(text, text_rect)

        ex = self.rect.centerx - camera_offset[0]
        ey = self.rect.centery - camera_offset[1]

        if self.patrol_type == "random" and self.wander_target:
            tx = self.wander_target[0] - camera_offset[0]
            ty = self.wander_target[1] - camera_offset[1]
            pygame.draw.line(surface, (0, 200, 255), (ex, ey), (int(tx), int(ty)), 2)
            pygame.draw.circle(surface, (0, 200, 255), (int(tx), int(ty)), 8, 2)
        elif self.target_waypoint and self.patrol_active:
            tx = self.target_waypoint.x * 64 - camera_offset[0]
            ty = self.target_waypoint.y * 64 - camera_offset[1]
            pygame.draw.line(surface, (255, 255, 0), (ex, ey), (int(tx), int(ty)), 2)
            pygame.draw.circle(surface, (255, 0, 0), (int(tx), int(ty)), 8, 2)

        hitbox_rect = self.hitbox.copy()
        hitbox_rect.x -= camera_offset[0]
        hitbox_rect.y -= camera_offset[1]
        pygame.draw.rect(surface, (0, 255, 0), hitbox_rect, 1)

    def get_debug_status(self):
        """One-line status string for the debug overlay."""
        if self.patrol_type == "random":
            if self.wander_target:
                tx = int(self.wander_target[0] / 64)
                ty = int(self.wander_target[1] / 64)
                return f"{self.name}: Wandering to ({tx}, {ty})"
            return f"{self.name}: Choosing target..."
        if not self.patrol_active:
            return f"{self.name}: Patrol Complete"
        if self.is_waiting:
            return f"{self.name}: Waiting ({self.wait_timer:.1f}s)"
        if self.target_waypoint:
            return f"{self.name}: Moving to ({self.target_waypoint.x}, {self.target_waypoint.y})"
        return f"{self.name}: No target"

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def reset_patrol(self):
        """Reset enemy to the start of its patrol (or clear wander target)."""
        self.direction.x = 0
        self.direction.y = 0
        if self.patrol_type == "random":
            self.wander_target = None
            self.wander_timer = 0.0
        else:
            self.patrol_path.reset()
            self.target_waypoint = self.patrol_path.get_next_waypoint()
            self.patrol_active = True
            self.is_waiting = False
            self.wait_timer = 0