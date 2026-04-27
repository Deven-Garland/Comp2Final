"""
inventory_ui.py - Scrolling Inventory Interface

Visual interface for displaying and interacting with inventory.
Press 'I' during game to open/close.

Author: [Student Name]
Date: [Date]
Lab: Lab 3 - Inventory System
"""

import pygame
from settings import *

class InventoryUI:
    """Scrolling inventory interface overlay."""
    
    def __init__(self, inventory):
        self.inventory = inventory
        self.active = False
        
        # UI dimensions
        self.width, self.height = 800, 600
        self.x = (WIDTH - self.width) // 2
        self.y = (HEIGTH - self.height) // 2
        
        # Grid settings
        self.grid_cols, self.grid_rows = 5, 4
        self.slot_size, self.slot_padding = 80, 10
        
        # Scrolling
        self.scroll_offset, self.max_scroll = 0, 0
        self.selected_index, self.hovered_index = None, None
        
        # Fonts
        try:
            self.title_font = pygame.font.Font(None, 36)
            self.item_font = pygame.font.Font(None, 20)
            self.desc_font = pygame.font.Font(None, 18)
        except:
            self.title_font = pygame.font.SysFont('arial', 36)
            self.item_font = pygame.font.SysFont('arial', 20)
            self.desc_font = pygame.font.SysFont('arial', 18)
        
        self.create_buttons()
    
    def create_buttons(self):
        """Create sort and action buttons"""
        button_y = self.y + 520
        button_width, button_height = 100, 30
        
        self.sort_buttons = [
            {'text': 'Name', 'rect': pygame.Rect(self.x + 20, button_y, button_width, button_height), 'action': 'sort_name'},
            {'text': 'Type', 'rect': pygame.Rect(self.x + 130, button_y, button_width, button_height), 'action': 'sort_type'},
            {'text': 'Value', 'rect': pygame.Rect(self.x + 240, button_y, button_width, button_height), 'action': 'sort_value'},
            {'text': 'Use', 'rect': pygame.Rect(self.x + 550, button_y, button_width, button_height), 'action': 'use_item'},
            {'text': 'Drop', 'rect': pygame.Rect(self.x + 660, button_y, button_width, button_height), 'action': 'drop_item'}
        ]
    
    def toggle(self):
        """Toggle inventory UI on/off"""
        self.active = not self.active
        if self.active:
            self.scroll_offset, self.selected_index = 0, None
    
    def handle_event(self, event, character=None):
        """Handle input events"""
        # Handle 'i' key to toggle inventory (even when closed!)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i:
                self.toggle()
                return True
        
        # Only handle other events when inventory is active
        if not self.active:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.toggle()
                return True
            elif event.key == pygame.K_UP:
                self.scroll_offset = max(0, self.scroll_offset - 1)
                return True
            elif event.key == pygame.K_DOWN:
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + 1)
                return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                return self.handle_click(event.pos, character)
            elif event.button == 4:
                self.scroll_offset = max(0, self.scroll_offset - 1)
                return True
            elif event.button == 5:
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + 1)
                return True
        
        elif event.type == pygame.MOUSEMOTION:
            self.hovered_index = self.get_slot_at_position(event.pos)
        
        return False
    
    def handle_click(self, pos, character):
        """Handle mouse click"""
        for button in self.sort_buttons:
            if button['rect'].collidepoint(pos):
                self.handle_button_action(button['action'], character)
                return True
        
        slot_index = self.get_slot_at_position(pos)
        if slot_index is not None:
            self.selected_index = slot_index
            return True
        
        return False
    
    def handle_button_action(self, action, character):
        """Handle button actions"""
        if action == 'sort_name':
            self.inventory.sort_by_name()
        elif action == 'sort_type':
            self.inventory.sort_by_type()
        elif action == 'sort_value':
            self.inventory.sort_by_value()
        elif action == 'use_item' and self.selected_index is not None and character:
            self.inventory.use_item(self.selected_index, character)
            self.selected_index = None
        elif action == 'drop_item' and self.selected_index is not None:
            self.inventory.remove_item_at(self.selected_index)
            self.selected_index = None
    
    def get_slot_at_position(self, pos):
        """Get inventory slot index at mouse position"""
        mx, my = pos
        grid_x, grid_y = self.x + 20, self.y + 80
        
        if mx < grid_x or my < grid_y:
            return None
        
        col = (mx - grid_x) // (self.slot_size + self.slot_padding)
        row = (my - grid_y) // (self.slot_size + self.slot_padding)
        
        if col >= self.grid_cols or row >= self.grid_rows:
            return None
        
        index = (row + self.scroll_offset) * self.grid_cols + col
        return index if index < len(self.inventory.items) else None
    
    def draw(self, surface):
        """Draw the inventory UI"""
        if not self.active:
            return
        
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGTH), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))
        
        # Main panel
        panel = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        panel.fill((40, 40, 60, 230))
        pygame.draw.rect(panel, (255, 255, 255), (0, 0, self.width, self.height), 3)
        
        # Title
        title = self.title_font.render("Inventory", True, (255, 255, 255))
        panel.blit(title, title.get_rect(center=(self.width // 2, 30)))
        
        # Count
        count_text = self.item_font.render(f"{len(self.inventory.items)}/{self.inventory.max_size} items", True, (255, 255, 255))
        panel.blit(count_text, (self.width - 150, 25))
        
        # Draw grid, details, buttons
        self.draw_item_grid(panel)
        if self.hovered_index is not None:
            self.draw_item_details(panel, self.hovered_index)
        self.draw_buttons(panel)
        if self.max_scroll > 0:
            self.draw_scroll_indicator(panel)
        
        surface.blit(panel, (self.x, self.y))
    
    def draw_item_grid(self, panel):
        """Draw grid of item slots"""
        grid_x, grid_y = 20, 80
        total_rows = (len(self.inventory.items) + self.grid_cols - 1) // self.grid_cols
        self.max_scroll = max(0, total_rows - self.grid_rows)
        
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                index = (row + self.scroll_offset) * self.grid_cols + col
                slot_x = grid_x + col * (self.slot_size + self.slot_padding)
                slot_y = grid_y + row * (self.slot_size + self.slot_padding)
                
                # Slot color
                if index == self.selected_index:
                    color = (100, 150, 100)
                elif index == self.hovered_index:
                    color = (80, 80, 100)
                else:
                    color = (60, 60, 80)
                
                slot_rect = pygame.Rect(slot_x, slot_y, self.slot_size, self.slot_size)
                pygame.draw.rect(panel, color, slot_rect)
                pygame.draw.rect(panel, (200, 200, 200), slot_rect, 2)
                
                # Draw item
                if index < len(self.inventory.items):
                    item = self.inventory.items[index]
                    img_size = self.slot_size - 10
                    try:
                        img = pygame.transform.scale(item.image, (img_size, img_size))
                        panel.blit(img, (slot_x + 5, slot_y + 5))
                    except:
                        pass
                    
                    if item.stackable and item.quantity > 1:
                        qty_text = self.item_font.render(str(item.quantity), True, (255, 255, 255))
                        qty_bg = pygame.Surface((30, 20))
                        qty_bg.fill((0, 0, 0))
                        qty_bg.set_alpha(180)
                        panel.blit(qty_bg, (slot_x + self.slot_size - 35, slot_y + self.slot_size - 25))
                        panel.blit(qty_text, (slot_x + self.slot_size - 30, slot_y + self.slot_size - 22))
    
    def draw_item_details(self, panel, index):
        """Draw item details panel"""
        if index >= len(self.inventory.items):
            return
        
        item = self.inventory.items[index]
        details_x, details_y = 550, 80
        details_width, details_height = 230, 400
        
        pygame.draw.rect(panel, (50, 50, 70), (details_x, details_y, details_width, details_height))
        pygame.draw.rect(panel, (200, 200, 200), (details_x, details_y, details_width, details_height), 2)
        
        y_offset = details_y + 10
        
        # Name
        panel.blit(self.item_font.render(item.name, True, (255, 255, 100)), (details_x + 10, y_offset))
        y_offset += 30
        
        # Type & Value
        panel.blit(self.desc_font.render(f"Type: {item.item_type}", True, (200, 200, 200)), (details_x + 10, y_offset))
        y_offset += 25
        panel.blit(self.desc_font.render(f"Value: {item.value} gold", True, (200, 200, 200)), (details_x + 10, y_offset))
        y_offset += 30
        
        # Stats
        if hasattr(item, 'attack_bonus'):
            panel.blit(self.desc_font.render(f"Attack: +{item.attack_bonus}", True, (255, 100, 100)), (details_x + 10, y_offset))
            y_offset += 25
        if hasattr(item, 'defense_bonus'):
            panel.blit(self.desc_font.render(f"Defense: +{item.defense_bonus}", True, (100, 100, 255)), (details_x + 10, y_offset))
            y_offset += 25
        
        # Description
        words = item.description.split()
        lines, current = [], []
        for word in words:
            current.append(word)
            if self.desc_font.size(' '.join(current))[0] > details_width - 20:
                current.pop()
                if current:
                    lines.append(' '.join(current))
                current = [word]
        if current:
            lines.append(' '.join(current))
        
        for i, line in enumerate(lines):
            panel.blit(self.desc_font.render(line, True, (220, 220, 220)), (details_x + 10, y_offset + i * 20))
    
    def draw_buttons(self, panel):
        """Draw buttons"""
        for button in self.sort_buttons:
            button_color = (80, 80, 120) if 'sort' in button['action'] else (120, 80, 80)
            button_rect = pygame.Rect(button['rect'].x - self.x, button['rect'].y - self.y, 
                                     button['rect'].width, button['rect'].height)
            
            pygame.draw.rect(panel, button_color, button_rect)
            pygame.draw.rect(panel, (200, 200, 200), button_rect, 2)
            
            text = self.item_font.render(button['text'], True, (255, 255, 255))
            panel.blit(text, text.get_rect(center=button_rect.center))
        
        panel.blit(self.desc_font.render("Sort by:", True, (200, 200, 200)), (20, 490))
        panel.blit(self.desc_font.render("Actions:", True, (200, 200, 200)), (550, 490))
    
    def draw_scroll_indicator(self, panel):
        """Draw scrollbar"""
        if self.max_scroll == 0:
            return
        
        indicator_x, indicator_y, indicator_height = self.width - 30, 80, 400
        pygame.draw.rect(panel, (80, 80, 80), (indicator_x, indicator_y, 10, indicator_height))
        
        thumb_height = max(20, indicator_height // (self.max_scroll + self.grid_rows))
        thumb_y = indicator_y + (indicator_height - thumb_height) * (self.scroll_offset / self.max_scroll) if self.max_scroll > 0 else indicator_y
        pygame.draw.rect(panel, (150, 150, 150), (indicator_x, int(thumb_y), 10, thumb_height))
