"""
weapon.py - Weapon sprite displayed next to the player during an attack

The sprite's rect doubles as the hit-detection area: Level checks which enemies
collide with it each frame and calls enemy.get_damage(player).
"""

import pygame


class Weapon(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        super().__init__(groups)
        self.sprite_type = 'weapon'

        direction = player.status.split('_')[0]  # 'up' / 'down' / 'left' / 'right'

        # --- Build base image ---
        if player.equipped_weapon is not None:
            # Use the item's already-loaded graphic, scaled to a visible size
            self.image = pygame.transform.scale(player.equipped_weapon.image, (40, 40))
        else:
            # Unarmed: small fist placeholder
            self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (220, 180, 130), self.image.get_rect())

        if direction == 'left':
            self.image = pygame.transform.flip(self.image, True, False)

        # --- Position next to player in facing direction ---
        if direction == 'right':
            self.rect = self.image.get_rect(
                midleft=player.rect.midright + pygame.math.Vector2(0, 16))
        elif direction == 'left':
            self.rect = self.image.get_rect(
                midright=player.rect.midleft + pygame.math.Vector2(0, 16))
        elif direction == 'down':
            self.rect = self.image.get_rect(
                midtop=player.rect.midbottom + pygame.math.Vector2(-10, 0))
        else:  # up
            self.rect = self.image.get_rect(
                midbottom=player.rect.midtop + pygame.math.Vector2(-10, 0))
