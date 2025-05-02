from typing import Dict, List, Set
from dataclasses import dataclass
from enum import Enum
from npcs import NPCS

class AchievementCategory(Enum):
    COMBAT = "Combat"
    EXPLORATION = "Exploration"
    SOCIAL = "Social"
    COLLECTION = "Collection"
    PROGRESSION = "Progression"
    SPECIAL = "Special"

@dataclass
class Achievement:
    id: str
    name: str
    description: str
    category: AchievementCategory
    condition: callable
    reward: Dict[str, int]  # e.g., {"gold": 100, "exp": 50}
    hidden: bool = False

class AchievementSystem:
    def __init__(self):
        self.achievements: Dict[str, Achievement] = {}
        self.unlocked_achievements: Set[str] = set()
        self._initialize_achievements()
    
    def _initialize_achievements(self):
        """Initialize all game achievements"""
        self.achievements = {
            # Combat Achievements
            "first_blood": Achievement(
                id="first_blood",
                name="First Blood",
                description="Defeat your first enemy",
                category=AchievementCategory.COMBAT,
                condition=lambda player: player.turns_taken > 0,
                reward={"gold": 50, "exp": 25}
            ),
            "dragon_slayer": Achievement(
                id="dragon_slayer",
                name="Dragon Slayer",
                description="Defeat the Flame Dragon",
                category=AchievementCategory.COMBAT,
                condition=lambda player: "Dragon Fang" in player.inventory,
                reward={"gold": 200, "exp": 100}
            ),
            "combo_master": Achievement(
                id="combo_master",
                name="Combo Master",
                description="Execute a 3-hit combo",
                category=AchievementCategory.COMBAT,
                condition=lambda player: player.combo_counter >= 3,
                reward={"gold": 100, "exp": 50}
            ),
            
            # Exploration Achievements
            "world_traveler": Achievement(
                id="world_traveler",
                name="World Traveler",
                description="Visit all locations in Eldoria",
                category=AchievementCategory.EXPLORATION,
                condition=lambda player: len(set(loc for loc in player.visited_locations)) >= 6,
                reward={"gold": 150, "exp": 75}
            ),
            "library_scholar": Achievement(
                id="library_scholar",
                name="Library Scholar",
                description="Find all magical tomes in the Arcane Library",
                category=AchievementCategory.EXPLORATION,
                condition=lambda player: sum(1 for item in player.inventory if "Magical Tome" in item) >= 2,
                reward={"gold": 100, "exp": 50}
            ),
            
            # Social Achievements
            "friend_of_all": Achievement(
                id="friend_of_all",
                name="Friend of All",
                description="Reach maximum friendship with all NPCs",
                category=AchievementCategory.SOCIAL,
                condition=lambda player: all(npc.friendship >= 5 for npc in NPCS.values()),
                reward={"gold": 200, "exp": 100}
            ),
            "master_trader": Achievement(
                id="master_trader",
                name="Master Trader",
                description="Complete 10 successful trades",
                category=AchievementCategory.SOCIAL,
                condition=lambda player: player.trades_completed >= 10,
                reward={"gold": 150, "exp": 75}
            ),
            
            # Collection Achievements
            "treasure_hunter": Achievement(
                id="treasure_hunter",
                name="Treasure Hunter",
                description="Collect 10 unique items",
                category=AchievementCategory.COLLECTION,
                condition=lambda player: len(set(player.inventory)) >= 10,
                reward={"gold": 100, "exp": 50}
            ),
            "equipment_master": Achievement(
                id="equipment_master",
                name="Equipment Master",
                description="Equip a full set of legendary items",
                category=AchievementCategory.COLLECTION,
                condition=lambda player: all(slot is not None for slot in player.equipment.values()),
                reward={"gold": 200, "exp": 100}
            ),
            
            # Progression Achievements
            "rising_star": Achievement(
                id="rising_star",
                name="Rising Star",
                description="Reach level 5",
                category=AchievementCategory.PROGRESSION,
                condition=lambda player: player.level >= 5,
                reward={"gold": 150, "exp": 75}
            ),
            "quest_master": Achievement(
                id="quest_master",
                name="Quest Master",
                description="Complete 5 quests",
                category=AchievementCategory.PROGRESSION,
                condition=lambda player: len(player.completed_quests) >= 5,
                reward={"gold": 200, "exp": 100}
            ),
            
            # Special Achievements
            "lucky_charm": Achievement(
                id="lucky_charm",
                name="Lucky Charm",
                description="Have maximum luck for 3 consecutive days",
                category=AchievementCategory.SPECIAL,
                condition=lambda player: player.consecutive_lucky_days >= 3,
                reward={"gold": 100, "exp": 50}
            ),
            "skill_master": Achievement(
                id="skill_master",
                name="Skill Master",
                description="Unlock all skills in your class skill tree",
                category=AchievementCategory.SPECIAL,
                condition=lambda player: len(player.skill_tree["passive"]) + len(player.skill_tree["active"]) >= 6,
                reward={"gold": 200, "exp": 100}
            )
        }
    
    def check_achievements(self, player) -> List[str]:
        """Check and unlock any new achievements"""
        newly_unlocked = []
        for achievement_id, achievement in self.achievements.items():
            if achievement_id not in self.unlocked_achievements:
                if achievement.condition(player):
                    self.unlocked_achievements.add(achievement_id)
                    newly_unlocked.append(achievement_id)
                    # Apply rewards
                    if "gold" in achievement.reward:
                        player.gold += achievement.reward["gold"]
                    if "exp" in achievement.reward:
                        player.exp += achievement.reward["exp"]
        return newly_unlocked
    
    def get_achievement_status(self) -> Dict[str, Dict]:
        """Get status of all achievements"""
        return {
            achievement_id: {
                "name": achievement.name,
                "description": achievement.description,
                "category": achievement.category.value,
                "unlocked": achievement_id in self.unlocked_achievements,
                "hidden": achievement.hidden and achievement_id not in self.unlocked_achievements
            }
            for achievement_id, achievement in self.achievements.items()
        }
    
    def get_category_achievements(self, category: AchievementCategory) -> Dict[str, Dict]:
        """Get achievements filtered by category"""
        return {
            achievement_id: status
            for achievement_id, status in self.get_achievement_status().items()
            if self.achievements[achievement_id].category == category
        }
    
    def get_unlocked_count(self) -> int:
        """Get total number of unlocked achievements"""
        return len(self.unlocked_achievements)
    
    def get_total_count(self) -> int:
        """Get total number of achievements"""
        return len(self.achievements)
    
    def get_completion_percentage(self) -> float:
        """Get percentage of achievements unlocked"""
        return (len(self.unlocked_achievements) / len(self.achievements)) * 100 