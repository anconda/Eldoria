import time
import random
from typing import List, Dict, Optional, Set
from save_manager import SaveManager
from achievements import AchievementSystem, AchievementCategory
from crafting import CraftingSystem, Rarity, Material, CraftingRecipe
from enum import Enum
from dataclasses import dataclass
from npcs import NPCS, NPC
from lore import LoreSystem, Faction, Era, WorldEvent, FactionInfo  # Add this import

#this is a text based RPG game that was based on my novel "the amulet of eldoria" and D&D one of my favorite games
#the game is very simple and is meant to be a fun and easy game to play
#i've used all my knowledge of python (even things i learned outside of DECI) to make this game so i hope you enjoy it
#made with love by Ahmed

# Globals
# Luck System
class LuckSystem:
    def __init__(self):
        self.base_luck = 5
        self.daily_luck = 0
        self.last_update = None
    
    def update_daily_luck(self):
        current_date = time.strftime("%Y-%m-%d")
        if self.last_update != current_date:
            self.daily_luck = random.randint(-3, 3)
            self.last_update = current_date
    
    def get_total_luck(self):
        self.update_daily_luck()
        return self.base_luck + self.daily_luck
    
    def apply_luck_bonus(self, value: int) -> int:
        luck_modifier = (self.get_total_luck() / 10)  # Convert luck to a percentage
        return int(value * (1 + luck_modifier))

# Status Effect System
class StatusEffect:
    def __init__(self, name: str, duration: int, effect_type: str, value: int, description: str):
        self.name = name
        self.duration = duration
        self.effect_type = effect_type  # "buff", "debuff", "dot", "hot"
        self.value = value
        self.description = description
    
    def apply(self, target):
        if self.effect_type == "buff":
            if self.name == "Strength Boost":
                target.stats["strength"] += self.value
            elif self.name == "Magic Boost":
                target.stats["magic"] += self.value
            elif self.name == "Agility Boost":
                target.stats["agility"] += self.value
            elif self.name == "Defense Boost":
                target.stats["defense"] += self.value
        elif self.effect_type == "debuff":
            if self.name == "Weakened":
                target.stats["strength"] -= self.value
            elif self.name == "Dazed":
                target.stats["magic"] -= self.value
            elif self.name == "Slowed":
                target.stats["agility"] -= self.value
            elif self.name == "Vulnerable":
                target.stats["defense"] -= self.value
        elif self.effect_type == "dot":
            target.health -= self.value
            print(f"💥 {target.name} takes {self.value} damage from {self.name}!")
        elif self.effect_type == "hot":
            target.health = min(target.max_health, target.health + self.value)
            print(f"💚 {target.name} recovers {self.value} health from {self.name}!")
    
    def remove(self, target):
        if self.effect_type == "buff":
            if self.name == "Strength Boost":
                target.stats["strength"] -= self.value
            elif self.name == "Magic Boost":
                target.stats["magic"] -= self.value
            elif self.name == "Agility Boost":
                target.stats["agility"] -= self.value
            elif self.name == "Defense Boost":
                target.stats["defense"] -= self.value
        elif self.effect_type == "debuff":
            if self.name == "Weakened":
                target.stats["strength"] += self.value
            elif self.name == "Dazed":
                target.stats["magic"] += self.value
            elif self.name == "Slowed":
                target.stats["agility"] += self.value
            elif self.name == "Vulnerable":
                target.stats["defense"] += self.value
    
    def update(self, target):
        self.duration -= 1
        if self.duration <= 0:
            self.remove(target)
            return True
        return False

class Gender(Enum):
    MALE = "Male"
    FEMALE = "Female"
    NON_BINARY = "Non-binary"

class Background(Enum):
    NOBLE = "Noble"
    COMMONER = "Commoner"
    OUTCAST = "Outcast"
    SCHOLAR = "Scholar"
    WARRIOR = "Warrior"
    ROGUE = "Rogue"

@dataclass
class Appearance:
    hair_color: str
    eye_color: str
    skin_tone: str
    height: str
    build: str

class Player:
    def __init__(self):
        self.name = ""
        self.gender: Optional[Gender] = None
        self.appearance: Optional[Appearance] = None
        self.background: Optional[Background] = None
        self.level = 1
        self.exp = 0
        self.max_health = 50
        self.health = 50
        self.gold = 20
        self.inventory: List[str] = []
        self.player_class = ""
        self.total_score = 0  # Added to track overall score
        self.turns_taken = 0  # Added to track number of turns
        self.stats = {
            "strength": 5,
            "magic": 5,
            "agility": 5,
            "defense": 5
        }
        self.abilities: List[str] = []
        self.active_quests: List[Dict] = []
        self.completed_quests: List[str] = []
        self.luck_system = LuckSystem()
        self.status_effects: List[StatusEffect] = []  # New: track status effects
        self.equipment = {  # New: equipment slots
            "weapon": None,
            "armor": None,
            "accessory": None
        }
        self.skill_points = 0  # New: skill points for skill tree
        self.skill_tree = {  # New: skill tree
            "passive": [],
            "active": []
        }
        self.combo_counter = 0  # New: for combo attacks
        self.last_ability_used = None  # New: for combo attacks
        self.visited_locations = set()  # Track visited locations
        self.trades_completed = 0  # Track completed trades
        self.consecutive_lucky_days = 0  # Track consecutive lucky days
        self.achievement_system = AchievementSystem()  # Add achievement system
        self.materials: Dict[str, int] = {}  # material_id: quantity
        self.crafting_system = CraftingSystem()  # Add crafting system
        self.lore_system = LoreSystem()
        self.known_locations: Set[str] = set()
        self.known_npcs: Set[str] = set()
        self.quest_history: List[str] = []

player = Player()

# Shop items
SHOP_ITEMS = {
    "Health Potion": {"cost": 15, "description": "Restores 20 HP", "type": "consumable"},
    "Steel Armor": {"cost": 30, "description": "+3 defense", "type": "armor"},
    "Magic Scroll": {"cost": 25, "description": "Deals 15 magic damage", "type": "consumable"},
    "Sharp Blade": {"cost": 35, "description": "+3 strength", "type": "weapon"},
    "Enchanted Amulet": {"cost": 50, "description": "+2 to all stats", "type": "accessory"},
    "Mage Staff": {"cost": 40, "description": "+3 magic", "type": "weapon"},
    "Rogue Dagger": {"cost": 35, "description": "+3 agility", "type": "weapon"},
    "Leather Armor": {"cost": 25, "description": "+2 defense, +1 agility", "type": "armor"},
    "Magic Robes": {"cost": 30, "description": "+2 defense, +1 magic", "type": "armor"},
    "Lucky Charm": {"cost": 45, "description": "+3 luck", "type": "accessory"}
}

# Available quests
AVAILABLE_QUESTS = {
    "Forest Guardian": {
        "description": "Defeat 3 Forest Creatures to protect the Enchanted Forest",
        "reward": {"gold": 40, "exp": 30, "item": "Forest Essence"},
        "target": {"enemy": "Forest Creature", "count": 3}
    },
    "Dragon Hunter": {
        "description": "Defeat the Flame Dragon and bring back its fang",
        "reward": {"gold": 100, "exp": 50, "item": "Dragon Scale Armor"},
        "target": {"enemy": "Flame Dragon", "count": 1}
    },
    "Library Scholar": {
        "description": "Find 2 magical tomes in the Arcane Library",
        "reward": {"gold": 30, "exp": 25, "item": "Ancient Spellbook"},
        "target": {"item": "Magical Tome", "count": 2}
    }
}

# NPC System
class NPC:
    def __init__(self, name: str, role: str, location: str, dialogue: Dict[str, str], trades: Dict[str, Dict] = None):
        self.name = name
        self.role = role
        self.location = location
        self.dialogue = dialogue
        self.trades = trades or {}
        self.friendship = 0
        self.status_effects: List[StatusEffect] = []  # New: NPCs can have status effects too

