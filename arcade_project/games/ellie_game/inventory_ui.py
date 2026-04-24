"""
inventory_ui.py - Scrolling Inventory Interface

Visual interface for displaying and interacting with inventory.
Press 'I' during game to open/close.

Author: [Student Name]
Date: [Date]
Lab: Lab 3 - Inventory System
"""

import pygame


class InventoryUI:
    """Scrolling inventory interface overlay."""

    def __init__(self, inventory):
        self.inventory = inventory
        self.active = False
        self.character = None   # Set by Level; needed to track equipped_weapon

        # Grid settings
        self.grid_cols, self.grid_rows = 4, 3
        self.slot_size, self.slot_padding = 70, 8

        # Scrolling
        self.scroll_offset, self.max_scroll = 0, 0
        self.selected_index, self.hovered_index = None, None

        # Fonts
        try:
            self.title_font = pygame.font.Font(None, 32)
            self.item_font  = pygame.font.Font(None, 20)
            self.desc_font  = pygame.font.Font(None, 18)
        except Exception:
            self.title_font = pygame.font.SysFont('arial', 32)
            self.item_font  = pygame.font.SysFont('arial', 20)
            self.desc_font  = pygame.font.SysFont('arial', 18)

        # These are computed fresh each draw() call from the surface size
        self._sw = 0
        self._sh = 0
        self._panel_x = 0
        self._panel_y = 0
        self._panel_w = 0
        self._panel_h = 0
        self._sort_buttons = []
        self._action_buttons = []

    def _layout(self, sw, sh):
        """Recompute layout whenever the surface size changes."""
        if sw == self._sw and sh == self._sh:
            return  # nothing changed

        self._sw = sw
        self._sh = sh

        pad = 12
        self._panel_w = sw - 2 * pad
        self._panel_h = sh - 2 * pad
        self._panel_x = pad
        self._panel_y = pad

        pw, ph = self._panel_w, self._panel_h
        bw, bh = 80, 26
        button_y = ph - bh - 10

        self._sort_buttons = [
            {'text': 'Name',  'rect': pygame.Rect(10,        button_y, bw, bh), 'action': 'sort_name'},
            {'text': 'Type',  'rect': pygame.Rect(10+bw+6,   button_y, bw, bh), 'action': 'sort_type'},
            {'text': 'Value', 'rect': pygame.Rect(10+2*(bw+6), button_y, bw, bh), 'action': 'sort_value'},
        ]
        ax = pw - 3 * (bw + 6) - 10
        self._action_buttons = [
            {'text': 'Equip', 'rect': pygame.Rect(ax,           button_y, bw, bh), 'action': 'equip_item'},
            {'text': 'Use',   'rect': pygame.Rect(ax+bw+6,      button_y, bw, bh), 'action': 'use_item'},
            {'text': 'Drop',  'rect': pygame.Rect(ax+2*(bw+6),  button_y, bw, bh), 'action': 'drop_item'},
        ]

    @property
    def _all_buttons(self):
        return self._sort_buttons + self._action_buttons

    def toggle(self):
        self.active = not self.active
        if self.active:
            self.scroll_offset = 0
            self.selected_index = None

    def handle_event(self, event, character=None):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_i:
            self.toggle()
            return True

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
                return self._handle_click(event.pos, character)
            elif event.button == 4:
                self.scroll_offset = max(0, self.scroll_offset - 1)
                return True
            elif event.button == 5:
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + 1)
                return True

        elif event.type == pygame.MOUSEMOTION:
            self.hovered_index = self._get_slot_at(event.pos)

        return False

    def _handle_click(self, pos, character):
        # Translate absolute pos to panel-local pos
        lx = pos[0] - self._panel_x
        ly = pos[1] - self._panel_y
        local = (lx, ly)

        for btn in self._all_buttons:
            if btn['rect'].collidepoint(local):
                self._handle_action(btn['action'], character)
                return True

        slot = self._get_slot_at(pos)
        if slot is not None:
            self.selected_index = slot
            return True
        return False

    def _handle_action(self, action, character):
        if action == 'sort_name':
            self.inventory.sort_by_name()
        elif action == 'sort_type':
            self.inventory.sort_by_type()
        elif action == 'sort_value':
            self.inventory.sort_by_value()
        elif action == 'equip_item' and self.selected_index is not None and self.character:
            if self.selected_index < len(self.inventory.items):
                item = self.inventory.items[self.selected_index]
                if item.item_type == 'weapon':
                    if self.character.equipped_weapon is item:
                        self.character.equipped_weapon = None
                        print(f"Unequipped {item.name}")
                    else:
                        self.character.equipped_weapon = item
                        print(f"Equipped {item.name} (+{item.attack_bonus} attack)")
        elif action == 'use_item' and self.selected_index is not None and character:
            self.inventory.use_item(self.selected_index, character)
            self.selected_index = None
        elif action == 'drop_item' and self.selected_index is not None:
            self.inventory.remove_item_at(self.selected_index)
            self.selected_index = None

    def _get_slot_at(self, abs_pos):
        """Return inventory index under abs_pos, or None."""
        mx = abs_pos[0] - self._panel_x
        my = abs_pos[1] - self._panel_y
        grid_x, grid_y = 10, 44

        if mx < grid_x or my < grid_y:
            return None

        col = (mx - grid_x) // (self.slot_size + self.slot_padding)
        row = (my - grid_y) // (self.slot_size + self.slot_padding)

        if col < 0 or col >= self.grid_cols or row < 0 or row >= self.grid_rows:
            return None

        index = (row + self.scroll_offset) * self.grid_cols + col
        return index if index < len(self.inventory.items) else None

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def draw(self, surface):
        if not self.active:
            return

        sw, sh = surface.get_size()
        self._layout(sw, sh)

        # Semi-transparent overlay
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        # Panel
        panel = pygame.Surface((self._panel_w, self._panel_h), pygame.SRCALPHA)
        panel.fill((40, 40, 60, 235))
        pygame.draw.rect(panel, (255, 255, 255), (0, 0, self._panel_w, self._panel_h), 2)

        # Title
        title = self.title_font.render("Inventory", True, (255, 255, 255))
        panel.blit(title, title.get_rect(center=(self._panel_w // 2, 20)))

        # Count
        count = self.item_font.render(
            f"{len(self.inventory.items)}/{self.inventory.max_size}", True, (200, 200, 200))
        panel.blit(count, (self._panel_w - count.get_width() - 10, 10))

        self._draw_grid(panel)
        if self.hovered_index is not None:
            self._draw_details(panel, self.hovered_index)
        self._draw_buttons(panel)
        if self.max_scroll > 0:
            self._draw_scrollbar(panel)

        surface.blit(panel, (self._panel_x, self._panel_y))

    def _draw_grid(self, panel):
        grid_x, grid_y = 10, 44
        total_rows = max(1, (len(self.inventory.items) + self.grid_cols - 1) // self.grid_cols)
        self.max_scroll = max(0, total_rows - self.grid_rows)

        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                index = (row + self.scroll_offset) * self.grid_cols + col
                sx = grid_x + col * (self.slot_size + self.slot_padding)
                sy = grid_y + row * (self.slot_size + self.slot_padding)

                is_equipped = (
                    self.character is not None and
                    self.character.equipped_weapon is not None and
                    index < len(self.inventory.items) and
                    self.inventory.items[index] is self.character.equipped_weapon
                )

                if index == self.selected_index:
                    color = (100, 150, 100)
                elif is_equipped:
                    color = (140, 110, 30)
                elif index == self.hovered_index:
                    color = (80, 80, 110)
                else:
                    color = (55, 55, 80)

                slot_rect = pygame.Rect(sx, sy, self.slot_size, self.slot_size)
                pygame.draw.rect(panel, color, slot_rect)
                pygame.draw.rect(panel, (180, 180, 180), slot_rect, 2)

                if index < len(self.inventory.items):
                    item = self.inventory.items[index]
                    img_size = self.slot_size - 8
                    try:
                        img = pygame.transform.scale(item.image, (img_size, img_size))
                        panel.blit(img, (sx + 4, sy + 4))
                    except Exception:
                        pass

                    if item.stackable and item.quantity > 1:
                        qty = self.item_font.render(str(item.quantity), True, (255, 255, 255))
                        bg = pygame.Surface((qty.get_width() + 4, qty.get_height()))
                        bg.set_alpha(160)
                        bg.fill((0, 0, 0))
                        panel.blit(bg, (sx + self.slot_size - bg.get_width() - 2,
                                        sy + self.slot_size - bg.get_height() - 2))
                        panel.blit(qty, (sx + self.slot_size - qty.get_width() - 4,
                                         sy + self.slot_size - qty.get_height() - 2))

                    if is_equipped:
                        eq = self.desc_font.render("EQ", True, (255, 220, 50))
                        panel.blit(eq, (sx + 3, sy + 3))

    def _draw_details(self, panel, index):
        if index >= len(self.inventory.items):
            return

        item = self.inventory.items[index]
        # Details panel on the right side
        dw = min(180, self._panel_w - self.grid_cols * (self.slot_size + self.slot_padding) - 30)
        dx = self._panel_w - dw - 8
        dy = 44
        dh = self.grid_rows * (self.slot_size + self.slot_padding) + 10

        pygame.draw.rect(panel, (50, 50, 72), (dx, dy, dw, dh))
        pygame.draw.rect(panel, (180, 180, 180), (dx, dy, dw, dh), 1)

        y = dy + 8
        panel.blit(self.item_font.render(item.name, True, (255, 255, 100)), (dx + 6, y)); y += 22
        panel.blit(self.desc_font.render(f"Type: {item.item_type}", True, (200, 200, 200)), (dx + 6, y)); y += 18
        panel.blit(self.desc_font.render(f"Value: {item.value}g", True, (200, 200, 200)), (dx + 6, y)); y += 22

        if hasattr(item, 'attack_bonus'):
            panel.blit(self.desc_font.render(f"Atk: +{item.attack_bonus}", True, (255, 120, 120)), (dx + 6, y)); y += 18
            if self.character and self.character.equipped_weapon is item:
                panel.blit(self.desc_font.render("[EQUIPPED]", True, (255, 220, 50)), (dx + 6, y)); y += 18
        if hasattr(item, 'defense_bonus'):
            panel.blit(self.desc_font.render(f"Def: +{item.defense_bonus}", True, (120, 120, 255)), (dx + 6, y)); y += 18

        # Word-wrap description
        words = item.description.split()
        line, lines = [], []
        for w in words:
            line.append(w)
            if self.desc_font.size(' '.join(line))[0] > dw - 12:
                line.pop()
                if line:
                    lines.append(' '.join(line))
                line = [w]
        if line:
            lines.append(' '.join(line))
        y += 4
        for ln in lines:
            if y + 16 > dy + dh:
                break
            panel.blit(self.desc_font.render(ln, True, (210, 210, 210)), (dx + 6, y))
            y += 16

    def _draw_buttons(self, panel):
        selected_is_equipped = (
            self.character is not None and
            self.character.equipped_weapon is not None and
            self.selected_index is not None and
            self.selected_index < len(self.inventory.items) and
            self.inventory.items[self.selected_index] is self.character.equipped_weapon
        )

        label_y = self._panel_h - 26 - 10 - 14
        panel.blit(self.desc_font.render("Sort:", True, (180, 180, 180)), (10, label_y))
        ax = self._panel_w - 3 * (80 + 6) - 10
        panel.blit(self.desc_font.render("Actions:", True, (180, 180, 180)), (ax, label_y))

        for btn in self._sort_buttons:
            color = (75, 75, 115)
            pygame.draw.rect(panel, color, btn['rect'])
            pygame.draw.rect(panel, (180, 180, 180), btn['rect'], 1)
            t = self.item_font.render(btn['text'], True, (255, 255, 255))
            panel.blit(t, t.get_rect(center=btn['rect'].center))

        for btn in self._action_buttons:
            if btn['action'] == 'equip_item':
                color = (150, 120, 30) if selected_is_equipped else (75, 115, 75)
            else:
                color = (115, 75, 75)
            pygame.draw.rect(panel, color, btn['rect'])
            pygame.draw.rect(panel, (180, 180, 180), btn['rect'], 1)
            t = self.item_font.render(btn['text'], True, (255, 255, 255))
            panel.blit(t, t.get_rect(center=btn['rect'].center))

    def _draw_scrollbar(self, panel):
        if self.max_scroll == 0:
            return
        bh = 26
        bar_x = self._panel_w - 14
        bar_y = 44
        bar_h = self.grid_rows * (self.slot_size + self.slot_padding)
        pygame.draw.rect(panel, (70, 70, 70), (bar_x, bar_y, 8, bar_h))
        thumb_h = max(16, bar_h // (self.max_scroll + self.grid_rows))
        thumb_y = bar_y + (bar_h - thumb_h) * self.scroll_offset // max(1, self.max_scroll)
        pygame.draw.rect(panel, (160, 160, 160), (bar_x, thumb_y, 8, thumb_h))