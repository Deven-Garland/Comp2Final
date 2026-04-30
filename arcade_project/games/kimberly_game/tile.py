import pygame
from settings import *


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, sprite_type="boundary"):
        super().__init__(groups)
        self.sprite_type = sprite_type
        self.image = pygame.image.load("../../graphics/test/rock.png").convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        # Keep collision behavior consistent with other games.
        self.hitbox = self.rect.inflate(0, -10)