"""
item.py - Item class for inventory system

Defines items that can be collected and stored in inventory.
Create your own items based on Lab 1 designs.

Author: [Kimberly Olea]
Date: [2/11/26]
Lab: Lab 3 - Inventory System
"""

import pygame

class Item:
    """
    Base class for all items in the game.
    
    Items can be weapons, consumables, armor, etc.
    """
    
    def __init__(self, name, item_type, description, image_path, value=0, stackable=False, max_stack=1):
        """
        Initialize an item.
        
        Args:
            name (str): Item name
            item_type (str): Type (weapon, consumable, armor, quest, etc.)
            description (str): Item description
            image_path (str): Path to item image
            value (int): Item value/price
            stackable (bool): Can multiple be in one slot?
            max_stack (int): Maximum stack size
        """
        self.name = name
        self.item_type = item_type
        self.description = description
        self.image_path = image_path
        self.value = value
        self.stackable = stackable
        self.max_stack = max_stack
        self.quantity = 1  # Current quantity in stack
        
        # Load image
        try:
            self.image = pygame.image.load(image_path).convert_alpha()
            # Scale to standard size (64x64)
            self.image = pygame.transform.scale(self.image, (64, 64))
        except:
            # Fallback if image not found
            self.image = pygame.Surface((64, 64))
            self.image.fill((150, 150, 150))
            # Draw item type indicator
            font = pygame.font.Font(None, 20)
            text = font.render(item_type[:3].upper(), True, (0, 0, 0))
            text_rect = text.get_rect(center=(32, 32))
            self.image.blit(text, text_rect)
    
    def __str__(self):
        """String representation of item"""
        if self.stackable and self.quantity > 1:
            return f"{self.name} x{self.quantity}"
        return self.name
    
    def __repr__(self):
        """Official representation"""
        return f"Item(name='{self.name}', type='{self.item_type}', qty={self.quantity})"
    
    def use(self, character):
        """
        Use/equip the item on a character.
        Override in subclasses for specific behavior.
        
        Args:
            character: Character using the item
            
        Returns:
            bool: True if item was consumed, False otherwise
        """
        print(f"Used {self.name}")
        return False  # Not consumed by default
    
    def can_stack_with(self, other):
        """
        Check if this item can stack with another.
        
        Args:
            other (Item): Other item
            
        Returns:
            bool: True if can stack
        """
        return (self.stackable and 
                isinstance(other, Item) and
                self.name == other.name and
                self.item_type == other.item_type and
                self.quantity < self.max_stack)


class Weapon(Item):
    """Weapon items that increase attack"""
    
    def __init__(self, name, description, image_path, attack_bonus, value=0):
        super().__init__(name, "weapon", description, image_path, value, stackable=False)
        self.attack_bonus = attack_bonus
    
    def use(self, character):
        """Equip the weapon"""
        print(f"{character.character_name} equipped {self.name} (+{self.attack_bonus} attack)")
        character.attack += self.attack_bonus
        return False  # Weapons are not consumed


class Armor(Item):
    """Armor items that increase defense"""
    
    def __init__(self, name, description, image_path, defense_bonus, value=0):
        super().__init__(name, "armor", description, image_path, value, stackable=False)
        self.defense_bonus = defense_bonus
    
    def use(self, character):
        """Equip the armor"""
        print(f"{character.character_name} equipped {self.name} (+{self.defense_bonus} defense)")
        character.defense += self.defense_bonus
        return False  # Armor is not consumed


class Consumable(Item):
    """Consumable items like potions"""
    
    def __init__(self, name, description, image_path, effect_type, effect_amount, value=0, max_stack=99):
        super().__init__(name, "consumable", description, image_path, value, stackable=True, max_stack=max_stack)
        self.effect_type = effect_type  # "heal", "mana", "speed", etc.
        self.effect_amount = effect_amount
    
    def use(self, character):
        """Use the consumable"""
        if self.effect_type == "heal":
            character.hp = min(character.hp + self.effect_amount, character.max_hp)
            print(f"{character.character_name} used {self.name} and healed {self.effect_amount} HP")
        elif self.effect_type == "mana":
            if hasattr(character, 'mana'):
                character.mana = min(character.mana + self.effect_amount, character.max_mana)
                print(f"{character.character_name} restored {self.effect_amount} mana")
        
        return True  # Consumables are used up