# Available NPCs
NPCS = {
    "Master Eldric": NPC(
        "Master Eldric",
        "Archmage",
        "Arcane Library",
        {
            "greeting": "Welcome, seeker of knowledge.",
            "quest": "I need help organizing these ancient tomes...",
            "friendly": "You've proven yourself a dedicated student.",
            "trade": "I have some rare scrolls, if you're interested."
        },
        {
            "Advanced Spellbook": {"cost": 45, "requires_friendship": 3},
            "Mana Crystal": {"cost": 30, "requires_friendship": 1}
        }
    ),
    "Sir Galahad": NPC(
        "Sir Galahad",
        "Knight Commander",
        "Training Grounds",
        {
            "greeting": "Hail, fellow warrior!",
            "quest": "Care to spar with the recruits?",
            "friendly": "You've got the makings of a true knight.",
            "trade": "I can teach you some combat techniques."
        },
        {
            "Advanced Combat Manual": {"cost": 45, "requires_friendship": 3},
            "Knight's Insignia": {"cost": 30, "requires_friendship": 1}
        }
    ),
    "Shadow": NPC(
        "Shadow",
        "Master Thief",
        "Enchanted Forest",
        {
            "greeting": "Keep your voice down...",
            "quest": "I've got a... delicate matter to discuss.",
            "friendly": "You're one of us now.",
            "trade": "Got some special items, if you can keep a secret."
        },
        {
            "Smoke Bombs": {"cost": 45, "requires_friendship": 3},
            "Lockpick Set": {"cost": 30, "requires_friendship": 1}
        }
    ),
    "Druidess Sylva": NPC(
        "Druidess Sylva",
        "High Druid",
        "Sacred Grove",
        {
            "greeting": "Nature welcomes you, traveler.",
            "quest": "The balance of nature is disturbed...",
            "friendly": "You understand the ways of nature.",
            "trade": "I can teach you the secrets of the forest."
        },
        {
            "Nature's Blessing": {"cost": 45, "requires_friendship": 3},
            "Herbal Remedies": {"cost": 30, "requires_friendship": 1}
        }
    ),
    "Guildmaster Goldhand": NPC(
        "Guildmaster Goldhand",
        "Merchant Leader",
        "Grand Market",
        {
            "greeting": "Welcome to the heart of commerce!",
            "quest": "I need someone to handle a delicate trade...",
            "friendly": "You've proven yourself a trustworthy trader.",
            "trade": "Looking for something special?"
        },
        {
            "Merchant's License": {"cost": 45, "requires_friendship": 3},
            "Trade Routes Map": {"cost": 30, "requires_friendship": 1}
        }
    ),
    "Dragon Priest Malakar": NPC(
        "Dragon Priest Malakar",
        "Cult Leader",
        "Dragon's Lair",
        {
            "greeting": "The dragon's fire burns within you...",
            "quest": "The ancient ones stir in their slumber...",
            "friendly": "You understand the true power of dragons.",
            "trade": "I have relics of the ancient ones..."
        },
        {
            "Dragon Scale": {"cost": 45, "requires_friendship": 3},
            "Dragon's Breath Potion": {"cost": 30, "requires_friendship": 1}
        }
    )
}

# Delay function
def pause(duration=1.2):
    time.sleep(duration)

