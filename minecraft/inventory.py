class Inventory:
    def __init__(self, capacity=10):
        self.slots = [None] * capacity  # Each slot can hold a tuple (item_type, quantity)
        self.capacity = capacity

    def add_item(self, item_type, quantity=1):
        # Try to stack with existing items of the same type
        for i, slot in enumerate(self.slots):
            if slot and slot[0] == item_type:
                # Assuming a max stack size for future, e.g., 64. For now, infinite stack in a slot.
                self.slots[i] = (item_type, slot[1] + quantity)
                return True

        # Else, find an empty slot
        for i, slot in enumerate(self.slots):
            if slot is None:
                self.slots[i] = (item_type, quantity)
                return True

        print(f"Inventory full. Cannot add {item_type}")
        return False # Inventory full or no empty slot for new item type

    def remove_item(self, item_type, quantity=1):
        # This method removes a specific quantity of an item type,
        # searching through slots. Useful for crafting or if specific slot isn't targeted.
        for i, slot in enumerate(self.slots):
            if slot and slot[0] == item_type:
                current_quantity = slot[1]
                if current_quantity >= quantity:
                    new_quantity = current_quantity - quantity
                    if new_quantity > 0:
                        self.slots[i] = (item_type, new_quantity)
                    else:
                        self.slots[i] = None  # Remove item if quantity is zero
                    return True
                else:
                    # Not enough quantity in this slot, try next if item is in multiple slots (though current add_item stacks)
                    # For now, assume add_item fully stacks, so this means not enough total
                    return False
        return False # Item not found or not enough quantity

    def get_item_count(self, item_type):
        count = 0
        for slot in self.slots:
            if slot and slot[0] == item_type:
                count += slot[1]
        return count

    def display(self): # Console display for debugging
        print("Inventory Slots:")
        if not any(self.slots):
            print("  (all empty)")
            return
        for i, slot in enumerate(self.slots):
            if slot:
                print(f"  Slot {i}: {slot[0]} ({slot[1]})")
            else:
                print(f"  Slot {i}: [Empty]")

    def render(self, screen, font, start_x, start_y, item_color=(255, 255, 255), selected_slot_idx=None):
        y_offset = 0
        title_surface = font.render("Inventory:", True, item_color)
        screen.blit(title_surface, (start_x, start_y + y_offset))
        y_offset += title_surface.get_height()

        if not any(self.slots): # Check if all slots are None
            empty_text = font.render("  (empty)", True, item_color)
            screen.blit(empty_text, (start_x, start_y + y_offset))
            # y_offset += empty_text.get_height() # Not needed if it's the last thing
            return

        for i, slot_content in enumerate(self.slots):
            prefix = "> " if selected_slot_idx == i else "  " # Indent non-selected for alignment
            item_text = f"{prefix}"
            if slot_content:
                item_text += f"{slot_content[0]}: {slot_content[1]}"
            else:
                item_text += "[Empty]"

            item_surface = font.render(item_text, True, item_color)
            screen.blit(item_surface, (start_x, start_y + y_offset))
            y_offset += item_surface.get_height()
