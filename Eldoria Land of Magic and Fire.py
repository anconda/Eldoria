import time
import random
from typing import List, Dict, Optional

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

class Player:
    def __init__(self):
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
        "consumable": []
    }
    
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
def intro():
    print_animated("✨ Welcome to Eldoria: Land of Magic and Fire ✨", delay=0.05, end_pause=1.0)
    pause(1.5)
    print_animated("You are one of the few chosen to stand against the growing darkness.", delay=0.04, end_pause=1.2)
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
        player.stats["defense"] = original_defense
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

# Main game loop
def main():
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
        print_border(40)
        
        while True:
            try:
                location = input("Enter 1-10: ")
                if location in [str(i) for i in range(1, 11)]:
                    break
                print("❌ Invalid choice! Please enter a number between 1 and 10.")
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

if __name__ == "__main__":
    main()
    
