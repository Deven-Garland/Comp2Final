"""
main.py - Complete game with character selection and networking

Integrated version combining lab-03 and project-01
"""

import pygame
import sys
import argparse
from settings import *
from level import Level
from subcharacter import get_all_character_classes

class Button:
    def __init__(self, x, y, width, height, fg, bg, content, fontsize):
        try:
            self.font = pygame.font.Font(None, fontsize)
        except:
            self.font = pygame.font.SysFont('arial', fontsize)
        
        self.content = content
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.fg, self.bg = fg, bg

        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(self.bg)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.x, self.y

        self.text = self.font.render(self.content, True, self.fg)
        self.text_rect = self.text.get_rect(center=(self.width/2, self.height/2))
        self.image.blit(self.text, self.text_rect)

    def is_pressed(self, pos, pressed):
        if self.rect.collidepoint(pos):
            if pressed[0]:
                return True
            return False
        return False


class CharacterCard:
    """Visual card displaying a character option"""
    def __init__(self, x, y, character_class):
        self.character_class = character_class
        self.x, self.y = x, y
        self.width, self.height = 200, 280
        
        # Fonts
        try:
            self.name_font = pygame.font.Font(None, 28)
            self.desc_font = pygame.font.Font(None, 18)
        except:
            self.name_font = pygame.font.SysFont('arial', 28)
            self.desc_font = pygame.font.SysFont('arial', 18)
        
        # Load character preview image
        try:
            self.char_image = pygame.image.load(character_class.get_preview_image()).convert_alpha()
            self.char_image = pygame.transform.scale(self.char_image, (128, 128))
        except:
            # Fallback if image not found
            self.char_image = pygame.Surface((128, 128))
            self.char_image.fill((200, 200, 200))
        
        # Create card surface
        self.image = pygame.Surface([self.width, self.height])
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.x, self.y
        
        self.selected = False
        self.hovered = False
        
    def draw(self, surface):
        """Draw the character card"""
        # Background color based on state
        if self.selected:
            bg_color = (100, 200, 100)  # Green if selected
        elif self.hovered:
            bg_color = (150, 150, 150)  # Light gray if hovered
        else:
            bg_color = (80, 80, 80)     # Dark gray
        
        self.image.fill(bg_color)
        
        # Draw border
        pygame.draw.rect(self.image, (255, 255, 255), [0, 0, self.width, self.height], 3)
        
        # Draw character image (centered at top)
        img_rect = self.char_image.get_rect(center=(self.width/2, 80))
        self.image.blit(self.char_image, img_rect)
        
        # Draw character name
        name_text = self.name_font.render(self.character_class.get_display_name(), True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(self.width/2, 160))
        self.image.blit(name_text, name_rect)
        
        # Draw description (word wrap)
        desc = self.character_class.get_description()
        self.draw_wrapped_text(desc, self.desc_font, (255, 255, 255), 10, 190, self.width - 20)
        
        # Draw to screen
        surface.blit(self.image, self.rect)
    
    def draw_wrapped_text(self, text, font, color, x, y, max_width):
        """Draw text with word wrapping"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            if font.size(test_line)[0] > max_width:
                current_line.pop()
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        for i, line in enumerate(lines):
            text_surface = font.render(line, True, color)
            self.image.blit(text_surface, (x, y + i * 20))
    
    def is_hovered(self, pos):
        """Check if mouse is over this card"""
        return self.rect.collidepoint(pos)
    
    def is_clicked(self, pos, pressed):
        """Check if this card was clicked"""
        if self.rect.collidepoint(pos) and pressed[0]:
            return True
        return False


class Game:
    def __init__(self, player_name, server_host='localhost', server_port=8080, serializer='text'):
        # general setup
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGTH))
        
        try:
            self.font = pygame.font.Font(None, 48)
            self.button_font = pygame.font.Font(None, 32)
            self.small_font = pygame.font.Font(None, 20)
        except:
            self.font = pygame.font.SysFont('arial', 48)
            self.button_font = pygame.font.SysFont('arial', 32)
            self.small_font = pygame.font.SysFont('arial', 20)
        
        pygame.display.set_caption(GAME_NAME + f' - {player_name} ({serializer.upper()})')
        self.clock = pygame.time.Clock()

        # Network settings
        self.player_name = player_name
        self.server_host = server_host
        self.server_port = server_port
        self.serializer = serializer

        self.selected_character = None
        self.level = None
        self.running = True

    def character_select(self):
        """Character selection screen"""
        char_select = True
        
        title = self.font.render("Choose Your Character", True, (255, 255, 255))
        title_rect = title.get_rect(center=(WIDTH/2, 50))
        
        # Network info
        network_info = self.small_font.render(
            f"Connecting as: {self.player_name} | Server: {self.server_host}:{self.server_port} | {self.serializer.upper()}", 
            True, (200, 200, 200)
        )
        network_info_rect = network_info.get_rect(center=(WIDTH/2, 600))
        
        # Get all available character classes
        character_classes = get_all_character_classes()
        
        # Create character cards
        cards = []
        card_spacing = 220
        start_x = (WIDTH - (len(character_classes) * card_spacing - 20)) / 2
        
        for i, char_class in enumerate(character_classes):
            card = CharacterCard(start_x + i * card_spacing, 120, char_class)
            cards.append(card)
        
        # Buttons
        button_width, button_height = 300, 50
        confirm_button_rect = pygame.Rect(WIDTH/2 - button_width/2, 480, button_width, button_height)
        
        selected_card = None
        clicked_this_frame = False
        
        while char_select:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    char_select = False
                    self.running = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        char_select = False
                        self.running = False
                        pygame.quit()
                        sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    clicked_this_frame = True
            
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            
            # Update card hover states and handle clicks
            for card in cards:
                card.hovered = card.is_hovered(mouse_pos)
                if clicked_this_frame and card.is_hovered(mouse_pos):
                    # Deselect all, select this one
                    for c in cards:
                        c.selected = False
                    card.selected = True
                    selected_card = card
            
            # Check confirm button
            if clicked_this_frame and selected_card and confirm_button_rect.collidepoint(mouse_pos):
                # Start game with selected character
                self.selected_character = selected_card.character_class
                char_select = False
            
            # Reset click flag
            if not mouse_pressed[0]:
                clicked_this_frame = False
            
            # Draw
            self.screen.fill((0, 0, 0))  # Black background
            self.screen.blit(title, title_rect)
            
            # Draw cards
            for card in cards:
                card.draw(self.screen)
            
            # Draw confirm button
            if selected_card:
                button_color = (50, 150, 50) if confirm_button_rect.collidepoint(mouse_pos) else (30, 100, 30)
            else:
                button_color = (100, 100, 100)  # Grayed out if nothing selected
            
            pygame.draw.rect(self.screen, button_color, confirm_button_rect)
            pygame.draw.rect(self.screen, (255, 255, 255), confirm_button_rect, 2)
            confirm_text = self.button_font.render("Confirm", True, (255, 255, 255))
            confirm_rect = confirm_text.get_rect(center=confirm_button_rect.center)
            self.screen.blit(confirm_text, confirm_rect)
            
            # Draw network info
            self.screen.blit(network_info, network_info_rect)
            
            self.clock.tick(FPS)
            pygame.display.update()
    
    def run(self):
        """Main game loop"""
        # Character selection
        self.character_select()
        
        if not self.running or self.selected_character is None:
            return
        
        # Create level with selected character
        self.level = Level(
            self.player_name, 
            self.selected_character, 
            self.server_host, 
            self.server_port, 
            self.serializer
        )
        
        # Game loop
        while self.running:
            events = []
            for event in pygame.event.get():
                events.append(event)
                if event.type == pygame.QUIT:
                    self.level.network.disconnect()
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.level.network.disconnect()
                        pygame.quit()
                        sys.exit()

            self.screen.fill('black')
            self.level.run(events)
            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Multiplayer Game Client with Character Selection')
    parser.add_argument('name', help='Your player name')
    parser.add_argument('--server', default='localhost', 
                       help='Server hostname (default: localhost)')
    parser.add_argument('--port', type=int, default=8080, 
                       help='Server port (default: 8080)')
    parser.add_argument('--serializer', choices=['text', 'json', 'binary'], 
                       default='text',
                       help='Serialization format: text (default), json, or binary')
    
    args = parser.parse_args()
    
    print("="*50)
    print(f"Starting game as '{args.name}'")
    print(f"Connecting to {args.server}:{args.port}")
    print(f"Using {args.serializer.upper()} serialization")
    print("="*50)
    print()
    
    game = Game(args.name, args.server, args.port, args.serializer)
    game.run()
