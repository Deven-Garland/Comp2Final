"""
tile.py - Tile sprite class for the world map

Supports sprite_type values:
  'boundary'  — invisible collision wall (no image rendered)
  'grass'     — ground cover with a random grass image
  'object'    — world object (tree, rock, etc.) with a specific image
  'invisible' — alias for boundary (legacy name)

All tiles have a hitbox that is slightly inset vertically so that
the player appears to walk "behind" tall objects naturally.

Lab: Lab 6 - Sparse World Map
"""

import pygame
from settings import *


class Tile(pygame.sprite.Sprite):
    """A single tile in the world map."""

    def __init__(self, pos, groups, sprite_type, surface=pygame.Surface((TILESIZE, TILESIZE))):
        """
        Initialize a tile.

        Args:
            pos (tuple): (x, y) pixel position of the tile's top-left corner.
            groups (list): Sprite groups this tile belongs to.
            sprite_type (str): One of 'boundary', 'grass', 'object', 'invisible'.
            surface (pygame.Surface): The image to display.  For boundary/invisible
                tiles the default transparent surface is used so nothing is drawn.
        """
        super().__init__(groups)
        self.sprite_type = sprite_type
        self.image = surface

        # Objects are tall (2 tiles) — offset them upward so their base
        # sits on the correct tile.
        if sprite_type == 'object':
            self.rect = self.image.get_rect(topleft=(pos[0], pos[1] - TILESIZE))
        else:
            self.rect = self.image.get_rect(topleft=pos)

        # Slightly inset hitbox makes movement feel tighter and more natural.
        self.hitbox = self.rect.inflate(0, -10)
