"""
item.py - Item class for inventory system

Defines items that can be collected and stored in inventory.

Author: Ellie Lutz
Date: 02/09/2026
Lab: Lab 3 - Inventory System
"""

import os
import pygame

# FIX: build absolute path to items folder based on this file's location
# so images load correctly regardless of launch directory
GAME_DIR = os.path.dirname(os.path.abspath(__file__))
ITEMS_DIR = os.path.join(GAME_DIR, "graphics", "items", "items")


class Item:
    """Base class for all items in the game."""

    def __init__(self, name, item_type, description, image_path, value=0, stackable=False, max_stack=1):
        """Initialize an item."""
        self.name = name
        self.item_type = item_type
        self.description = description
        self.image_path = image_path
        self.value = value
        self.stackable = stackable
        self.max_stack = max_stack
        self.quantity = 1

        try:
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (64, 64))
        except:
            self.image = pygame.Surface((64, 64))
            self.image.fill((150, 150, 150))
            font = pygame.font.Font(None, 20)
            text = font.render(item_type[:3].upper(), True, (0, 0, 0))
            text_rect = text.get_rect(center=(32, 32))
            self.image.blit(text, text_rect)

    def __str__(self):
        """Return a readable name."""
        if self.stackable and self.quantity > 1:
            return f"{self.name} x{self.quantity}"
        return self.name

    def __repr__(self):
        """Return an unambiguous representation."""
        return f"Item(name='{self.name}', type='{self.item_type}', qty={self.quantity})"

    def use(self, character):
        """Use/equip the item on a character."""
        print(f"Used {self.name}")
        return False

    def can_stack_with(self, other):
        """Return True if this item can stack with other."""
        return (
            self.stackable
            and isinstance(other, Item)
            and self.name == other.name
            and self.item_type == other.item_type
            and self.quantity < self.max_stack
        )


class Weapon(Item):
    """Weapon items that increase attack."""

    def __init__(self, name, description, image_path, attack_bonus, value=0):
        super().__init__(name, "weapon", description, image_path, value, stackable=False)
        self.attack_bonus = attack_bonus

    def use(self, character):
        """Equip the weapon."""
        print(f"{character.character_name} equipped {self.name} (+{self.attack_bonus} attack)")
        character.attack += self.attack_bonus
        return False


class Armor(Item):
    """Armor items that increase defense."""

    def __init__(self, name, description, image_path, defense_bonus, value=0):
        super().__init__(name, "armor", description, image_path, value, stackable=False)
        self.defense_bonus = defense_bonus

    def use(self, character):
        """Equip the armor."""
        print(f"{character.character_name} equipped {self.name} (+{self.defense_bonus} defense)")
        character.defense += self.defense_bonus
        return False


class Consumable(Item):
    """Consumable items like food/potions."""

    def __init__(self, name, description, image_path, effect_type, effect_amount, value=0, max_stack=99):
        super().__init__(name, "consumable", description, image_path, value, stackable=True, max_stack=max_stack)
        self.effect_type = effect_type
        self.effect_amount = effect_amount

    def use(self, character):
        """Use the consumable."""
        if self.effect_type == "heal":
            character.hp = min(character.hp + self.effect_amount, character.max_hp)
            print(f"{character.character_name} used {self.name} and healed {self.effect_amount} HP")
            return True

        if self.effect_type == "mana":
            if hasattr(character, "mana") and hasattr(character, "max_mana"):
                character.mana = min(character.mana + self.effect_amount, character.max_mana)
                print(f"{character.character_name} used {self.name} and restored {self.effect_amount} mana")
                return True
            print(f"{character.character_name} used {self.name} (no mana stat)")
            return True

        print(f"{character.character_name} used {self.name}")
        return True


class QuestItem(Item):
    """Special quest-related items."""

    def __init__(self, name, description, image_path, quest_id=None, value=0):
        super().__init__(name, "quest", description, image_path, value=value, stackable=False)
        self.quest_id = quest_id

    def use(self, character):
        """Quest items usually can't be used directly."""
        print(f"{self.name} is a quest item")
        return False


def _p(filename):
    """Helper: absolute path to an item image."""
    return os.path.join(ITEMS_DIR, filename)


def create_example_items():
    """Create example items using sprites in graphics/items/items/."""
    items = []

    # Weapons
    items.append(Weapon(
        name="Blade",
        description="A sharp blade. Simple and reliable.",
        image_path=_p("blade.png"),
        attack_bonus=12,
        value=120
    ))

    items.append(Weapon(
        name="Dagger",
        description="Fast and light. Great for quick strikes.",
        image_path=_p("dagger.png"),
        attack_bonus=8,
        value=75
    ))

    items.append(Weapon(
        name="Hammer",
        description="Heavy hits. Slow, but strong.",
        image_path=_p("hammer.png"),
        attack_bonus=15,
        value=150
    ))

    items.append(Weapon(
        name="Bow and Arrow",
        description="A ranged weapon for careful shots.",
        image_path=_p("bowandarrow.png"),
        attack_bonus=10,
        value=110
    ))

    # Consumables
    items.append(Consumable(
        name="Apple",
        description="A crisp snack. Restores a little health.",
        image_path=_p("apple.png"),
        effect_type="heal",
        effect_amount=10,
        value=5,
        max_stack=20
    ))

    items.append(Consumable(
        name="Cookie",
        description="Sugary and comforting. Restores a little health.",
        image_path=_p("cookie.png"),
        effect_type="heal",
        effect_amount=6,
        value=4,
        max_stack=30
    ))

    items.append(Consumable(
        name="Muffin",
        description="Filling and warm. Restores more health.",
        image_path=_p("muffin.png"),
        effect_type="heal",
        effect_amount=18,
        value=8,
        max_stack=15
    ))

    items.append(Consumable(
        name="Tea",
        description="Calming tea. Restores mana if your character has it.",
        image_path=_p("tea.png"),
        effect_type="mana",
        effect_amount=12,
        value=10,
        max_stack=10
    ))

    # Gems
    items.append(QuestItem(
        name="Diamond",
        description="A bright, valuable gemstone.",
        image_path=_p("diamond.png"),
        quest_id="gem_set",
        value=200
    ))

    items.append(QuestItem(
        name="Alexandrite",
        description="A rare gemstone with shifting color.",
        image_path=_p("alexandrite.png"),
        quest_id="gem_set",
        value=160
    ))

    items.append(QuestItem(
        name="Jade",
        description="A smooth green gemstone.",
        image_path=_p("jade.png"),
        quest_id="gem_set",
        value=90
    ))

    items.append(QuestItem(
        name="Opal",
        description="A shimmering gemstone with rainbow flashes.",
        image_path=_p("opal.png"),
        quest_id="gem_set",
        value=130
    ))

    items.append(QuestItem(
        name="Oynx",
        description="A light gemstone.",
        image_path=_p("oynx.png"),
        quest_id="gem_set",
        value=85
    ))

    items.append(QuestItem(
        name="Topaz",
        description="A golden gemstone that catches the light.",
        image_path=_p("topaz.png"),
        quest_id="gem_set",
        value=120
    ))

    print(f"Created {len(items)} example items")
    return items


if __name__ == "__main__":
    print("Testing Item classes with your sprites...\n")
    test_items = create_example_items()
    for it in test_items:
        print(it)
    print("\nItem tests completed!")