class QuestItem(Item):
    """Special quest-related items"""
    
    def __init__(self, name, description, image_path, quest_id=None):
        super().__init__(name, "quest", description, image_path, value=0, stackable=False)
        self.quest_id = quest_id
    
    def use(self, character):
        """Quest items usually can't be used directly"""
        print(f"{self.name} is a quest item")
        return False


# =============
# EXAMPLE ITEMS
# =============

def create_example_items():
    """
    Create example items for testing.
    Create your own items based on Lab 1 designs.
    """
    items = []
    
    items.append(Item(
        name="Cool shovel",
        item_type="tool",
        description="A sturdy shovel.",
        image_path="../graphics/items/shovel.png",
    ))
    
    # Weapons
    items.append(Weapon(
        name="Steel Sword",
        description="Heavy but powerful. Deals massive damage.",
        image_path="../graphics/items/sword.png",
        attack_bonus=15,
        value=200
    ))
    
    items.append(Weapon(
        name="Magic Sword",
        description="Channels magical energy for devastating spells.",
        image_path="../graphics/items/scithersword.png",
        attack_bonus=20,
        value=300
    ))
    
    
    items.append(Weapon(
        name="Legendary Staff",
        description="Forged by ancient masters. Extremely powerful!",
        image_path="../graphics/items/staff.png",
        attack_bonus=50,
        value=1000
    ))


    items.append(Consumable(
        name="Antidote",
        description="Cures poison. Keep one handy!",
        image_path="../graphics/items/potion_yellow.png",
        effect_type="cure",
        effect_amount=0,
        value=15,
        max_stack=10
    ))
    
    items.append(Consumable(
        name="Elixir",
        description="Fully restores HP and mana. Very rare!",
        image_path="../graphics/items/potion_purple.png",
        effect_type="full_restore",
        effect_amount=999,
        value=500,
        max_stack=5
    ))
    items.append(Item(
        name="Energy Drink",
        item_type = "consumable",
        description="Quick burst of speed.",
        image_path="../graphics/items/energy_drink.png",
        value=25, 
        stackable = True,
        max_stack = 20
    ))
    items.append(Item(
        name="Adrenaline Shot",
        item_type = "consumable",
        description="Instant attack surge.",
        image_path="../graphics/items/adrenaline_shot.png",
        value=60, 
        stackable = True,
        max_stack = 10
    ))
    items.append(Item(
        name="Focus Pill",
        item_type = "consumable",
        description="Sharper timing for counters.",
        image_path="../graphics/items/focus_pill.png",
        value=40, 
        stackable = True, 
        max_stack = 10
    ))
    items.append(Item(
        name="Pain Suppressant",
        item_type = "consumable",
        description="Reduces damage briefly.",
        image_path="../graphics/items/pain_suppressant.png",
        value=55, 
        stackable = True,
        max_stack = 10    
     ))
    items.append(Item(
        name="Combat Gel",
        item_type = "consumable",
        description="Quick patch-up heal.",
        image_path="../graphics/items/combat_gel.png",
        value=20, 
        stackable = True,
        max_stack = 50
    ))
    items.append(Item(
        name="Overclock Serum",
        item_type = "consumable",
        description="High risk boost.",
        image_path="../graphics/items/overclock_serum.png",
        value=120, 
        stackable = True,
        max_stack = 5   
    ))
    items.append(Item(
        name="Guard patch",
        item_type = "armor",
        description="Temporary protective patch.",
        image_path="../graphics/items/gaurd_patch.png",
        value=20,
        stackable = False 
    )) 
    items.append(Item(
        name="Fate Crystal Shard",
        item_type = "quest",
        description="A shard that resonates with your destiny.",
        image_path="../graphics/items/fate_crystal_shard.png",
        value=0,
        stackable = False
    ))


    
    
    print(f"Created {len(items)} example items")
    return items


if __name__ == "__main__":
    # Test item creation
    print("Testing Item classes...\n")
    
    sword = Weapon("Test Sword", "A test weapon", "../graphics/test.png", attack_bonus=5, value=50)
    print(f"Created: {sword}")
    print(f"Type: {sword.item_type}")
    print(f"Attack bonus: {sword.attack_bonus}\n")
    
    potion = Consumable("Test Potion", "Heals 20 HP", "../graphics/test.png", 
                       effect_type="heal", effect_amount=20, value=10)
    print(f"Created: {potion}")
    print(f"Stackable: {potion.stackable}")
    print(f"Max stack: {potion.max_stack}\n")
    
    print("Item tests completed!")
