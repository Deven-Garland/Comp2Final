"""
inventory.py - Inventory management using ArrayList

Implement an inventory system using their custom ArrayList.
This replaces using Python's built-in list.
"""

from datastructures.array import ArrayList
from item import Item

class Inventory:
    """
    Inventory system for managing items.
    Uses custom ArrayList instead of Python list.
    """
    
    def __init__(self, max_size=20):
        """
        Initialize inventory with a maximum size.
        
        Args:
            max_size (int): Maximum allowed number of item in inventory
        """
        self.items = ArrayList()
        self.max_size = max_size
    
    def add_item(self, item):
        """
        Add an item to the inventory.
        Handles stacking for stackable items.
        
        Args:
            item (Item): Item to add
            
        Returns:
            bool: True if successful, False if inventory full
        """
        if item.stackable:
            # Try to stack with existing item
            for existing_item in self.items:
                if existing_item.can_stack_with(item):
                    # Add to existing stack
                    add_amount = min(item.quantity, existing_item.max_stack - existing_item.quantity)
                    existing_item.quantity += add_amount
                    item.quantity -= add_amount
                    
                    if item.quantity == 0:
                        return True  # All stacked
            
            # If we still have items left, add as new stack
            if item.quantity > 0:
                if len(self.items) >= self.max_size:
                    return False  # Inventory full
                self.items.append(item)
                return True
        else:
            # Not stackable - add as new item
            if len(self.items) >= self.max_size:
                return False  # Inventory full
            
            self.items.append(item)
            return True
    
    def remove_item(self, item):
        """
        Remove an item from inventory.
        
        Args:
            item (Item): Item to remove
            
        Returns:
            bool: True if successful, False if not found
        """
        try:
            self.items.remove(item)
            return True
        except ValueError:
            return False
    
    def remove_item_at(self, index):
        """
        Remove item at specific index.
        
        Args:
            index (int): Index to remove from
            
        Returns:
            Item: Removed item, or None if invalid index
        """
        try:
            return self.items.pop(index)
        except IndexError:
            return None
    
    def get_item(self, index):
        """
        Get item at index without removing it.
        
        Args:
            index (int): Index to get
            
        Returns:
            Item: Item at index, or None if invalid
        """
        try:
            return self.items[index]
        except IndexError:
            return None
    
    def use_item(self, index, character):
        """
        Use an item from inventory on a character.
        
        Args:
            index (int): Index of item to use
            character: Character using the item
            
        Returns:
            bool: True if successful
        """
        item = self.get_item(index)
        if item is None:
            return False
        
        consumed = item.use(character)
        
        if consumed:
            if item.stackable and item.quantity > 1:
                item.quantity -= 1
            else:
                self.remove_item_at(index)
        
        return True
    
    def find_item_by_name(self, name):
        """
        Find first item with given name.
        
        Args:
            name (str): Item name to search for
            
        Returns:
            tuple: (item, index) if found, (None, -1) otherwise
        """
        for i, item in enumerate(self.items):
            if item.name == name:
                return (item, i)
        return (None, -1)
    
    def find_items_by_type(self, item_type):
        """
        Find all items of a given type.
        
        Args:
            item_type (str): Type to search for
            
        Returns:
            ArrayList: ArrayList of matching items
        """
        matching = ArrayList()
        for item in self.items:
            if item.item_type == item_type:
                matching.append(item)
        return matching
    
    def is_full(self):
        """
        Check if inventory is full.
        
        Returns:
            bool: True if full
        """
        return len(self.items) >= self.max_size
    
    def is_empty(self):
        """
        Check if inventory is empty.
        
        Returns:
            bool: True if empty
        """
        return len(self.items) == 0
    
    def get_size(self):
        """
        Get number of items in inventory.
        
        Returns:
            int: Number of items
        """
        return len(self.items)
    
    def clear(self):
        """
        Remove all items from inventory.
        """
        self.items.clear()
    
    def sort_by_name(self):
        """
        Sort inventory alphabetically by item name.
        
        Note: This uses a simple bubble sort for demonstration.
        Students could implement more efficient sorting later.
        """
        n = len(self.items)
        for i in range(n):
            for j in range(0, n - i - 1):
                if self.items[j].name > self.items[j + 1].name:
                    # Swap
                    temp = self.items[j]
                    self.items[j] = self.items[j + 1]
                    self.items[j + 1] = temp
    
    def sort_by_type(self):
        """
        Sort inventory by item type.
        """
        n = len(self.items)
        for i in range(n):
            for j in range(0, n - i - 1):
                if self.items[j].item_type > self.items[j + 1].item_type:
                    # Swap
                    temp = self.items[j]
                    self.items[j] = self.items[j + 1]
                    self.items[j + 1] = temp
    
    def sort_by_value(self):
        """
        Sort inventory by item value (descending).
        """
        n = len(self.items)
        for i in range(n):
            for j in range(0, n - i - 1):
                if self.items[j].value < self.items[j + 1].value:
                    # Swap
                    temp = self.items[j]
                    self.items[j] = self.items[j + 1]
                    self.items[j + 1] = temp
    
    def get_total_value(self):
        """
        Calculate total value of all items.
        
        Returns:
            int: Total value
        """
        total = 0
        for item in self.items:
            total += item.value * item.quantity
        return total
    
    def __str__(self):
        """
        String representation of inventory.
        
        Returns:
            str: Formatted inventory list
        """
        if self.is_empty():
            return "Inventory is empty"
        
        result = f"Inventory ({len(self.items)}/{self.max_size}):\n"
        for i, item in enumerate(self.items):
            result += f"  {i+1}. {item}\n"
        return result
    
    def __repr__(self):
        """Official representation"""
        return f"Inventory(size={len(self.items)}/{self.max_size})"
    
    def __iter__(self):
        """Make inventory iterable"""
        return iter(self.items)


# ============================================
# TESTING
# ============================================

if __name__ == "__main__":
    from item import Weapon, Armor, Consumable
    
    print("Testing Inventory system...\n")
    
    # Create inventory
    inventory = Inventory(max_size=10)
    print(f"Created: {repr(inventory)}\n")
    
    # Add items
    print("Adding items...")
    sword = Weapon("Iron Sword", "A sturdy blade", "../../graphics/test.png", attack_bonus=10, value=100)
    inventory.add_item(sword)
    
    armor = Armor("Leather Armor", "Light protection", "../../graphics/test.png", defense_bonus=5, value=80)
    inventory.add_item(armor)
    
    potion1 = Consumable("Health Potion", "Heals 50 HP", "../../graphics/test.png", 
                        effect_type="heal", effect_amount=50, value=25)
    inventory.add_item(potion1)
    
    potion2 = Consumable("Health Potion", "Heals 50 HP", "../../graphics/test.png", 
                        effect_type="heal", effect_amount=50, value=25)
    potion2.quantity = 3
    inventory.add_item(potion2)  # Should stack with potion1
    
    print(inventory)
    
    # Test finding
    print("\nFinding items...")
    item, idx = inventory.find_item_by_name("Iron Sword")
    if item:
        print(f"Found '{item.name}' at index {idx}")
    
    # Test filtering
    print("\nFinding all weapons...")
    weapons = inventory.find_items_by_type("weapon")
    for weapon in weapons:
        print(f"  - {weapon.name}")
    
    # Test sorting
    print("\nSorting by name...")
    inventory.sort_by_name()
    print(inventory)
    
    # Test total value
    print(f"\nTotal inventory value: {inventory.get_total_value()} gold")
    
    print("\nInventory tests completed!")