def print_animated(text, delay=0.03, end_pause=0.5):
    """Print text with a typing animation effect"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()  # New line at the end
    time.sleep(end_pause)  # Pause after the text is complete

def print_header(text, width=50):
    print_border(width)
    padding = (width - len(text)) // 2
    print_animated(" " * padding + text, delay=0.02, end_pause=0.3)
    print_border(width)

def print_menu_item(number, text):
    print_animated(f"│ {number}. {text}", delay=0.02, end_pause=0.1)

def print_border(width=50):
    print("─" * width)
    time.sleep(0.2)  # Short pause after border

def level_up():
    player.level += 1
    player.max_health += 10
    player.health = player.max_health
    player.skill_points += 1  # Gain a skill point on level up
    
    print_animated(f"\n🌟 LEVEL UP! You are now level {player.level}!", delay=0.05, end_pause=1.0)
    pause(0.8)
    print_animated("Choose a stat to increase:", delay=0.03, end_pause=0.5)
    print_animated("1. Strength (+2)", delay=0.03, end_pause=0.3)
    print_animated("2. Magic (+2)", delay=0.03, end_pause=0.3)
    print_animated("3. Agility (+2)", delay=0.03, end_pause=0.3)
    print_animated("4. Defense (+2)", delay=0.03, end_pause=0.5)
    
    while True:
        choice = input("Enter 1-4: ")
        if choice in ["1", "2", "3", "4"]:
            if choice == "1":
                player.stats["strength"] += 2
                print_animated("Your strength has increased!", delay=0.03, end_pause=0.5)
            elif choice == "2":
                player.stats["magic"] += 2
                print_animated("Your magic has increased!", delay=0.03, end_pause=0.5)
            elif choice == "3":
                player.stats["agility"] += 2
                print_animated("Your agility has increased!", delay=0.03, end_pause=0.5)
            else:
                player.stats["defense"] += 2
                print_animated("Your defense has increased!", delay=0.03, end_pause=0.5)
            break
        else:
            print_animated("Invalid choice!", delay=0.03, end_pause=0.5)
    
    # Unlock new ability at level 3
    if player.level == 3:
        unlock_new_ability()
    
    # Offer skill tree options if player has skill points
    if player.skill_points > 0:
        print_animated(f"\n🎯 You have {player.skill_points} skill point(s) to spend!", delay=0.04, end_pause=0.8)
        print_animated("Would you like to spend skill points now? (yes/no)", delay=0.03, end_pause=0.5)
        choice = input().lower()
        if choice == "yes":
            spend_skill_points()
    check_achievements()

def spend_skill_points():
    # Define available skills based on player class
    available_skills = {
        "Mage": {
            "passive": [
                {"name": "Arcane Mastery", "description": "Increases magic damage by 10%", "cost": 1},
                {"name": "Mana Regeneration", "description": "Recover 5 mana per turn", "cost": 1},
                {"name": "Spell Penetration", "description": "Ignore 20% of enemy magic resistance", "cost": 1}
            ],
            "active": [
                {"name": "Teleport", "description": "Instantly move to a random location", "cost": 1},
                {"name": "Time Stop", "description": "Freeze time for 1 turn", "cost": 2},
                {"name": "Summon Elemental", "description": "Summon a powerful elemental to fight for you", "cost": 2}
            ]
        },
        "Knight": {
            "passive": [
                {"name": "Combat Mastery", "description": "Increases physical damage by 10%", "cost": 1},
                {"name": "Iron Will", "description": "Take 10% less damage", "cost": 1},
                {"name": "Battle Hardened", "description": "Gain 5 HP per turn in combat", "cost": 1}
            ],
            "active": [
                {"name": "Charge", "description": "Dash to the enemy and deal extra damage", "cost": 1},
                {"name": "Battle Cry", "description": "Increase all stats by 20% for 3 turns", "cost": 2},
                {"name": "Divine Shield", "description": "Become invulnerable for 1 turn", "cost": 2}
            ]
        },
        "Rogue": {
            "passive": [
                {"name": "Stealth Mastery", "description": "20% chance to avoid attacks", "cost": 1},
                {"name": "Critical Strike", "description": "15% chance to deal double damage", "cost": 1},
                {"name": "Evasion", "description": "Dodge chance increased by 10%", "cost": 1}
            ],
            "active": [
                {"name": "Smoke Screen", "description": "Become invisible for 2 turns", "cost": 1},
                {"name": "Death Mark", "description": "Mark an enemy to take 30% more damage", "cost": 2},
                {"name": "Shadow Clone", "description": "Create a clone that fights alongside you", "cost": 2}
            ]
        }
    }
    
    while player.skill_points > 0:
        print(f"\n🎯 Available Skill Points: {player.skill_points}")
        print("\nAvailable Skills:")
        
        # Display passive skills
        print("\n🔮 Passive Skills:")
        for i, skill in enumerate(available_skills[player.player_class]["passive"], 1):
            if skill["name"] not in player.skill_tree["passive"]:
                print(f"{i}. {skill['name']} ({skill['cost']} point(s)): {skill['description']}")
        
        # Display active skills
        print("\n⚔️ Active Skills:")
        for i, skill in enumerate(available_skills[player.player_class]["active"], 1):
            if skill["name"] not in player.skill_tree["active"]:
                print(f"{i + len(available_skills[player.player_class]['passive'])}. {skill['name']} ({skill['cost']} point(s)): {skill['description']}")
        
        print(f"{len(available_skills[player.player_class]['passive']) + len(available_skills[player.player_class]['active']) + 1}. Exit")
        
        choice = input("\nEnter the number of the skill you want to learn (or the last number to exit): ")
        
        if choice.isdigit() and 1 <= int(choice) <= len(available_skills[player.player_class]["passive"]) + len(available_skills[player.player_class]["active"]) + 1:
            if int(choice) == len(available_skills[player.player_class]["passive"]) + len(available_skills[player.player_class]["active"]) + 1:
                break
            
            # Determine if it's a passive or active skill
            if int(choice) <= len(available_skills[player.player_class]["passive"]):
                skill = available_skills[player.player_class]["passive"][int(choice) - 1]
                skill_type = "passive"
            else:
                skill = available_skills[player.player_class]["active"][int(choice) - len(available_skills[player.player_class]["passive"]) - 1]
                skill_type = "active"
            
            if player.skill_points >= skill["cost"]:
                player.skill_points -= skill["cost"]
                player.skill_tree[skill_type].append(skill["name"])
                print(f"\n✨ You learned {skill['name']}!")
                
                # Apply passive skill effects immediately
                if skill_type == "passive":
                    apply_passive_skill(skill["name"])
            else:
                print("❌ Not enough skill points!")
        else:
            print("❌ Invalid choice!")

def unlock_new_ability():
    print_animated("\n🌟 You've unlocked a new ability!", delay=0.05, end_pause=0.8)
    pause(0.5)
    
    if player.player_class == "Mage":
        player.abilities.append("Arcane Explosion")
        print_animated("You learned Arcane Explosion - A powerful area attack!", delay=0.04, end_pause=0.8)
    elif player.player_class == "Knight":
        player.abilities.append("Shield Wall")
        print_animated("You learned Shield Wall - Temporarily increases defense!", delay=0.04, end_pause=0.8)
    elif player.player_class == "Rogue":
        player.abilities.append("Shadow Step")
        print_animated("You learned Shadow Step - Become invisible for one turn!", delay=0.04, end_pause=0.8)
    
    pause(0.8)

def gain_exp(amount: int):
    player.exp += amount
    player.total_score += amount  # Update total score when gaining exp
    print_animated(f"+{amount} EXP!", delay=0.03, end_pause=0.5)
    print_animated(f"Current Score: {player.total_score}", delay=0.03, end_pause=0.5)
    if player.exp >= player.level * 20:
        player.exp = 0
        level_up()

def apply_passive_skill(skill_name):
    if skill_name == "Arcane Mastery":
        # This will be applied in combat calculations
        pass
    elif skill_name == "Mana Regeneration":
        # This will be applied in combat
        pass
    elif skill_name == "Spell Penetration":
        # This will be applied in combat calculations
        pass
    elif skill_name == "Combat Mastery":
        # This will be applied in combat calculations
        pass
    elif skill_name == "Iron Will":
        # This will be applied in combat calculations
        pass
    elif skill_name == "Battle Hardened":
        # This will be applied in combat
        pass
    elif skill_name == "Stealth Mastery":
        # This will be applied in combat calculations
        pass
    elif skill_name == "Critical Strike":
        # This will be applied in combat calculations
        pass
    elif skill_name == "Evasion":
        # This will be applied in combat calculations
        pass

def shop():
    print_header("💰 Welcome to the Mystic Shop! 💰")
    print(f"👛 Your gold: {player.gold}")
    print("\n📦 Available Items:")
    print_border(40)
    
    # Group items by type
    items_by_type = {
        "weapon": [],
        "armor": [],
        "accessory": [],
        "consumable": [],
        "material": []  # Add materials category
    }
    
    # Add materials to shop
    for material_id, material in player.crafting_system.materials.items():
        if material.rarity in [Rarity.COMMON, Rarity.UNCOMMON]:  # Only sell common and uncommon materials
            items_by_type["material"].append((material.name, {
                "cost": material.value,
                "description": material.description,
                "type": "material",
                "id": material_id
            }))
    
    for item, details in SHOP_ITEMS.items():
        items_by_type[details["type"]].append((item, details))
    
    # Display items by category
    print("🗡️ Weapons:")
    for item, details in items_by_type["weapon"]:
        print(f"🎁 {item}: {details['cost']} 💰 - {details['description']}")
    
    print("\n🛡️ Armor:")
    for item, details in items_by_type["armor"]:
        print(f"🎁 {item}: {details['cost']} 💰 - {details['description']}")
    
    print("\n💍 Accessories:")
    for item, details in items_by_type["accessory"]:
        print(f"🎁 {item}: {details['cost']} 💰 - {details['description']}")
    
    print("\n🧪 Consumables:")
    for item, details in items_by_type["consumable"]:
        print(f"🎁 {item}: {details['cost']} 💰 - {details['description']}")
    
    # Display materials
    print("\n📦 Materials:")
    for item, details in items_by_type["material"]:
        print(f"🎁 {item}: {details['cost']} 💰 - {details['description']}")
    
    print_border(40)
    
    # Display current equipment
    print("\n🎒 Your Equipment:")
    print(f"Weapon: {player.equipment['weapon'] or 'None'}")
    print(f"Armor: {player.equipment['armor'] or 'None'}")
    print(f"Accessory: {player.equipment['accessory'] or 'None'}")
    print_border(40)
    
    choice = input("\n🛍️ What would you like to buy? (or 'exit' to leave): ").title()
    if choice in SHOP_ITEMS:
        item_details = SHOP_ITEMS[choice]
        if player.gold >= item_details["cost"]:
            # Handle equipment items
            if item_details["type"] in ["weapon", "armor", "accessory"]:
                # Unequip current item if any
                current_item = player.equipment[item_details["type"]]
                if current_item:
                    # Add the unequipped item back to inventory
                    player.inventory.append(current_item)
                
                # Equip the new item
                player.equipment[item_details["type"]] = choice
                player.gold -= item_details["cost"]
                print(f"\n✨ You equipped {choice}!")
            else:
                # Handle consumable items
                player.gold -= item_details["cost"]
                player.inventory.append(choice)
                print(f"\n✨ You bought {choice}!")
            
            print(f"💰 Remaining gold: {player.gold}")
            check_quest_completion("item", choice)
            player.trades_completed += 1
            check_achievements()
        else:
            print("❌ Not enough gold!")
    elif choice in [item[0] for item in items_by_type["material"]]:
        # Handle material purchase
        material_details = next(details for item, details in items_by_type["material"] if item == choice)
        if player.gold >= material_details["cost"]:
            player.gold -= material_details["cost"]
            if material_details["id"] not in player.materials:
                player.materials[material_details["id"]] = 0
            player.materials[material_details["id"]] += 1
            print(f"\n✨ You bought {choice}!")
            print(f"💰 Remaining gold: {player.gold}")
            check_achievements()
        else:
            print("❌ Not enough gold!")
    elif choice != "Exit":
        print("❌ Invalid item!")

def accept_quest(quest_name: str):
    if quest_name in AVAILABLE_QUESTS and quest_name not in player.active_quests and quest_name not in player.completed_quests:
        quest = AVAILABLE_QUESTS[quest_name].copy()
        quest["progress"] = 0
        player.active_quests.append(quest)
        print(f"\n✅ Quest accepted: {quest_name}")
        print(f"Description: {quest['description']}")
    else:
        print("This quest is not available.")

def check_quest_completion(type: str, value: str):
    for quest in player.active_quests[:]:  # Use a copy to avoid modification during iteration
        if type == "enemy" and "enemy" in quest["target"] and quest["target"]["enemy"] == value:
            quest["progress"] += 1
            if quest["progress"] >= quest["target"]["count"]:
                complete_quest(quest)
        elif type == "item" and "item" in quest["target"] and quest["target"]["item"] == value:
            quest["progress"] += 1
            if quest["progress"] >= quest["target"]["count"]:
                complete_quest(quest)

def complete_quest(quest):
    print(f"\n🎉 Quest completed: {quest['description']}")
    player.gold += quest["reward"]["gold"]
    gain_exp(quest["reward"]["exp"])
    if "item" in quest["reward"]:
        player.inventory.append(quest["reward"]["item"])
        print(f"You received {quest['reward']['item']}!")
    
    # Remove from active quests and add to completed
    player.active_quests.remove(quest)
    player.completed_quests.append(quest["description"])
    check_achievements()
    
    # Learn about related events
    for event in player.lore_system.world_events:
        if any(faction in event.related_factions for faction in player.lore_system.faction_info.keys()):
            player.lore_system.learn_event(event.name)
    
    # Update faction relations
    if "Council of Mages" in quest["description"]:
        player.lore_system.update_faction_relation(Faction.COUNCIL_OF_MAGES, 10)
    elif "Knights of Eldoria" in quest["description"]:
        player.lore_system.update_faction_relation(Faction.KNIGHTS_OF_ELDORIA, 10)
    elif "Shadow Thieves" in quest["description"]:
        player.lore_system.update_faction_relation(Faction.SHADOW_THIEVES, 10)
    elif "Druid Circle" in quest["description"]:
        player.lore_system.update_faction_relation(Faction.DRUID_CIRCLE, 10)
    elif "Merchant Guild" in quest["description"]:
        player.lore_system.update_faction_relation(Faction.MERCHANT_GUILD, 10)
    elif "Cult of the Dragon" in quest["description"]:
        player.lore_system.update_faction_relation(Faction.CULT_OF_THE_DRAGON, 10)

def quest_board():
    print_header("📜 QUEST BOARD 📜")
    print("\n🆕 Available Quests:")
    print_border(40)
    for quest_name, quest in AVAILABLE_QUESTS.items():
        if quest_name not in player.active_quests and quest_name not in player.completed_quests:
            print(f"⭐ {quest_name}: {quest['description']}")
    print_border(40)
    
    print("\n📋 Active Quests:")
    print_border(40)
    if not player.active_quests:
        print("📭 No active quests.")
    else:
        for quest in player.active_quests:
            print(f"🎯 {quest['description']} (Progress: {quest['progress']}/{quest['target']['count']})")
    print_border(40)
    
    print("\n✅ Completed Quests:")
    print_border(40)
    if not player.completed_quests:
        print("📭 No completed quests.")
    else:
        for quest in player.completed_quests:
            print(f"🏆 {quest}")
    print_border(40)
    
    choice = input("\n📝 Enter quest name to accept (or 'exit' to leave): ")
    if choice in AVAILABLE_QUESTS:
        accept_quest(choice)
    elif choice != "exit":
        print("❌ Invalid quest name.")

# Introduction and class selection
def customize_character():
    """Handle character customization"""
    print_header("👤 CHARACTER CUSTOMIZATION 👤")
    
    # Gender Selection
    print("\nChoose your gender:")
    for i, gender in enumerate(Gender, 1):
        print(f"{i}. {gender.value}")
    
    while True:
        try:
            choice = int(input("\nEnter your choice (1-3): "))
            if 1 <= choice <= len(Gender):
                player.gender = list(Gender)[choice - 1]
                break
            print("❌ Invalid choice!")
        except ValueError:
            print("❌ Please enter a number!")
    
    # Background Selection
    print("\nChoose your background:")
    for i, background in enumerate(Background, 1):
        print(f"{i}. {background.value}")
    
    while True:
        try:
            choice = int(input("\nEnter your choice (1-6): "))
            if 1 <= choice <= len(Background):
                player.background = list(Background)[choice - 1]
                break
            print("❌ Invalid choice!")
        except ValueError:
            print("❌ Please enter a number!")
    
    # Appearance Customization
    print("\nCustomize your appearance:")
    
    # Hair Color
    hair_colors = ["Black", "Brown", "Blonde", "Red", "White", "Blue", "Green", "Purple"]
    print("\nChoose your hair color:")
    for i, color in enumerate(hair_colors, 1):
        print(f"{i}. {color}")
    
    while True:
        try:
            choice = int(input("\nEnter your choice (1-8): "))
            if 1 <= choice <= len(hair_colors):
                hair_color = hair_colors[choice - 1]
                break
            print("❌ Invalid choice!")
        except ValueError:
            print("❌ Please enter a number!")
    
    # Eye Color
    eye_colors = ["Brown", "Blue", "Green", "Hazel", "Gray", "Amber", "Red", "Purple"]
    print("\nChoose your eye color:")
    for i, color in enumerate(eye_colors, 1):
        print(f"{i}. {color}")
    
    while True:
        try:
            choice = int(input("\nEnter your choice (1-8): "))
            if 1 <= choice <= len(eye_colors):
                eye_color = eye_colors[choice - 1]
                break
            print("❌ Invalid choice!")
        except ValueError:
            print("❌ Please enter a number!")
    
    # Skin Tone
    skin_tones = ["Pale", "Fair", "Medium", "Olive", "Tan", "Brown", "Dark"]
    print("\nChoose your skin tone:")
    for i, tone in enumerate(skin_tones, 1):
        print(f"{i}. {tone}")
    
    while True:
        try:
            choice = int(input("\nEnter your choice (1-7): "))
            if 1 <= choice <= len(skin_tones):
                skin_tone = skin_tones[choice - 1]
                break
            print("❌ Invalid choice!")
        except ValueError:
            print("❌ Please enter a number!")
    
    # Height
    heights = ["Short", "Average", "Tall", "Very Tall"]
    print("\nChoose your height:")
    for i, height in enumerate(heights, 1):
        print(f"{i}. {height}")
    
    while True:
        try:
            choice = int(input("\nEnter your choice (1-4): "))
            if 1 <= choice <= len(heights):
                height = heights[choice - 1]
                break
            print("❌ Invalid choice!")
        except ValueError:
            print("❌ Please enter a number!")
    
    # Build
    builds = ["Slim", "Average", "Athletic", "Muscular", "Heavy"]
    print("\nChoose your build:")
    for i, build in enumerate(builds, 1):
        print(f"{i}. {build}")
    
    while True:
        try:
            choice = int(input("\nEnter your choice (1-5): "))
            if 1 <= choice <= len(builds):
                build = builds[choice - 1]
                break
            print("❌ Invalid choice!")
        except ValueError:
            print("❌ Please enter a number!")
    
    # Create appearance object
    player.appearance = Appearance(
        hair_color=hair_color,
        eye_color=eye_color,
        skin_tone=skin_tone,
        height=height,
        build=build
    )
    
    # Apply background bonuses
    if player.background == Background.NOBLE:
        player.gold += 50
        print("\n💰 As a noble, you start with 50 extra gold!")
    elif player.background == Background.SCHOLAR:
        player.stats["magic"] += 2
        print("\n✨ As a scholar, you gain +2 to magic!")
    elif player.background == Background.WARRIOR:
        player.stats["strength"] += 2
        print("\n💪 As a warrior, you gain +2 to strength!")
    elif player.background == Background.ROGUE:
        player.stats["agility"] += 2
        print("\n🏃 As a rogue, you gain +2 to agility!")
    
    # Show character summary
    print_header("👤 CHARACTER SUMMARY 👤")
    print(f"\nName: {player.name}")
    print(f"Gender: {player.gender.value}")
    print(f"Background: {player.background.value}")
    print("\nAppearance:")
    print(f"  Hair: {player.appearance.hair_color}")
    print(f"  Eyes: {player.appearance.eye_color}")
    print(f"  Skin: {player.appearance.skin_tone}")
    print(f"  Height: {player.appearance.height}")
    print(f"  Build: {player.appearance.build}")
    
    input("\nPress Enter to continue...")

def intro():
    print_animated("✨ Welcome to Eldoria: Land of Magic and Fire ✨", delay=0.05, end_pause=1.0)
    pause(1.5)
    
    # Get player name
    while True:
        player_name = input("\nWhat is your name, brave adventurer? ").strip()
        if player_name:
            player.name = player_name
            break
        print("❌ Please enter a valid name!")
    
    # Character customization
    customize_character()
    
    print_animated(f"\nWelcome, {player.name}! You are one of the few chosen to stand against the growing darkness.", delay=0.04, end_pause=1.2)
    pause(1.0)

    while True:
        print_animated("\nChoose your class:", delay=0.03, end_pause=0.5)
        print_animated("1. Mage - Master of arcane spells (High magic, Special: Mana Shield)", delay=0.03, end_pause=0.3)
        print_animated("2. Knight - Brave and strong with a sword (High defense, Special: Rally)", delay=0.03, end_pause=0.3)
        print_animated("3. Rogue - Quick and cunning in danger (High agility, Special: Backstab)", delay=0.03, end_pause=0.5)
        
        choice = input("Enter 1, 2, or 3: ")

        if choice == "1":
            player.player_class = "Mage"
            player.inventory.append("Spellbook")
            player.stats["magic"] += 3
            player.abilities.append("Mana Shield")
            break
        elif choice == "2":
            player.player_class = "Knight"
            player.inventory.append("Sword")
            player.stats["defense"] += 3
            player.abilities.append("Rally")
            break
        elif choice == "3":
            player.player_class = "Rogue"
            player.inventory.append("Dagger")
            player.stats["agility"] += 3
            player.abilities.append("Backstab")
            break
        else:
            print_animated("Invalid choice. Try again.", delay=0.03, end_pause=0.5)

    print_animated(f"\nYou are now a {player.player_class} of Eldoria!", delay=0.04, end_pause=0.8)
    print_animated(f"Starting Inventory: {player.inventory}", delay=0.03, end_pause=0.5)
    print_animated("\nYour Stats:", delay=0.03, end_pause=0.5)
    for stat, value in player.stats.items():
        print_animated(f"{stat.title()}: {value}", delay=0.03, end_pause=0.3)
    pause(1.5)

# Arcane Library path
def arcane_library():
    print("\n📚 You enter the Arcane Library, filled with floating books and ancient magic.")
    pause()

    # Random event system
    event = random.randint(1, 3)
    if event == 1:
        print("You discover a hidden magical tome!")
        player.stats["magic"] += 1
        gain_exp(10)
        if "Magical Tome" not in player.inventory:
            player.inventory.append("Magical Tome")
            print("You found a Magical Tome!")
            check_quest_completion("item", "Magical Tome")
    elif event == 2:
        print("You solve an ancient puzzle!")
        player.gold += random.randint(5, 15)
        gain_exp(8)
    else:
        print("You must fight a magical construct!")
        combat("Magical Construct", 20, 5)

    if player.player_class == "Mage":
        print("As a Mage, you absorb magical knowledge effortlessly.")
        if "Fireball Spell" not in player.inventory:
            player.inventory.append("Fireball Spell")
        gain_exp(12)
    else:
        print("You struggle to understand the glyphs, but manage to find a useful scroll.")
        if "Healing Potion" not in player.inventory:
            player.inventory.append("Healing Potion")
        gain_exp(8)

    print(f"Updated Inventory: {player.inventory}")
    pause()

# Enchanted Forest path
def enchanted_forest():
    print("\n🌳 You enter the Enchanted Forest, where ancient trees whisper secrets.")
    pause()
    
    # Random event system
    event = random.randint(1, 3)
    if event == 1:
        print("You discover a rare herb with healing properties!")
        if "Forest Herb" not in player.inventory:
            player.inventory.append("Forest Herb")
            print("You found a Forest Herb!")
        gain_exp(8)
    elif event == 2:
        print("You encounter a friendly forest spirit!")
        player.health = min(player.max_health, player.health + 15)
        print("The spirit heals you for 15 HP!")
        gain_exp(5)
    else:
        print("A Forest Creature emerges from the shadows!")
        combat("Forest Creature", 25, 7)
        check_quest_completion("enemy", "Forest Creature")

    if player.player_class == "Rogue":
        print("As a Rogue, you navigate the forest with ease.")
        if "Forest Cloak" not in player.inventory:
            player.inventory.append("Forest Cloak")
            print("You found a Forest Cloak!")
        gain_exp(10)
    else:
        print("The forest is mysterious, but you manage to find some useful items.")
        if "Healing Potion" not in player.inventory:
            player.inventory.append("Healing Potion")
        gain_exp(8)

    print(f"Updated Inventory: {player.inventory}")
    pause()

def use_ability(enemy_health: int) -> int:
    print("\nChoose your ability:")
    for i, ability in enumerate(player.abilities, 1):
        print(f"{i}. {ability}")
    
    choice = input("Enter your choice: ")
    
    if choice.isdigit() and 1 <= int(choice) <= len(player.abilities):
        ability = player.abilities[int(choice) - 1]
        
        # Apply luck to ability effectiveness
        luck_bonus = player.luck_system.get_total_luck() / 10
        
        # Check for combo potential
        combo_bonus = 1.0
        if player.last_ability_used is not None:
            # Define combo pairs
            combo_pairs = {
                ("Mana Shield", "Arcane Explosion"): 1.5,
                ("Backstab", "Poison Blade"): 1.3,
                ("Shield Wall", "Shield Bash"): 1.4,
                ("Rally", "Shield Wall"): 1.2
            }
            
            combo_key = (player.last_ability_used, ability)
            if combo_key in combo_pairs:
                combo_bonus = combo_pairs[combo_key]
                player.combo_counter += 1
                print(f"🔥 COMBO! {player.last_ability_used} + {ability} = {combo_bonus}x damage!")
            else:
                player.combo_counter = 0
        
        player.last_ability_used = ability
        
        if ability == "Mana Shield":
            print("Mana Shield activated! Damage reduced!")
            damage = int(player.stats["magic"] * (1 + luck_bonus) * combo_bonus)
            # Apply vulnerability debuff
            vulnerability = StatusEffect("Vulnerable", 2, "debuff", 2, "Reduces defense by 2")
            player.status_effects.append(vulnerability)
            vulnerability.apply(player)
            return max(0, enemy_health - damage)
        elif ability == "Rally":
            bonus = int(player.stats["defense"] * (1 + luck_bonus) * combo_bonus)
            player.health = min(player.max_health, player.health + bonus)
            print(f"Rally activated! Recovered {bonus} HP!")
            # Apply strength boost
            strength_boost = StatusEffect("Strength Boost", 2, "buff", 2, "Increases strength by 2")
            player.status_effects.append(strength_boost)
            strength_boost.apply(player)
            return enemy_health
        elif ability == "Backstab":
            damage = int(player.stats["agility"] * 2 * (1 + luck_bonus) * combo_bonus)
            print(f"Backstab deals {damage} damage!")
            # Apply poison dot
            poison = StatusEffect("Poison", 3, "dot", 3, "Deals 3 damage per turn")
            player.status_effects.append(poison)
            poison.apply(player)
            return max(0, enemy_health - damage)
        elif ability == "Shield Bash":
            damage = int((player.stats["strength"] + player.stats["defense"]) * (1 + luck_bonus) * combo_bonus)
            print(f"Shield Bash deals {damage} damage and stuns the enemy!")
            # Apply stun debuff
            stun = StatusEffect("Stunned", 1, "debuff", 0, "Cannot act for 1 turn")
            player.status_effects.append(stun)
            stun.apply(player)
            return max(0, enemy_health - damage)
        elif ability == "Poison Blade":
            base_damage = int(player.stats["agility"] * 1.5 * (1 + luck_bonus) * combo_bonus)
            poison_damage = int(base_damage * 0.5)
            print(f"Poison Blade deals {base_damage} damage and {poison_damage} poison damage!")
            # Apply poison dot
            poison = StatusEffect("Poison", 3, "dot", 3, "Deals 3 damage per turn")
            player.status_effects.append(poison)
            poison.apply(player)
            return max(0, enemy_health - (base_damage + poison_damage))
        elif ability == "Arcane Explosion":
            damage = int(player.stats["magic"] * 3 * (1 + luck_bonus) * combo_bonus)
            print(f"Arcane Explosion deals {damage} damage!")
            # Apply dazed debuff
            dazed = StatusEffect("Dazed", 2, "debuff", 2, "Reduces magic by 2")
            player.status_effects.append(dazed)
            dazed.apply(player)
            return max(0, enemy_health - damage)
        elif ability == "Shield Wall":
            bonus = int(5 * (1 + luck_bonus) * combo_bonus)
            print(f"Shield Wall activated! Defense increased by {bonus} for this turn!")
            player.stats["defense"] += bonus
            # Apply defense boost
            defense_boost = StatusEffect("Defense Boost", 2, "buff", bonus, f"Increases defense by {bonus}")
            player.status_effects.append(defense_boost)
            defense_boost.apply(player)
            return enemy_health
        elif ability == "Shadow Step":
            print("Shadow Step activated! You become invisible for one turn!")
            # Apply invisibility buff
            invisibility = StatusEffect("Invisible", 1, "buff", 0, "Cannot be targeted for 1 turn")
            player.status_effects.append(invisibility)
            invisibility.apply(player)
            return enemy_health
    else:
        print("Invalid ability choice!")
        return enemy_health

def combat(enemy_name: str, enemy_health: int, enemy_damage: int):
    print_header(f"⚔️ COMBAT WITH {enemy_name} ⚔️")
    
    original_defense = player.stats["defense"]
    
    # Create enemy object with status effects
    enemy = type('Enemy', (), {
        'name': enemy_name,
        'health': enemy_health,
        'damage': enemy_damage,
        'stats': {'strength': 5, 'magic': 5, 'agility': 5, 'defense': 5},
        'status_effects': []
    })
    
    weather_conditions = {
        "sunny": "☀️",
        "rainy": "🌧️",
        "foggy": "🌫️",
        "stormy": "⛈️"
    }
    current_weather = random.choice(list(weather_conditions.keys()))
    print(f"\n{weather_conditions[current_weather]} Current weather: {current_weather}")
    
    # Apply luck to weather effects
    weather_bonus = player.luck_system.get_total_luck() / 10
    
    if current_weather == "rainy":
        enemy.damage = max(1, int(enemy.damage * (1 - weather_bonus)))
        print("💧 The rain reduces enemy damage!")
    elif current_weather == "foggy":
        agility_bonus = int(2 * (1 + weather_bonus))
        player.stats["agility"] += agility_bonus
        print(f"🌫️ The fog increases your agility by {agility_bonus}!")
    elif current_weather == "stormy":
        enemy.health = int(enemy.health * (1 + weather_bonus))
        print("⚡ The storm strengthens the enemy!")
    
    # Apply equipment bonuses
    if player.equipment["weapon"]:
        if "Sword" in player.equipment["weapon"]:
            player.stats["strength"] += 3
        elif "Staff" in player.equipment["weapon"]:
            player.stats["magic"] += 3
        elif "Dagger" in player.equipment["weapon"]:
            player.stats["agility"] += 3
    
    if player.equipment["armor"]:
        if "Armor" in player.equipment["armor"]:
            player.stats["defense"] += 3
    
    if player.equipment["accessory"]:
        if "Amulet" in player.equipment["accessory"]:
            for stat in player.stats:
                player.stats[stat] += 2
    
    while player.health > 0 and enemy.health > 0:
        print_border(40)
        print(f"❤️ Your Health: {player.health}/{player.max_health} | 👿 {enemy_name}'s Health: {enemy.health}")
        
        # Display active status effects
        if player.status_effects:
            print("\n🔮 Your Status Effects:")
            for effect in player.status_effects:
                print(f"  • {effect.name} ({effect.duration} turns): {effect.description}")
        
        if enemy.status_effects:
            print("\n🔮 Enemy Status Effects:")
            for effect in enemy.status_effects:
                print(f"  • {effect.name} ({effect.duration} turns): {effect.description}")
        
        print_border(40)
        print("\n⚔️ Choose your action:")
        print_menu_item("1", "🗡️ Attack")
        print_menu_item("2", "✨ Use Special Ability")
        if "Healing Potion" in player.inventory:
            print_menu_item("3", "🧪 Use Healing Potion")
        print_menu_item("4", "🏃 Try to Run")
        print_border(40)

        while True:
            choice = input("Enter your choice: ")
            if choice in ["1", "2", "3", "4"]:
                break
            print("❌ Invalid choice! Please enter a number between 1 and 4.")

        if choice == "1":
            # Apply luck to critical hit chance and damage
            critical_chance = 0.2 + (player.luck_system.get_total_luck() / 50)
            critical = random.random() < critical_chance
            
            base_damage = random.randint(3, 8) + player.stats["strength"]
            damage = int(base_damage * (1 + player.luck_system.get_total_luck() / 10))
            
            if critical:
                damage *= 2
                print("💥 Critical Hit!")
            enemy.health -= damage
            print(f"⚔️ You deal {damage} damage!")
        elif choice == "2":
            enemy.health = use_ability(enemy.health)
        elif choice == "3" and "Healing Potion" in player.inventory:
            heal_amount = int(20 * (1 + player.luck_system.get_total_luck() / 10))
            player.health = min(player.max_health, player.health + heal_amount)
            player.inventory.remove("Healing Potion")
            print(f"💚 You used a Healing Potion! +{heal_amount} HP")
        elif choice == "4":
            escape_chance = (player.stats["agility"] / 20) + (player.luck_system.get_total_luck() / 20)
            if current_weather == "foggy":
                escape_chance += 0.2
            if random.random() < escape_chance:
                print("🏃 You successfully fled!")
                player.stats["defense"] = original_defense
                return True
            print("❌ Couldn't escape!")
        
        # Update and apply status effects
        for effect in player.status_effects[:]:
            if effect.update(player):
                player.status_effects.remove(effect)
        
        for effect in enemy.status_effects[:]:
            if effect.update(enemy):
                enemy.status_effects.remove(effect)
        
        if enemy.health > 0:
            # Check if enemy is stunned
            is_stunned = any(effect.name == "Stunned" for effect in enemy.status_effects)
            if is_stunned:
                print("😴 Enemy is stunned and cannot act!")
            else:
                dodge_chance = (player.stats["agility"] / 50) + (player.luck_system.get_total_luck() / 25)
                dodge = random.random() < dodge_chance
                if dodge:
                    print("💨 You dodged the attack!")
                else:
                    damage_taken = max(1, enemy.damage - (player.stats["defense"] // 2))
                    # Apply luck to damage reduction
                    damage_taken = int(damage_taken * (1 - player.luck_system.get_total_luck() / 20))
                    player.health -= damage_taken
                    print(f"💢 {enemy_name} attacks you for {damage_taken} damage!")
        
        player.stats["defense"] = original_defense

    if player.health <= 0:
        print_header(f"☠️ DEFEAT ☠️")
        print(f"You were defeated by {enemy_name}...")
        player.stats["defense"] = original_defense
        return False
    else:
        print_header(f"🏆 VICTORY 🏆")
        # Apply luck to rewards
        gold_reward = player.luck_system.apply_luck_bonus(random.randint(10, 25))
        player.gold += gold_reward
        player.total_score += gold_reward
        print(f"💰 You found {gold_reward} gold!")
        print(f"📊 Current Score: {player.total_score}")
        gain_exp(15)
        
        # Add material drops
        for material_id, material in player.crafting_system.materials.items():
            if random.random() < material.drop_chance:
                if material_id not in player.materials:
                    player.materials[material_id] = 0
                player.materials[material_id] += 1
                print(f"📦 You found {material.name}!")
        
        player.stats["defense"] = original_defense
        check_achievements()
        return True

# Dragon Battle System
def dragon_battle():
    print("\n🔥 You descend into the Cavern of the Flame Dragon.")
    pause()
    print("The ground trembles... A massive DRAGON emerges, breathing fire!")
    pause()

    if combat("Flame Dragon", 50, 12):
        player.inventory.append("Dragon Fang")
        gain_exp(25)
        print("You obtained a Dragon Fang!")
        check_quest_completion("enemy", "Flame Dragon")

# Check for game ending
def check_end(turn):
    # Enhanced end game conditions
    if (turn >= 5 or 
        player.level >= 5 or 
        player.total_score >= 500 or 
        len(player.completed_quests) >= 3):
        
        print("\n⚔️ Your journey reaches a turning point...")
        print(f"Final Level: {player.level}")
        print(f"Total Score: {player.total_score}")
        print(f"Turns Taken: {turn}")
        print(f"Final Stats:")
        for stat, value in player.stats.items():
            print(f"{stat.title()}: {value}")
        print(f"Final Inventory: {player.inventory}")
        print(f"Final Gold: {player.gold}")
        print(f"Completed Quests: {len(player.completed_quests)}")
        
        # Calculate final score
        final_score = (
            player.total_score +
            (player.level * 50) +
            (len(player.completed_quests) * 100) +
            player.gold
        )
        print(f"\nFINAL SCORE: {final_score}")
        return True
    return False

def interact_with_npc(npc_name: str):
    if npc_name not in NPCS:
        print("That NPC is not available.")
        return
    
    npc = NPCS[npc_name]
    print_header(f"💬 Talking with {npc.name} - {npc.role}")
    
    # Apply luck to friendship gain
    friendship_gain = player.luck_system.apply_luck_bonus(1)
    npc.friendship += friendship_gain
    
    print(f"\n{npc.name}: {npc.dialogue['greeting']}")
    if npc.friendship >= 3:
        print(f"{npc.name}: {npc.dialogue['friendly']}")
    
    while True:
        print("\nWhat would you like to do?")
        print("1. Chat")
        print("2. Trade")
        print("3. Leave")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == "1":
            chat_result = random.choice([
                "You share stories of your adventures.",
                "You learn about the history of Eldoria.",
                f"You discuss recent events with {npc.name}.",
                "You receive some valuable advice."
            ])
            print(f"\n{chat_result}")
            gain_exp(5)
        elif choice == "2":
            trade_with_npc(npc)
        elif choice == "3":
            print(f"\nFarewell from {npc.name}!")
            break
        else:
            print("Invalid choice!")

def trade_with_npc(npc: NPC):
    print_header(f"🤝 Trading with {npc.name}")
    print(f"Your Gold: {player.gold}")
    print(f"Friendship Level: {npc.friendship}")
    
    available_trades = {
        item: details for item, details in npc.trades.items()
        if npc.friendship >= details["requires_friendship"]
    }
    
    if not available_trades:
        print("\nNo items available at your current friendship level.")
        return
    
    print("\nAvailable Items:")
    for item, details in available_trades.items():
        print(f"{item}: {details['cost']} gold (Requires Friendship: {details['requires_friendship']})")
    
    item_choice = input("\nWhat would you like to buy? (or 'exit'): ")
    if item_choice in available_trades:
        cost = available_trades[item_choice]["cost"]
        if player.gold >= cost:
            player.gold -= cost
            player.inventory.append(item_choice)
            print(f"\nYou bought {item_choice}!")
            # Apply luck to friendship gain from trading
            friendship_gain = player.luck_system.apply_luck_bonus(2)
            npc.friendship += friendship_gain
            player.trades_completed += 1
            check_achievements()
        else:
            print("Not enough gold!")
    elif item_choice != "exit":
        print("Invalid item!")

def training_grounds():
    print("\n⚔️ Welcome to the Training Grounds!")
    
    if player.player_class == "Knight":
        print("Sir Galahad offers to teach you advanced combat techniques!")
        gain_exp(15)
        if "Shield Bash" not in player.abilities:
            player.abilities.append("Shield Bash")
            print("You learned Shield Bash!")
    elif player.player_class == "Rogue":
        print("You practice your agility on the training dummies.")
        player.stats["agility"] += 1
        gain_exp(10)
    else:
        print("You spend some time practicing basic combat moves.")
        gain_exp(8)
    
    # Apply luck to training results
    bonus_exp = player.luck_system.apply_luck_bonus(5)
    gain_exp(bonus_exp)

def thieves_den():
    print("\n🗡️ You enter the secret Thieves' Den...")
    
    if player.player_class == "Rogue":
        print("Shadow offers to teach you advanced stealth techniques!")
        gain_exp(15)
        if "Poison Blade" not in player.abilities:
            player.abilities.append("Poison Blade")
            print("You learned Poison Blade!")
    elif player.player_class == "Mage":
        print("You find some interesting scrolls in the shadows.")
        gain_exp(10)
    else:
        print("You feel out of place here...")
        gain_exp(5)
    
    # Apply luck to finding loot
    if random.random() < (player.luck_system.get_total_luck() / 20):
        print("You found a hidden treasure!")
        player.gold += random.randint(10, 30)

def serialize_game_state() -> dict:
    """Convert current game state to a dictionary for saving"""
    return {
        "player": {
            "name": player.name,
            "gender": player.gender.value if player.gender else None,
            "background": player.background.value if player.background else None,
            "appearance": {
                "hair_color": player.appearance.hair_color if player.appearance else None,
                "eye_color": player.appearance.eye_color if player.appearance else None,
                "skin_tone": player.appearance.skin_tone if player.appearance else None,
                "height": player.appearance.height if player.appearance else None,
                "build": player.appearance.build if player.appearance else None
            } if player.appearance else None,
            "level": player.level,
            "exp": player.exp,
            "max_health": player.max_health,
            "health": player.health,
            "gold": player.gold,
            "inventory": player.inventory,
            "player_class": player.player_class,
            "total_score": player.total_score,
            "turns_taken": player.turns_taken,
            "stats": player.stats,
            "abilities": player.abilities,
            "active_quests": player.active_quests,
            "completed_quests": player.completed_quests,
            "skill_points": player.skill_points,
            "skill_tree": player.skill_tree,
            "equipment": player.equipment,
            "combo_counter": player.combo_counter,
            "last_ability_used": player.last_ability_used,
            "status_effects": [
                {
                    "name": effect.name,
                    "duration": effect.duration,
                    "effect_type": effect.effect_type,
                    "value": effect.value,
                    "description": effect.description
                }
                for effect in player.status_effects
            ],
            "visited_locations": list(player.visited_locations),
            "trades_completed": player.trades_completed,
            "consecutive_lucky_days": player.consecutive_lucky_days,
            "unlocked_achievements": list(player.achievement_system.unlocked_achievements),
            "materials": player.materials,
            "known_events": list(player.lore_system.known_events),
            "faction_relations": {faction.value: relation for faction, relation in player.lore_system.faction_relations.items()},
            "known_locations": list(player.known_locations),
            "known_npcs": list(player.known_npcs),
            "quest_history": player.quest_history
        },
        "luck_system": {
            "base_luck": player.luck_system.base_luck,
            "daily_luck": player.luck_system.daily_luck,
            "last_update": player.luck_system.last_update
        }
    }

def deserialize_game_state(game_state: dict) -> None:
    """Load game state from dictionary"""
    global player
    
    # Create new player instance
    player = Player()
    
    # Restore player attributes
    player_data = game_state["player"]
    player.name = player_data["name"]
    
    # Restore gender
    if player_data["gender"]:
        player.gender = Gender(player_data["gender"])
    
    # Restore background
    if player_data["background"]:
        player.background = Background(player_data["background"])
    
    # Restore appearance
    if player_data["appearance"]:
        player.appearance = Appearance(
            hair_color=player_data["appearance"]["hair_color"],
            eye_color=player_data["appearance"]["eye_color"],
            skin_tone=player_data["appearance"]["skin_tone"],
            height=player_data["appearance"]["height"],
            build=player_data["appearance"]["build"]
        )
    
    # Restore other player attributes
    for key, value in player_data.items():
        if key == "status_effects":
            player.status_effects = [
                StatusEffect(
                    effect["name"],
                    effect["duration"],
                    effect["effect_type"],
                    effect["value"],
                    effect["description"]
                )
                for effect in value
            ]
        else:
            setattr(player, key, value)
    
    # Restore luck system
    luck_data = game_state["luck_system"]
    player.luck_system.base_luck = luck_data["base_luck"]
    player.luck_system.daily_luck = luck_data["daily_luck"]
    player.luck_system.last_update = luck_data["last_update"]
    
    # Restore achievement system
    player.achievement_system = AchievementSystem()
    player.achievement_system.unlocked_achievements = set(player_data["unlocked_achievements"])
    
    # Restore additional player attributes
    player.visited_locations = set(player_data["visited_locations"])
    player.trades_completed = player_data["trades_completed"]
    player.consecutive_lucky_days = player_data["consecutive_lucky_days"]
    player.materials = dict(player_data["materials"])
    
    # Restore lore system
    player.lore_system.known_events = set(player_data["known_events"])
    player.lore_system.faction_relations = {
        Faction(faction): relation for faction, relation in player_data["faction_relations"].items()
    }
    player.known_locations = set(player_data["known_locations"])
    player.known_npcs = set(player_data["known_npcs"])
    player.quest_history = player_data["quest_history"]

def save_game_menu():
    """Display save game menu"""
    print_header("💾 SAVE GAME 💾")
    save_manager = SaveManager()
    
    # List existing saves
    saves = save_manager.list_saves()
    if saves:
        print("\n📂 Existing Saves:")
        for i, save in enumerate(saves, 1):
            print(f"{i}. {save}")
        print(f"{len(saves) + 1}. New Save")
    else:
        print("\n📂 No existing saves found")
        print("1. New Save")
    
    while True:
        try:
            choice = int(input("\nEnter your choice: "))
            if 1 <= choice <= (len(saves) + 1):
                break
            print("❌ Invalid choice!")
        except ValueError:
            print("❌ Please enter a number!")
    
    if choice <= len(saves):
        save_name = saves[choice - 1]
        if input(f"Overwrite save '{save_name}'? (yes/no): ").lower() != "yes":
            return
    else:
        while True:
            save_name = input("Enter save name: ").strip()
            if save_name:
                break
            print("❌ Save name cannot be empty!")
    
    password = input("Enter password for save file: ")
    if not password:
        print("❌ Password cannot be empty!")
        return
    
    game_state = serialize_game_state()
    if save_manager.save_game(game_state, save_name, password):
        print(f"✅ Game saved successfully as '{save_name}'!")
    else:
        print("❌ Failed to save game!")

def load_game_menu():
    """Display load game menu"""
    print_header("📂 LOAD GAME 📂")
    save_manager = SaveManager()
    
    saves = save_manager.list_saves()
    if not saves:
        print("\n❌ No save files found!")
        return False
    
    print("\n📂 Available Saves:")
    for i, save in enumerate(saves, 1):
        print(f"{i}. {save}")
    print("0. Cancel")
    
    while True:
        try:
            choice = int(input("\nEnter save number to load (or 0 to cancel): "))
            if 0 <= choice <= len(saves):
                break
            print("❌ Invalid choice!")
        except ValueError:
            print("❌ Please enter a number!")
    
    if choice == 0:
        return False
    
    save_name = saves[choice - 1]
    password = input("Enter password: ")
    
    game_state = save_manager.load_game(save_name, password)
    if game_state:
        deserialize_game_state(game_state)
        print(f"✅ Game loaded successfully from '{save_name}'!")
        print(f"Welcome back, {player.name}!")
        return True
    else:
        print("❌ Failed to load game!")
        return False

def show_achievements_menu():
    """Display achievements menu"""
    print_header("🏆 ACHIEVEMENTS 🏆")
    achievement_system = player.achievement_system
    
    # Show completion stats
    unlocked = achievement_system.get_unlocked_count()
    total = achievement_system.get_total_count()
    percentage = achievement_system.get_completion_percentage()
    print(f"\n📊 Progress: {unlocked}/{total} ({percentage:.1f}%)")
    print_border(40)
    
    # Show achievements by category
    categories = [
        AchievementCategory.COMBAT,
        AchievementCategory.EXPLORATION,
        AchievementCategory.SOCIAL,
        AchievementCategory.COLLECTION,
        AchievementCategory.PROGRESSION,
        AchievementCategory.SPECIAL
    ]
    
    for category in categories:
        print(f"\n{category.value} Achievements:")
        achievements = achievement_system.get_category_achievements(category)
        for achievement_id, status in achievements.items():
            if status["hidden"]:
                print("  🔒 Hidden Achievement")
            else:
                unlocked_symbol = "✅" if status["unlocked"] else "❌"
                print(f"  {unlocked_symbol} {status['name']}: {status['description']}")
        print_border(40)
    
    input("\nPress Enter to return to the main menu...")

def check_achievements():
    """Check for new achievements and display notifications"""
    newly_unlocked = player.achievement_system.check_achievements(player)
    if newly_unlocked:
        print_header("🎉 ACHIEVEMENT UNLOCKED! 🎉")
        for achievement_id in newly_unlocked:
            achievement = player.achievement_system.achievements[achievement_id]
            print(f"\n🏆 {achievement.name}")
            print(f"📝 {achievement.description}")
            if "gold" in achievement.reward:
                print(f"💰 +{achievement.reward['gold']} gold")
            if "exp" in achievement.reward:
                print(f"✨ +{achievement.reward['exp']} exp")
        print_border(40)
        input("\nPress Enter to continue...")

def show_crafting_menu():
    """Display crafting menu"""
    print_header("🔨 CRAFTING MENU 🔨")
    
    # Show materials
    print("\n📦 Your Materials:")
    print_border(40)
    if not player.materials:
        print("No materials in inventory")
    else:
        for material_id, quantity in player.materials.items():
            material = player.crafting_system.get_material_by_id(material_id)
            if material:
                print(f"{material.name} ({material.rarity.value}): {quantity}")
    print_border(40)
    
    # Show available recipes
    print("\n📜 Available Recipes:")
    print_border(40)
    available_recipes = player.crafting_system.get_available_recipes(player.level, player.materials)
    if not available_recipes:
        print("No recipes available")
    else:
        for i, recipe in enumerate(available_recipes, 1):
            print(f"{i}. {recipe.name} ({recipe.rarity.value})")
            print(f"   {recipe.description}")
            print("   Required Materials:")
            for material_id, quantity in recipe.materials.items():
                material = player.crafting_system.get_material_by_id(material_id)
                if material:
                    print(f"   - {material.name}: {quantity}")
            print_border(40)
    
    while True:
        try:
            choice = int(input("\nEnter recipe number to craft (or 0 to exit): "))
            if choice == 0:
                break
            if 1 <= choice <= len(available_recipes):
                recipe = available_recipes[choice - 1]
                result = player.crafting_system.craft_item(recipe.id, player.materials)
                if result:
                    print(f"\n✨ You crafted {recipe.name}!")
                    player.inventory.append(result)
                    check_achievements()
                else:
                    print("❌ Failed to craft item!")
            else:
                print("❌ Invalid choice!")
        except ValueError:
            print("❌ Please enter a number!")

def show_lore_menu():
    """Display the lore menu"""
    print_header("📚 ELDORIA LORE 📚")
    
    while True:
        print("\n1. World History")
        print("2. Factions")
        print("3. Known Events")
        print("4. Faction Relations")
        print("5. Random Lore")
        print("0. Back to Main Menu")
        
        choice = input("\nEnter your choice: ")
        
        if choice == "1":
            show_world_history()
        elif choice == "2":
            show_factions()
        elif choice == "3":
            show_known_events()
        elif choice == "4":
            show_faction_relations()
        elif choice == "5":
            show_random_lore()
        elif choice == "0":
            break
        else:
            print("❌ Invalid choice!")

def show_world_history():
    """Display the history of Eldoria"""
    print_header("📜 WORLD HISTORY 📜")
    
    for era in Era:
        print(f"\n{era.value}:")
        events = [event for event in player.lore_system.world_events if event.era == era]
        for event in events:
            known = event.name in player.lore_system.known_events
            print(f"  {'✅' if known else '❓'} {event.name}")
            if known:
                print(f"     {event.description}")
                print(f"     Impact: {event.impact}")
    
    input("\nPress Enter to continue...")

def show_factions():
    """Display information about factions"""
    print_header("🏰 FACTIONS 🏰")
    
    for faction, info in player.lore_system.faction_info.items():
        print(f"\n{info.name}:")
        print(f"  {info.description}")
        print("\n  Goals:")
        for goal in info.goals:
            print(f"    • {goal}")
        print("\n  Headquarters: " + info.headquarters)
        print("  Leader: " + info.leader)
        print("\n  Allies:", ", ".join(ally.value for ally in info.allies))
        print("  Enemies:", ", ".join(enemy.value for enemy in info.enemies))
        print(f"  Your Status: {player.lore_system.get_faction_status(faction)}")
    
    input("\nPress Enter to continue...")

def show_known_events():
    """Display events the player has learned about"""
    print_header("📅 KNOWN EVENTS 📅")
    
    if not player.lore_system.known_events:
        print("\nYou haven't learned about any major events yet.")
    else:
        for event in player.lore_system.world_events:
            if event.name in player.lore_system.known_events:
                print(f"\n{event.name} ({event.era.value}):")
                print(f"  {event.description}")
                print(f"  Impact: {event.impact}")
                print("  Related Factions:", ", ".join(faction.value for faction in event.related_factions))
    
    input("\nPress Enter to continue...")

def show_faction_relations():
    """Display the player's relations with factions"""
    print_header("🤝 FACTION RELATIONS 🤝")
    
    for faction in Faction:
        status = player.lore_system.get_faction_status(faction)
        print(f"\n{faction.value}: {status}")
    
    input("\nPress Enter to continue...")

