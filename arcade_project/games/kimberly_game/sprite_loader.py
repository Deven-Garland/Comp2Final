"""
sprite_loader.py - Unified sprite loading system for characters and NPCs

Handles two sprite organization patterns:
1. Animated: graphics/characters/wizard/down/0.png, down/1.png, etc.
2. Static: graphics/characters/wizard.png (single image for all directions)

Author: [System - Lab 5]
Date: [Date]
"""

import pygame
import os

class SpriteLoader:
    """Handles sprite loading for both characters and NPCs with flexible organization."""
    
    @staticmethod
    def _case_insensitive_match(parent_dir, target_name):
        if not os.path.isdir(parent_dir):
            return None
        direct = os.path.join(parent_dir, target_name)
        if os.path.exists(direct):
            return direct
        target_lower = target_name.lower()
        try:
            for entry in os.listdir(parent_dir):
                if entry.lower() == target_lower:
                    return os.path.join(parent_dir, entry)
        except Exception:
            return None
        return None
    
    @staticmethod
    def load_character_sprites(character_name, base_path="../../graphics/characters"):
        """
        Load sprites for a character.
        
        Args:
            character_name (str): Name of character (e.g., "wizard", "cleric")
            base_path (str): Base directory for character graphics
            
        Returns:
            dict: Animation dictionary with status keys and frame lists
        """
        return SpriteLoader._load_sprites(character_name, base_path, is_character=True)
    
    @staticmethod
    def load_enemy_sprites(enemy_name, base_path="../../graphics/enemies"):
        """
        Load sprites for an enemy.

        Args:
            enemy_name (str): Name of enemy (e.g., "forest_guard", "wandering_goblin")
            base_path (str): Base directory for enemy graphics

        Returns:
            dict: Animation dictionary with status keys and frame lists
        """
        return SpriteLoader._load_sprites(enemy_name, base_path, is_character=False)

    @staticmethod
    def load_npc_sprites(npc_name, base_path="../../graphics/npcs"):
        """Deprecated: use load_enemy_sprites instead."""
        return SpriteLoader._load_sprites(npc_name, base_path, is_character=False)
    
    @staticmethod
    def _load_sprites(name, base_path, is_character=True):
        """
        Internal method to load sprites with flexible organization.
        
        Args:
            name (str): Character/NPC name
            base_path (str): Base graphics directory
            is_character (bool): True for characters, False for NPCs
            
        Returns:
            dict: {status: [pygame.Surface, ...], ...}
        """
        name_lower = name.lower()
        module_dir = os.path.dirname(os.path.abspath(__file__))
        base_path = base_path if os.path.isabs(base_path) else os.path.normpath(os.path.join(module_dir, base_path))
        asset_alias = {
            "technical_fighter": "wizard",
            "mystic_warrior": "cleric",
            "balanced_prodigy": "thief",
            "heavy_enforcer": "hobbit",
        }
        name_lower = asset_alias.get(name_lower, name_lower)
        name_slug = name_lower.replace(" ", "_")
        animations = {}
        
        # Define all possible statuses
        statuses = ['up', 'down', 'left', 'right', 'up_idle', 'down_idle', 'left_idle', 'right_idle']
        
        # Check for animated sprites (subdirectory structure)
        character_dir = SpriteLoader._case_insensitive_match(base_path, name_slug)
        if character_dir is None:
            character_dir = os.path.join(base_path, name_slug)
        static_path = SpriteLoader._case_insensitive_match(base_path, f"{name_slug}.png")
        if static_path is None:
            static_path = os.path.join(base_path, f"{name_slug}.png")
        # Kimberly assets also exist under graphics/graphics/* in this repo.
        fallback_base = os.path.join(os.path.dirname(base_path), "graphics", os.path.basename(base_path))
        fallback_dir = SpriteLoader._case_insensitive_match(fallback_base, name_slug)
        if fallback_dir is None:
            fallback_dir = os.path.join(fallback_base, name_slug)
        fallback_static = SpriteLoader._case_insensitive_match(fallback_base, f"{name_slug}.png")
        if fallback_static is None:
            fallback_static = os.path.join(fallback_base, f"{name_slug}.png")
        
        print(f"  Checking for animated sprites at: {character_dir}")
        print(f"  Directory exists: {os.path.exists(character_dir)}")
        
        if os.path.exists(character_dir) and os.path.isdir(character_dir):
            # Animated sprites - load from subdirectories
            print(f"  Loading animated sprites for {name} from {character_dir}")
            animations = SpriteLoader._load_animated_sprites(character_dir, statuses)
            
            # Check if we actually loaded any frames
            total_frames = sum(len(frames) for frames in animations.values() if frames)
            print(f"  Total frames loaded: {total_frames}")
            
        else:
            # Static sprite - single image file
            print(f"  Checking for static sprite at: {static_path}")
            print(f"  File exists: {os.path.exists(static_path)}")
            
            if os.path.exists(static_path):
                print(f"  Loading static sprite for {name} from {static_path}")
                animations = SpriteLoader._load_static_sprite(static_path, statuses)
            elif os.path.exists(fallback_dir) and os.path.isdir(fallback_dir):
                print(f"  Loading fallback animated sprites for {name} from {fallback_dir}")
                animations = SpriteLoader._load_animated_sprites(fallback_dir, statuses)
            elif os.path.exists(fallback_static):
                print(f"  Loading fallback static sprite for {name} from {fallback_static}")
                animations = SpriteLoader._load_static_sprite(fallback_static, statuses)
            else:
                # No sprites found - create defaults
                print(f"  No sprites found for {name}, using default colored rectangles")
                animations = SpriteLoader._create_default_sprites(name, statuses, is_character)
        
        return animations
    
    @staticmethod
    def _load_animated_sprites(character_dir, statuses):
        """Load animated sprites from subdirectory structure."""
        animations = {}
        
        for status in statuses:
            animations[status] = []
            
            # Determine which directory to look in
            # idle statuses use the same sprites as movement statuses
            if '_idle' in status:
                direction = status.replace('_idle', '')  # 'up_idle' -> 'up'
            else:
                direction = status  # 'up' -> 'up'
            
            sprite_dir = os.path.join(character_dir, direction)
            
            if os.path.exists(sprite_dir) and os.path.isdir(sprite_dir):
                try:
                    # Get all PNG files and sort alphabetically
                    all_files = os.listdir(sprite_dir)
                    png_files = [f for f in all_files if f.lower().endswith('.png')]
                    png_files.sort()  # Simple alphabetical sort
                    
                    print(f"    Loading {direction}: found {len(png_files)} PNG files")
                    
                    # Load all PNG files
                    for png_file in png_files:
                        try:
                            image_path = os.path.join(sprite_dir, png_file)
                            image = pygame.image.load(image_path).convert_alpha()
                            animations[status].append(image)
                        except pygame.error as e:
                            print(f"      Error loading {image_path}: {e}")
                            
                except Exception as e:
                    print(f"    Error reading directory {sprite_dir}: {e}")
            
            # If no frames loaded, create a default
            if not animations[status]:
                default_sprite = SpriteLoader._create_single_default_sprite(direction)
                animations[status] = [default_sprite]
        
        return animations
    
    @staticmethod
    def _load_static_sprite(image_path, statuses):
        """Load single static sprite for all statuses."""
        animations = {}
        
        try:
            static_image = pygame.image.load(image_path).convert_alpha()
            
            # Use the same image for all statuses
            for status in statuses:
                animations[status] = [static_image.copy()]
                
        except pygame.error as e:
            print(f"Error loading static sprite {image_path}: {e}")
            # Create defaults if loading fails
            for status in statuses:
                default_sprite = SpriteLoader._create_single_default_sprite('down')
                animations[status] = [default_sprite]
        
        return animations
    
    @staticmethod
    def _create_default_sprites(name, statuses, is_character=True):
        """Create default colored rectangle sprites."""
        animations = {}
        
        # Different default colors for characters vs NPCs
        if is_character:
            # Character default colors (based on common RPG classes)
            colors = {
                'wizard': (100, 100, 200),
                'cleric': (200, 200, 100),
                'warrior': (200, 100, 100),
                'rogue': (100, 200, 100),
                'paladin': (200, 150, 100),
                'archer': (150, 200, 150),
            }
            default_color = colors.get(name.lower(), (150, 150, 150))
        else:
            # Enemy default colors
            colors = {
                'forest_guard': (0, 100, 0),
                'village_merchant': (100, 100, 200),
                'temple_priest': (200, 200, 200),
                'dungeon_scout': (150, 0, 0),
                'market_vendor': (200, 150, 0),
                'wandering_goblin': (80, 140, 60),
            }
            default_color = colors.get(name.lower(), (100, 100, 100))
        
        for status in statuses:
            direction = status.replace('_idle', '') if '_idle' in status else status
            sprite = SpriteLoader._create_single_default_sprite(direction, default_color)
            animations[status] = [sprite]
        
        return animations
    
    @staticmethod
    def _create_single_default_sprite(direction, color=(100, 100, 100)):
        """Create a single default sprite with directional indicator."""
        sprite = pygame.Surface((32, 32), pygame.SRCALPHA)
        sprite.fill(color)
        
        # Add directional arrow
        if direction == 'up':
            pygame.draw.polygon(sprite, (255, 255, 255), [(16, 5), (10, 15), (22, 15)])
        elif direction == 'down':
            pygame.draw.polygon(sprite, (255, 255, 255), [(16, 27), (10, 17), (22, 17)])
        elif direction == 'left':
            pygame.draw.polygon(sprite, (255, 255, 255), [(5, 16), (15, 10), (15, 22)])
        elif direction == 'right':
            pygame.draw.polygon(sprite, (255, 255, 255), [(27, 16), (17, 10), (17, 22)])
        
        # Add border
        pygame.draw.rect(sprite, (255, 255, 255), sprite.get_rect(), 2)
        
        return sprite
    
    @staticmethod
    def _extract_number(filename):
        """Extract number from filename for sorting (0.png -> 0, 1.png -> 1, etc.)."""
        try:
            # Remove extension and convert to int
            return int(os.path.splitext(filename)[0])
        except ValueError:
            # If filename doesn't start with number, sort alphabetically
            return float('inf')
    
    @staticmethod
    def get_sprite_info(name, base_path):
        """Get information about available sprites for debugging."""
        name_lower = name.lower()
        module_dir = os.path.dirname(os.path.abspath(__file__))
        base_path = base_path if os.path.isabs(base_path) else os.path.normpath(os.path.join(module_dir, base_path))
        character_dir = os.path.join(base_path, name_lower)
        static_path = os.path.join(base_path, f"{name_lower}.png")
        
        info = {
            'name': name,
            'type': 'none',
            'directories': [],
            'files': []
        }
        
        if os.path.exists(character_dir) and os.path.isdir(character_dir):
            info['type'] = 'animated'
            for item in os.listdir(character_dir):
                item_path = os.path.join(character_dir, item)
                if os.path.isdir(item_path):
                    png_count = len([f for f in os.listdir(item_path) if f.lower().endswith('.png')])
                    info['directories'].append(f"{item} ({png_count} frames)")
        elif os.path.exists(static_path):
            info['type'] = 'static'
            info['files'].append(f"{name_lower}.png")
        else:
            info['type'] = 'default'
        
        return info