BLOCK_TYPES = {
    "grass": {"color": (0, 200, 0), "hardness": 1.5, "tool_type": "shovel", "required_tool_tier": 0},
    "dirt": {"color": (139, 69, 19), "hardness": 1.0, "tool_type": "shovel", "required_tool_tier": 0},
    "stone": {"color": (128, 128, 128), "hardness": 7.5, "tool_type": "pickaxe", "required_tool_tier": 1},
    "coal_ore": {"color": (50, 50, 50), "hardness": 10.0, "tool_type": "pickaxe", "required_tool_tier": 1},
    "iron_ore": {"color": (210, 105, 30), "hardness": 15.0, "tool_type": "pickaxe", "required_tool_tier": 2},
    "wood_log": {"color": (102, 51, 0), "hardness": 3.0, "tool_type": "axe", "required_tool_tier": 0},
    "leaves": {"color": (0, 100, 0), "hardness": 0.5, "tool_type": None, "required_tool_tier": 0}, # None tool_type means any tool or hand
    "air": {"color": None, "hardness": 0, "tool_type": None, "required_tool_tier": 0}
}

class Block:
    def __init__(self, block_type_name):
        if block_type_name not in BLOCK_TYPES:
            raise ValueError(f"Unknown block type: {block_type_name}")
        self.type_name = block_type_name
        self.properties = BLOCK_TYPES[block_type_name]
        self.color = self.properties["color"]

    def __repr__(self):
        return f"Block({self.type_name})"
