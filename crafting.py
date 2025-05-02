from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass

class Rarity(Enum):
    COMMON = "Common"
    UNCOMMON = "Uncommon"
    RARE = "Rare"
    EPIC = "Epic"
    LEGENDARY = "Legendary"

@dataclass
class Material:
    id: str
    name: str
    description: str
    rarity: Rarity
    value: int
    locations: List[str]  # Where it can be found
    drop_chance: float  # Chance to drop from enemies (0-1)
    required_level: int = 1

@dataclass
class CraftingRecipe:
    id: str
    name: str
    description: str
    rarity: Rarity
    required_level: int
    materials: Dict[str, int]  # material_id: quantity
    result: str  # item_id
    skill_requirement: Optional[str] = None  # Required crafting skill

class CraftingSystem:
    def __init__(self):
        self.materials: Dict[str, Material] = {}
        self.recipes: Dict[str, CraftingRecipe] = {}
        self._initialize_materials()
        self._initialize_recipes()
    
    def _initialize_materials(self):
        """Initialize all craftable materials"""
        self.materials = {
            # Common Materials
            "iron_ore": Material(
                id="iron_ore",
                name="Iron Ore",
                description="A common metal ore used in basic crafting",
                rarity=Rarity.COMMON,
                value=10,
                locations=["Dragon's Cavern", "Training Grounds"],
                drop_chance=0.3
            ),
            "wood": Material(
                id="wood",
                name="Wood",
                description="Basic crafting material from trees",
                rarity=Rarity.COMMON,
                value=5,
                locations=["Enchanted Forest"],
                drop_chance=0.4
            ),
            "leather": Material(
                id="leather",
                name="Leather",
                description="Tanned animal hide",
                rarity=Rarity.COMMON,
                value=8,
                locations=["Enchanted Forest", "Training Grounds"],
                drop_chance=0.25
            ),
            
            # Uncommon Materials
            "silver_ore": Material(
                id="silver_ore",
                name="Silver Ore",
                description="A valuable metal ore",
                rarity=Rarity.UNCOMMON,
                value=25,
                locations=["Dragon's Cavern"],
                drop_chance=0.15
            ),
            "enchanted_wood": Material(
                id="enchanted_wood",
                name="Enchanted Wood",
                description="Wood infused with magical energy",
                rarity=Rarity.UNCOMMON,
                value=20,
                locations=["Enchanted Forest"],
                drop_chance=0.1
            ),
            "magic_crystal": Material(
                id="magic_crystal",
                name="Magic Crystal",
                description="A crystal containing magical energy",
                rarity=Rarity.UNCOMMON,
                value=30,
                locations=["Arcane Library"],
                drop_chance=0.1
            ),
            
            # Rare Materials
            "gold_ore": Material(
                id="gold_ore",
                name="Gold Ore",
                description="A precious metal ore",
                rarity=Rarity.RARE,
                value=50,
                locations=["Dragon's Cavern"],
                drop_chance=0.05
            ),
            "dragon_scale": Material(
                id="dragon_scale",
                name="Dragon Scale",
                description="A scale from a mighty dragon",
                rarity=Rarity.RARE,
                value=75,
                locations=["Dragon's Cavern"],
                drop_chance=0.03
            ),
            "ancient_rune": Material(
                id="ancient_rune",
                name="Ancient Rune",
                description="A magical rune from ancient times",
                rarity=Rarity.RARE,
                value=60,
                locations=["Arcane Library"],
                drop_chance=0.02
            ),
            
            # Epic Materials
            "mithril_ore": Material(
                id="mithril_ore",
                name="Mithril Ore",
                description="A legendary metal ore",
                rarity=Rarity.EPIC,
                value=100,
                locations=["Dragon's Cavern"],
                drop_chance=0.01
            ),
            "phoenix_feather": Material(
                id="phoenix_feather",
                name="Phoenix Feather",
                description="A feather from the mythical phoenix",
                rarity=Rarity.EPIC,
                value=150,
                locations=["Enchanted Forest"],
                drop_chance=0.005
            ),
            "void_shard": Material(
                id="void_shard",
                name="Void Shard",
                description="A shard containing void energy",
                rarity=Rarity.EPIC,
                value=120,
                locations=["Thieves' Den"],
                drop_chance=0.005
            ),
            
            # Legendary Materials
            "dragon_heart": Material(
                id="dragon_heart",
                name="Dragon Heart",
                description="The heart of a mighty dragon",
                rarity=Rarity.LEGENDARY,
                value=500,
                locations=["Dragon's Cavern"],
                drop_chance=0.001
            ),
            "elder_wood": Material(
                id="elder_wood",
                name="Elder Wood",
                description="Wood from the ancient tree of life",
                rarity=Rarity.LEGENDARY,
                value=400,
                locations=["Enchanted Forest"],
                drop_chance=0.001
            ),
            "arcane_core": Material(
                id="arcane_core",
                name="Arcane Core",
                description="The core of pure magical energy",
                rarity=Rarity.LEGENDARY,
                value=450,
                locations=["Arcane Library"],
                drop_chance=0.001
            )
        }
    
    def _initialize_recipes(self):
        """Initialize all crafting recipes"""
        self.recipes = {
            # Common Recipes
            "iron_sword": CraftingRecipe(
                id="iron_sword",
                name="Iron Sword",
                description="A basic sword made of iron",
                rarity=Rarity.COMMON,
                required_level=1,
                materials={"iron_ore": 3, "wood": 1},
                result="iron_sword"
            ),
            "leather_armor": CraftingRecipe(
                id="leather_armor",
                name="Leather Armor",
                description="Basic armor made of leather",
                rarity=Rarity.COMMON,
                required_level=1,
                materials={"leather": 4, "wood": 1},
                result="leather_armor"
            ),
            
            # Uncommon Recipes
            "silver_dagger": CraftingRecipe(
                id="silver_dagger",
                name="Silver Dagger",
                description="A dagger made of silver",
                rarity=Rarity.UNCOMMON,
                required_level=3,
                materials={"silver_ore": 2, "wood": 1},
                result="silver_dagger"
            ),
            "enchanted_staff": CraftingRecipe(
                id="enchanted_staff",
                name="Enchanted Staff",
                description="A staff infused with magic",
                rarity=Rarity.UNCOMMON,
                required_level=3,
                materials={"enchanted_wood": 1, "magic_crystal": 1},
                result="enchanted_staff"
            ),
            
            # Rare Recipes
            "golden_sword": CraftingRecipe(
                id="golden_sword",
                name="Golden Sword",
                description="A sword made of gold",
                rarity=Rarity.RARE,
                required_level=5,
                materials={"gold_ore": 3, "enchanted_wood": 1},
                result="golden_sword"
            ),
            "dragon_scale_armor": CraftingRecipe(
                id="dragon_scale_armor",
                name="Dragon Scale Armor",
                description="Armor made from dragon scales",
                rarity=Rarity.RARE,
                required_level=5,
                materials={"dragon_scale": 5, "leather": 3},
                result="dragon_scale_armor"
            ),
            
            # Epic Recipes
            "mithril_sword": CraftingRecipe(
                id="mithril_sword",
                name="Mithril Sword",
                description="A legendary sword made of mithril",
                rarity=Rarity.EPIC,
                required_level=7,
                materials={"mithril_ore": 4, "phoenix_feather": 1},
                result="mithril_sword"
            ),
            "void_robe": CraftingRecipe(
                id="void_robe",
                name="Void Robe",
                description="A robe infused with void energy",
                rarity=Rarity.EPIC,
                required_level=7,
                materials={"void_shard": 3, "enchanted_wood": 2},
                result="void_robe"
            ),
            
            # Legendary Recipes
            "dragon_heart_sword": CraftingRecipe(
                id="dragon_heart_sword",
                name="Dragon Heart Sword",
                description="A sword containing the power of a dragon",
                rarity=Rarity.LEGENDARY,
                required_level=10,
                materials={"dragon_heart": 1, "mithril_ore": 5, "arcane_core": 1},
                result="dragon_heart_sword"
            ),
            "elder_staff": CraftingRecipe(
                id="elder_staff",
                name="Elder Staff",
                description="A staff made from the ancient tree of life",
                rarity=Rarity.LEGENDARY,
                required_level=10,
                materials={"elder_wood": 1, "arcane_core": 2, "phoenix_feather": 1},
                result="elder_staff"
            )
        }
    
    def get_material_by_id(self, material_id: str) -> Optional[Material]:
        """Get material by ID"""
        return self.materials.get(material_id)
    
    def get_recipe_by_id(self, recipe_id: str) -> Optional[CraftingRecipe]:
        """Get recipe by ID"""
        return self.recipes.get(recipe_id)
    
    def get_recipes_by_rarity(self, rarity: Rarity) -> List[CraftingRecipe]:
        """Get all recipes of a specific rarity"""
        return [recipe for recipe in self.recipes.values() if recipe.rarity == rarity]
    
    def get_available_recipes(self, player_level: int, materials: Dict[str, int]) -> List[CraftingRecipe]:
        """Get all recipes that can be crafted with current materials and level"""
        available = []
        for recipe in self.recipes.values():
            if player_level >= recipe.required_level:
                can_craft = True
                for material_id, quantity in recipe.materials.items():
                    if materials.get(material_id, 0) < quantity:
                        can_craft = False
                        break
                if can_craft:
                    available.append(recipe)
        return available
    
    def craft_item(self, recipe_id: str, materials: Dict[str, int]) -> Optional[str]:
        """Attempt to craft an item"""
        recipe = self.get_recipe_by_id(recipe_id)
        if not recipe:
            return None
        
        # Check if we have enough materials
        for material_id, quantity in recipe.materials.items():
            if materials.get(material_id, 0) < quantity:
                return None
        
        # Remove materials
        for material_id, quantity in recipe.materials.items():
            materials[material_id] -= quantity
        
        return recipe.result 