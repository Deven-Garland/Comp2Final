"""
level.py - Game level with character classes and networking

Integrated version combining lab-03 and project-01
"""

import pygame
from settings import *
from tile import Tile
from map_loader import load_layer
from character import Character
from subcharacter import get_all_character_classes
from network_client import NetworkClient
from inventory_ui import InventoryUI
from item import create_example_items
from time_travel import TimeTravel
from enemy import Enemy, ENEMY_SPAWN_DATA
from datastructures.patrol_path import PatrolPath
from weapon import Weapon as WeaponSprite
import sys


class Level:
    def __init__(self, player_name, character_class, server_host='localhost', server_port=8080, serializer='json'):
        # Get the display surface
        self.display_surface = pygame.display.get_surface()

        # Sprite group setup
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()

        # Combat sprite groups
        self.current_attack = None
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()

        # Store character class for player creation
        self.character_class = character_class

        # Sprite setup
        self.create_map()

        # Network setup with serializer
        self.network = NetworkClient(player_name, server_host, server_port, serializer, game_id='ellie')
        self.connected = self.network.connect()

        # Track other players
        self.other_players = {}  # player_id -> Character sprite

        # Font for displaying names
        self.font = pygame.font.Font(None, 24)

        # Connection status
        self.connection_status = "Connecting..."

        # Inventory UI
        self.inventory_ui = InventoryUI(self.player.inventory)
        self.inventory_ui.character = self.player

        # Add starting items for testing
        self.add_starting_items()

        # Time travel system (Lab 4)
        self.time_travel = TimeTravel(max_history=180)
        self.is_time_traveling = False
        self.enemy_history = []
        self.enemy_future = []

        # Enemy system (Lab 5)
        self.enemies = pygame.sprite.Group()
        self.create_enemies()

        # Debug mode for showing enemy paths
        self.show_enemy_debug = False

    def _load_tileset(self, path):
        """Load a tileset image and return a dict mapping tile_id -> Surface.

        Assumes tiles are arranged left-to-right, top-to-bottom in a grid of
        TILESIZE x TILESIZE cells.  Returns an empty dict if the file is
        missing or unreadable.
        """
        try:
            sheet = pygame.image.load(path).convert_alpha()
            cols = sheet.get_width() // TILESIZE
            rows = sheet.get_height() // TILESIZE
            tiles = {}

            for r in range(rows):
                for c in range(cols):
                    tile_id = r * cols + c
                    surf = sheet.subsurface(
                        pygame.Rect(c * TILESIZE, r * TILESIZE, TILESIZE, TILESIZE)
                    )
                    tiles[tile_id] = surf

            return tiles
        except Exception:
            return {}

    def create_map(self):
        """Create the game map and player.

        Loads CSV layers and creates floor, boundary, grass, and object tiles.
        Player spawn is read from WORLD_MAP.
        """
        floor_blocks_loaded = False

        try:
            from support import import_csv_to_sparse

            start_path = str(sys.path[0])

            layouts = {
                'floor':    import_csv_to_sparse(start_path + '/map/map_Floor.csv'),
                'boundary': import_csv_to_sparse(start_path + '/map/map_FloorBlocks.csv'),
                'grass':    import_csv_to_sparse(start_path + '/map/map_Grass.csv'),
                'object':   import_csv_to_sparse(start_path + '/map/map_Objects.csv'),
            }

            for style, layout in layouts.items():
                for (row, col), area_id in layout.items():
                    x = col * TILESIZE
                    y = row * TILESIZE

                    if style == 'floor':
                        Tile((x, y), [self.visible_sprites], 'floor', area_id=area_id)

                    elif style == 'boundary':
                        Tile((x, y), [self.obstacle_sprites], 'boundary')
                        floor_blocks_loaded = True

                    elif style == 'grass':
                        Tile((x, y), [self.visible_sprites], 'grass', area_id=area_id)

                    elif style == 'object':
                        Tile((x, y), [self.visible_sprites, self.obstacle_sprites], 'object', area_id=area_id)

        except Exception:
            # Fallback to original loader style
            LAYERS = [
                ('map/map_Floor.csv',       'floor',    [self.visible_sprites]),
                ('map/map_FloorBlocks.csv', 'boundary', [self.obstacle_sprites]),
                ('map/map_Grass.csv',       'grass',    [self.visible_sprites]),
                ('map/map_Objects.csv',     'object',   [self.visible_sprites, self.obstacle_sprites]),
            ]

            for csv_path, sprite_type, groups in LAYERS:
                try:
                    layer = load_layer(csv_path)
                    entries = list(layer.items())

                    if not entries:
                        continue

                    for (row, col), area_id in entries:
                        x = col * TILESIZE
                        y = row * TILESIZE

                        if sprite_type == 'boundary':
                            Tile((x, y), [self.obstacle_sprites], 'boundary')
                            floor_blocks_loaded = True
                        else:
                            Tile((x, y), groups, sprite_type, area_id=area_id)

                except Exception as e:
                    print(f"[Map] {csv_path} failed: {e}")

        # WORLD_MAP fallback for boundaries and player spawn
        for row_index, row in enumerate(WORLD_MAP):
            for col_index, col in enumerate(row):
                x = col_index * TILESIZE
                y = row_index * TILESIZE

                if col == 'x' and not floor_blocks_loaded:
                    Tile((x, y), [self.obstacle_sprites], 'boundary')

                if col == 'p':
                    self.player = self.character_class(
                        (x, y),
                        [self.visible_sprites],
                        self.obstacle_sprites,
                        is_local=True
                    )
                    self.player.create_attack_callback = self.create_attack
                    self.player.destroy_attack_callback = self.destroy_attack

    def add_starting_items(self):
        """Add items defined in item.py's create_example_items() to the player's inventory."""
        print("Adding starting items to inventory...")

        for item in create_example_items():
            success = self.player.inventory.add_item(item)
            if success:
                print(f"  Added: {item.name}")
            else:
                print(f"  Inventory full! Couldn't add: {item.name}")

        print(f"Total items: {len(self.player.inventory.items)}")

        for item in self.player.inventory.items:
            if item.item_type == 'weapon':
                self.player.equipped_weapon = item
                print(f"Auto-equipped: {item.name}")
                break

        print("Press 'I' to open inventory and switch weapons. SPACE to attack!")

    def create_enemies(self):
        """Create enemies — patrol types use linked list paths (Lab 5), random type wanders freely."""
        try:
            print("Creating enemies...")

            for data in ENEMY_SPAWN_DATA:
                try:
                    combat_kwargs = dict(
                        health=data.get("health", 60),
                        exp=data.get("exp", 30),
                        attack_damage=data.get("attack_damage", 10),
                        notice_radius=data.get("notice_radius", 200),
                        attack_radius=data.get("attack_radius", 60),
                        damage_player=self.damage_player,
                    )

                    if data["patrol_type"] == "random":
                        enemy = Enemy(
                            name=data["name"],
                            start_x=data["spawn"][0],
                            start_y=data["spawn"][1],
                            patrol_path=None,
                            patrol_type="random",
                            obstacle_sprites=self.obstacle_sprites,
                            speed=data["speed"],
                            sprite_name=data["name"].lower().replace(' ', '_'),
                            **combat_kwargs
                        )
                    else:
                        patrol_path = PatrolPath(data["patrol_type"])
                        for waypoint in data["waypoints"]:
                            x, y = waypoint
                            patrol_path.add_waypoint(x, y, wait_time=1.0)

                        enemy = Enemy(
                            name=data["name"],
                            start_x=data["spawn"][0],
                            start_y=data["spawn"][1],
                            patrol_path=patrol_path,
                            obstacle_sprites=self.obstacle_sprites,
                            speed=data["speed"],
                            sprite_name=data["name"].lower().replace(' ', '_'),
                            **combat_kwargs
                        )

                    self.enemies.add(enemy)
                    self.visible_sprites.add(enemy)
                    self.obstacle_sprites.add(enemy)
                    self.attackable_sprites.add(enemy)

                    print(f"  Created: {data['name']} ({data['patrol_type']})")
                except Exception as e:
                    print(f"  Failed to create enemy {data['name']}: {e}")

            print(f"Total enemies created: {len(self.enemies)}")
            if len(self.enemies) > 0:
                print("Press 'N' to toggle enemy debug view!")
            else:
                print("No patrol enemies created - implement Waypoint and PatrolPath to see them!")

        except ImportError as e:
            print(f"Enemies not available yet: {e}")
            print("Complete the linked list implementation in datastructures/ to enable patrol enemies!")
        except Exception as e:
            print(f"Error setting up enemies: {e}")
            print("Check your Waypoint and PatrolPath implementations!")

    def create_attack(self):
        """Spawn a weapon sprite in front of the player (called on SPACE)."""
        self.current_attack = WeaponSprite(self.player, [self.visible_sprites, self.attack_sprites])

    def destroy_attack(self):
        """Remove the weapon sprite when the attack cooldown ends."""
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None

    def player_attack_logic(self):
        """Check weapon sprite vs every enemy each frame."""
        for attack_sprite in list(self.attack_sprites):
            for enemy in pygame.sprite.spritecollide(attack_sprite, self.attackable_sprites, False):
                was_alive = enemy.health > 0
                enemy.get_damage(self.player)
                if was_alive and enemy.health <= 0:
                    self.player.exp += enemy.exp

    def damage_player(self, amount):
        """Called by enemies when they land an attack."""
        self.player.take_damage(amount)

    def update_network(self):
        """Handle network synchronization"""
        if not self.connected:
            self.connection_status = "Disconnected"
            return

        character_type = self.player.character_name.lower()
        status = self.player.status.replace("_idle", "").replace("_attack", "")
        self.network.send_update(self.player.rect.x, self.player.rect.y, character_type, status)

        updates = self.network.get_updates()

        if updates:
            self.connection_status = f"Connected - {len(updates)} players online ({self.network.serializer.upper()})"

            current_player_ids = set()

            for player_id, data in updates.items():
                current_player_ids.add(player_id)

                if player_id == self.network.my_player_id:
                    continue

                if player_id not in self.other_players:
                    character_type = data.get('character_type', '').lower()

                    all_classes = get_all_character_classes()
                    CharClass = None
                    for cls in all_classes:
                        if cls.get_display_name().lower() == character_type:
                            CharClass = cls
                            break

                    if CharClass is None:
                        CharClass = Character
                        print(f"[WARNING] Unknown character type '{character_type}', using default")

                    other_player = CharClass(
                        (data['x'], data['y']),
                        [self.visible_sprites],
                        self.obstacle_sprites,
                        player_id=player_id,
                        is_local=False
                    )
                    other_player.name = data['name']
                    self.other_players[player_id] = other_player
                    print(f"[DEBUG] Created remote player {player_id} as {character_type}")
                else:
                    other_player = self.other_players[player_id]
                    other_player.set_position(data['x'], data['y'])
                    other_player.name = data['name']
                    if 'status' in data:
                        other_player.status = data['status']

            disconnected = set(self.other_players.keys()) - current_player_ids
            for player_id in disconnected:
                self.other_players[player_id].kill()
                del self.other_players[player_id]

            self.player.other_players = list(self.other_players.values())

    def handle_events(self, events):
        """Handle pygame events (pass from main game loop)"""
        for event in events:
            self.inventory_ui.handle_event(event, self.player)

    def draw_names(self):
        """Draw player names above their heads"""
        if self.network.my_player_id is not None:
            name_text = f"{self.network.player_name} ({self.player.character_name})"
            name_surface = self.font.render(name_text, True, (0, 255, 0))
            name_rect = name_surface.get_rect(
                center=(self.player.rect.centerx, self.player.rect.top - 10)
            )
            offset_pos = self.visible_sprites.offset_from_world(name_rect.topleft)
            self.display_surface.blit(name_surface, offset_pos)

        for other_player in self.other_players.values():
            name_surface = self.font.render(other_player.name, True, (100, 100, 255))
            name_rect = name_surface.get_rect(
                center=(other_player.rect.centerx, other_player.rect.top - 10)
            )
            offset_pos = self.visible_sprites.offset_from_world(name_rect.topleft)
            self.display_surface.blit(name_surface, offset_pos)

    def draw_status(self):
        """Draw HUD: connection, hints, health bar, XP, equipped weapon."""
        status_color = (0, 255, 0) if self.connected else (255, 100, 100)
        self.display_surface.blit(
            self.font.render(self.connection_status, True, status_color), (10, 10))

        self.display_surface.blit(
            self.font.render("I: Inventory | SPACE: Attack", True, (255, 255, 255)), (10, 40))

        bar_rect = pygame.Rect(10, 70, HEALTH_BAR_WIDTH, BAR_HEIGHT)
        ratio = max(0.0, self.player.hp / max(1, self.player.max_hp))
        fill_rect = pygame.Rect(10, 70, int(HEALTH_BAR_WIDTH * ratio), BAR_HEIGHT)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bar_rect)
        pygame.draw.rect(self.display_surface, HEALTH_COLOR, fill_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bar_rect, 2)
        self.display_surface.blit(
            self.font.render(f"HP {self.player.hp}/{self.player.max_hp}", True, (255, 255, 255)),
            (10 + HEALTH_BAR_WIDTH + 8, 70))

        self.display_surface.blit(
            self.font.render(f"XP: {self.player.exp}", True, (255, 215, 0)), (10, 100))

        if self.player.equipped_weapon:
            w = self.player.equipped_weapon
            msg = f"Weapon: {w.name}  (+{w.attack_bonus} atk)"
            color = (255, 200, 100)
        else:
            msg = "Weapon: none  (open I → select weapon → Equip)"
            color = (150, 150, 150)
        self.display_surface.blit(self.font.render(msg, True, color), (10, 125))

    def _snapshot_enemies(self):
        """Capture full enemy state (position, patrol cursor, combat) for time-travel."""
        enemies = []
        for enemy in self.enemies:
            enemies.append({
                'x': enemy.rect.x,
                'y': enemy.rect.y,
                'target_waypoint': enemy.target_waypoint,
                'patrol_active': enemy.patrol_active,
                'is_waiting': enemy.is_waiting,
                'wait_timer': enemy.wait_timer,
                'patrol_current': enemy.patrol_path.current if enemy.patrol_path else None,
                'patrol_direction': enemy.patrol_path.direction if enemy.patrol_path else None,
                'wander_target': getattr(enemy, 'wander_target', None),
                'health': enemy.health,
                'combat_status': enemy.combat_status,
            })
        return {'enemies': enemies, 'player_hp': self.player.hp}

    def _restore_enemies(self, snapshot):
        """Restore full enemy state from a snapshot (also restores player HP)."""
        enemy_list = snapshot['enemies'] if isinstance(snapshot, dict) else snapshot
        for enemy, state in zip(self.enemies, enemy_list):
            enemy.rect.x = state['x']
            enemy.rect.y = state['y']
            enemy.x = float(enemy.rect.x)
            enemy.y = float(enemy.rect.y)
            enemy.hitbox.center = enemy.rect.center
            enemy.target_waypoint = state['target_waypoint']
            enemy.patrol_active = state['patrol_active']
            enemy.is_waiting = state['is_waiting']
            enemy.wait_timer = state['wait_timer']
            if enemy.patrol_path is not None:
                enemy.patrol_path.current = state['patrol_current']
                enemy.patrol_path.direction = state['patrol_direction']
            if hasattr(enemy, 'wander_target'):
                enemy.wander_target = state['wander_target']
            enemy.health = state.get('health', enemy.health)
            enemy.combat_status = state.get('combat_status', 'patrol')

        if isinstance(snapshot, dict):
            self.player.hp = snapshot.get('player_hp', self.player.hp)
            self.player.vulnerable = True

    def record_player_state(self):
        if not self.is_time_traveling and not self.connected:
            prev_size = self.time_travel.get_history_size()
            self.time_travel.record_state(
                self.player.rect.x,
                self.player.rect.y
            )
            if self.time_travel.get_history_size() > prev_size:
                self.enemy_history.append(self._snapshot_enemies())
                while len(self.enemy_history) > self.time_travel.max_history:
                    self.enemy_history.pop(0)
                self.enemy_future.clear()

    def handle_time_travel_input(self, events):
        if self.connected:
            self.is_time_traveling = False
            return

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.time_travel.can_rewind():
                    state = self.time_travel.rewind()
                    if state:
                        self.player.rect.x = state.player_x
                        self.player.rect.y = state.player_y
                        self.player.hitbox.center = self.player.rect.center
                        self.is_time_traveling = True
                        if self.enemy_history:
                            self.enemy_future.append(self.enemy_history.pop())
                            if self.enemy_history:
                                self._restore_enemies(self.enemy_history[-1])

                elif event.key == pygame.K_f and self.time_travel.can_replay():
                    state = self.time_travel.replay()
                    if state:
                        self.player.rect.x = state.player_x
                        self.player.rect.y = state.player_y
                        self.player.hitbox.center = self.player.rect.center
                        self.is_time_traveling = True
                        if self.enemy_future:
                            snapshot = self.enemy_future.pop()
                            self.enemy_history.append(snapshot)
                            self._restore_enemies(snapshot)

                else:
                    self.is_time_traveling = False

    def draw_time_travel_ui(self):
        font_small = pygame.font.Font(None, 24)

        if not self.connected:
            if self.is_time_traveling:
                font_large = pygame.font.Font(None, 48)
                text = font_large.render("⏪ TIME TRAVELING", True, (255, 100, 100))
                rect = text.get_rect(center=(WIDTH // 2, 50))
                self.display_surface.blit(text, rect)

            info = f"History: {self.time_travel.get_history_size()} | Future: {self.time_travel.get_future_size()}"
            text = font_small.render(info, True, (255, 255, 255))
            self.display_surface.blit(text, (10, 100))

            hint = "R: Rewind | F: Replay"
            text = font_small.render(hint, True, (200, 200, 200))
            self.display_surface.blit(text, (10, 130))
        else:
            text = font_small.render("Time travel disabled (multiplayer)", True, (150, 150, 150))
            self.display_surface.blit(text, (10, 100))

    def run(self, events):
        """Main update loop"""
        self.handle_events(events)
        self.handle_time_travel_input(events)
        self.handle_enemy_debug_input(events)

        self.update_network()

        self.player.update()
        for other_player in self.other_players.values():
            other_player.update()

        if not self.is_time_traveling:
            for enemy in list(self.enemies):
                enemy.enemy_update(self.player)
            self.enemies.update()
            self.player_attack_logic()

        self.visible_sprites.custom_draw(self.player)

        self.record_player_state()

        self.draw_names()
        self.draw_status()
        self.draw_time_travel_ui()
        self.draw_enemy_debug()

        if self.inventory_ui.active:
            self.inventory_ui.draw(self.display_surface)

    def handle_enemy_debug_input(self, events):
        """Handle enemy debug controls (Lab 5)."""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    self.show_enemy_debug = not self.show_enemy_debug
                    status = "ON" if self.show_enemy_debug else "OFF"
                    count = len(self.enemies)
                    print(f"Enemy debug view: {status} ({count} enemies active)")

                elif event.key == pygame.K_m:
                    reset_count = 0
                    for enemy in self.enemies:
                        enemy.reset_patrol()
                        reset_count += 1
                    print(f"Reset {reset_count} enemy patrols")

    def draw_enemy_debug(self):
        """Draw enemy debug information (Lab 5)."""
        if not self.show_enemy_debug:
            return

        if len(self.enemies) == 0:
            font = pygame.font.Font(None, 24)
            text = font.render("No patrol enemies - implement Waypoint and PatrolPath!", True, (255, 255, 100))
            self.display_surface.blit(text, (10, 160))
            return

        y_offset = 160
        for enemy in self.enemies:
            status = enemy.get_debug_status()
            font = pygame.font.Font(None, 20)
            text = font.render(status, True, (255, 255, 100))
            self.display_surface.blit(text, (10, y_offset))
            y_offset += 25

            enemy.draw_debug_info(self.display_surface,
                                  (self.visible_sprites.offset.x, self.visible_sprites.offset.y))

        instructions = [
            "Enemy Debug Controls:",
            "N: Toggle debug view",
            "M: Reset all patrols"
        ]
        font = pygame.font.Font(None, 18)
        for i, instruction in enumerate(instructions):
            color = (200, 200, 200) if i == 0 else (150, 150, 150)
            text = font.render(instruction, True, color)
            self.display_surface.blit(text, (WIDTH - 200, 10 + i * 20))


class YSortCameraGroup(pygame.sprite.Group):
    """Camera that follows player and sorts sprites by Y position"""

    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
        """Draw sprites: floor first, then grass, then everything else sorted by Y."""
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        # 1. Draw floor tiles first (bottom-most layer)
        for sprite in self.sprites():
            if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'floor':
                offset_pos = sprite.rect.topleft - self.offset
                self.display_surface.blit(sprite.image, offset_pos)

        # 2. Draw grass on top of floor
        for sprite in self.sprites():
            if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'grass':
                offset_pos = sprite.rect.topleft - self.offset
                self.display_surface.blit(sprite.image, offset_pos)

        # 3. Draw everything else (player, enemies, objects) sorted by Y
        y_sorted_sprites = [
            s for s in self.sprites()
            if not hasattr(s, 'sprite_type') or s.sprite_type not in ['floor', 'grass', 'boundary']
        ]

        for sprite in sorted(y_sorted_sprites, key=lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

    def offset_from_world(self, world_pos):
        """Convert world position to screen position"""
        return pygame.math.Vector2(world_pos) - self.offset