def show_random_lore():
    """Display a random piece of lore"""
    print_header("🔍 RANDOM LORE 🔍")
    
    tidbit = player.lore_system.get_random_lore_tidbit()
    print(f"\n{tidbit}")
    
    input("\nPress Enter to continue...")

# Main game loop
def main():
    # Add save/load option to main menu
    print_header("✨ WELCOME TO ELDORIA: LAND OF MAGIC AND FIRE ✨")
    print("\n1. New Game")
    print("2. Load Game")
    print("3. Exit")
    
    while True:
        try:
            choice = int(input("\nEnter your choice (1-3): "))
            if 1 <= choice <= 3:
                break
            print("❌ Invalid choice!")
        except ValueError:
            print("❌ Please enter a number!")
    
    if choice == 2:
        if not load_game_menu():
            return
    elif choice == 3:
        return
    
    # Original intro and game loop
    intro()
    turn = 0
    
    while True:
        # Update and display daily luck
        player.luck_system.update_daily_luck()
        luck_status = "🍀 Lucky day!" if player.luck_system.daily_luck > 0 else "👎 Unlucky day..." if player.luck_system.daily_luck < 0 else "😐 Normal luck today."
        
        print_header("🗺️ CHOOSE YOUR DESTINATION 🗺️")
        print(f"\n{luck_status}")
        print(f"Luck Rating: {player.luck_system.get_total_luck()}")
        print_border(40)
        
        print_menu_item("1", "📚 Arcane Library")
        print_menu_item("2", "🐉 Cavern of the Flame Dragon")
        print_menu_item("3", "🌳 Enchanted Forest")
        print_menu_item("4", "🏪 Mystic Shop")
        print_menu_item("5", "📜 Quest Board")
        print_menu_item("6", "⚔️ Training Grounds")
        print_menu_item("7", "🗡️ Thieves' Den")
        print_menu_item("8", "💬 Talk to NPCs")
        print_menu_item("9", "📊 View Character Status")
        print_menu_item("10", "🚪 Exit Game")
        print_menu_item("11", "💾 Save Game")
        print_menu_item("12", "🏆 View Achievements")
        print_menu_item("13", "🔨 Crafting")  # Add crafting option
        print_menu_item("14", "📚 Lore")  # Add lore option
        print_border(40)
        
        while True:
            try:
                location = input("Enter 1-14: ")  # Update range
                if location in [str(i) for i in range(1, 15)]:  # Update range
                    break
                print("❌ Invalid choice! Please enter a number between 1 and 14.")
            except ValueError:
                print("❌ Invalid input! Please enter a number.")

        if location == "10":
            print_header("🎮 GAME OVER 🎮")
            print(f"🏆 Final Score: {player.total_score}")
            break
            
        if location == "1":
            arcane_library()
            if random.random() < 0.7:  # 70% chance to meet Master Eldric
                print("\nMaster Eldric is present in the library...")
                if input("Would you like to talk to him? (yes/no): ").lower() == "yes":
                    interact_with_npc("Master Eldric")
        elif location == "2":
            dragon_battle()
        elif location == "3":
            enchanted_forest()
            if random.random() < 0.5:  # 50% chance to meet Shadow
                print("\nYou notice a mysterious figure in the shadows...")
                if input("Would you like to approach? (yes/no): ").lower() == "yes":
                    interact_with_npc("Shadow")
        elif location == "4":
            shop()
        elif location == "5":
            quest_board()
        elif location == "6":
            training_grounds()
            if random.random() < 0.7:  # 70% chance to meet Sir Galahad
                print("\nSir Galahad is overseeing the training...")
                if input("Would you like to talk to him? (yes/no): ").lower() == "yes":
                    interact_with_npc("Sir Galahad")
        elif location == "7":
            thieves_den()
        elif location == "8":
            print("\nAvailable NPCs:")
            for npc_name, npc in NPCS.items():
                print(f"- {npc_name} ({npc.role}) at {npc.location}")
            npc_choice = input("\nWho would you like to talk to? (or 'exit'): ")
            if npc_choice in NPCS:
                interact_with_npc(npc_choice)
        elif location == "9":
            print_header("📊 CHARACTER STATUS 📊")
            print(f"🎭 Class: {player.player_class}")
            print(f"📈 Level: {player.level}")
            print(f"✨ EXP: {player.exp}/{player.level * 20}")
            print(f"❤️ Health: {player.health}/{player.max_health}")
            print(f"💰 Gold: {player.gold}")
            print(f"🏆 Current Score: {player.total_score}")
            print(f"🍀 Luck Rating: {player.luck_system.get_total_luck()}")
            print(f"🎯 Skill Points: {player.skill_points}")
            print_border(30)
            
            print("\n💪 Stats:")
            for stat, value in player.stats.items():
                print(f"⚡ {stat.title()}: {value}")
            print_border(30)
            
            print("\n🎒 Equipment:")
            print(f"🗡️ Weapon: {player.equipment['weapon'] or 'None'}")
            print(f"🛡️ Armor: {player.equipment['armor'] or 'None'}")
            print(f"💍 Accessory: {player.equipment['accessory'] or 'None'}")
            print_border(30)
            
            print("\n🔮 Skills:")
            if player.skill_tree["passive"]:
                print("Passive Skills:")
                for skill in player.skill_tree["passive"]:
                    print(f"  • {skill}")
            else:
                print("No passive skills learned yet.")
                
            if player.skill_tree["active"]:
                print("\nActive Skills:")
                for skill in player.skill_tree["active"]:
                    print(f"  • {skill}")
            else:
                print("No active skills learned yet.")
            print_border(30)
            
            print("\n✨ Special Abilities:")
            if player.abilities:
                for ability in player.abilities:
                    print(f"  • {ability}")
            else:
                print("No special abilities yet.")
            print_border(30)
            
            print("\n🔮 Status Effects:")
            if player.status_effects:
                for effect in player.status_effects:
                    print(f"  • {effect.name} ({effect.duration} turns): {effect.description}")
            else:
                print("No active status effects.")
            print_border(30)
            
            print(f"\n🎒 Inventory: {', '.join(player.inventory)}")
            print(f"📋 Active Quests: {len(player.active_quests)}")
            print(f"🏆 Completed Quests: {len(player.completed_quests)}")
            print_border(30)
            time.sleep(2)

        if location in ["1", "2", "3", "6", "7"]:
            turn += 1
            player.turns_taken += 1
            if check_end(turn):
                break
            
        cont = input("\n🎮 Continue your adventure? (yes/no): ").lower()
        while cont not in ["yes", "no"]:
            print("❌ Invalid input! Please enter 'yes' or 'no'.")
            cont = input("🎮 Continue your adventure? (yes/no): ").lower()
            
        if cont != "yes":
            print_header("👋 FAREWELL, BRAVE ADVENTURER! 👋")
            print(f"🏆 Final Score: {player.total_score}")
            break

        if location == "11":
            save_game_menu()
            continue

        if location == "12":
            show_achievements_menu()
            continue

        if location == "13":
            show_crafting_menu()
            continue

        if location == "14":
            show_lore_menu()
            continue

if __name__ == "__main__":
    main()
    
