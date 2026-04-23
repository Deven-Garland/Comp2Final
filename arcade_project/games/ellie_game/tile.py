import pygame
from settings import *
import random
import os


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, sprite_type, surface=None, area_id=None):
        super().__init__(groups)
        self.sprite_type = sprite_type

        if surface is not None:
            self.image = surface
        else:
            self.image = self.load_image(sprite_type, area_id)

        if sprite_type == 'object':
            self.rect = self.image.get_rect(topleft=(pos[0], pos[1] - TILESIZE))
        else:
            self.rect = self.image.get_rect(topleft=pos)

        self.hitbox = self.rect.inflate(0, -10)

    def load_image(self, sprite_type, area_id):
        if sprite_type in ['boundary', 'invisible']:
            surf = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)
            surf.fill((0, 0, 0, 0))
            return surf

        # build path from this file's location, not from where python was run
        game_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(os.path.dirname(game_dir))

        if sprite_type == 'grass':
            grass_options = ['grass0', 'grass1', 'grass2', 'grass3', 'grass4', 'grass5']
            folder = random.choice(grass_options)

            path = os.path.join(
                project_dir,
                'graphics',
                'tilemap',
                'tiles',
                folder,
                'straight',
                '0',
                '0.png'
            )

            try:
                image = pygame.image.load(path).convert_alpha()
                image = pygame.transform.scale(image, (TILESIZE, TILESIZE))
                return image
            except Exception as e:
                print("FAILED TILE LOAD:", path)
                print(e)

        surf = pygame.Surface((TILESIZE, TILESIZE))
        if sprite_type == 'grass':
            surf.fill((50, 160, 50))
        elif sprite_type == 'object':
            surf.fill((120, 120, 120))
        else:
            surf.fill((255, 0, 255))

        return surf