from typing import Dict, List, Set
from enum import Enum
from dataclasses import dataclass
import random

class Faction(Enum):
    COUNCIL_OF_MAGES = "Council of Mages"
    KNIGHTS_OF_ELDORIA = "Knights of Eldoria"
    SHADOW_THIEVES = "Shadow Thieves"
    DRUID_CIRCLE = "Druid Circle"
    MERCHANT_GUILD = "Merchant Guild"
    CULT_OF_THE_DRAGON = "Cult of the Dragon"

class Era(Enum):
    AGE_OF_CREATION = "Age of Creation"
    AGE_OF_DRAGONS = "Age of Dragons"
    AGE_OF_MAGIC = "Age of Magic"
    AGE_OF_DARKNESS = "Age of Darkness"
    CURRENT_AGE = "Current Age"

@dataclass
class WorldEvent:
    name: str
    description: str
    era: Era
    impact: str
    related_factions: List[Faction]

@dataclass
class FactionInfo:
    name: str
    description: str
    goals: List[str]
    allies: List[Faction]
    enemies: List[Faction]
    headquarters: str
    leader: str

class LoreSystem:
    def __init__(self):
        self.known_events: Set[str] = set()
        self.faction_relations: Dict[Faction, int] = {faction: 0 for faction in Faction}
        self.current_era = Era.CURRENT_AGE
        
        # Major world events
        self.world_events = [
            WorldEvent(
                "The Sundering",
                "A cataclysmic event where the world was split into three realms: The Material Plane, The Feywild, and The Shadowfell.",
                Era.AGE_OF_CREATION,
                "Created the current geography of Eldoria and established the ley lines of magic.",
                [Faction.COUNCIL_OF_MAGES, Faction.DRUID_CIRCLE]
            ),
            WorldEvent(
                "The Dragon War",
                "A great conflict between the ancient dragons and the first mortal civilizations.",
                Era.AGE_OF_DRAGONS,
                "Led to the near-extinction of dragons and the rise of mortal kingdoms.",
                [Faction.KNIGHTS_OF_ELDORIA, Faction.CULT_OF_THE_DRAGON]
            ),
            WorldEvent(
                "The Arcane Revolution",
                "The discovery of systematic magic and the founding of the first magical academies.",
                Era.AGE_OF_MAGIC,
                "Established modern magical practices and the Council of Mages.",
                [Faction.COUNCIL_OF_MAGES]
            ),
            WorldEvent(
                "The Shadow Pact",
                "A secret alliance between the Shadow Thieves and the Cult of the Dragon.",
                Era.AGE_OF_DARKNESS,
                "Led to increased criminal activity and dragon cult resurgence.",
                [Faction.SHADOW_THIEVES, Faction.CULT_OF_THE_DRAGON]
            ),
            WorldEvent(
                "The Great Awakening",
                "The rediscovery of ancient magical artifacts and the resurgence of dragon sightings.",
                Era.CURRENT_AGE,
                "Current events that shape the world's present state.",
                [Faction.COUNCIL_OF_MAGES, Faction.KNIGHTS_OF_ELDORIA, Faction.CULT_OF_THE_DRAGON]
            )
        ]
        
        # Faction information
        self.faction_info = {
            Faction.COUNCIL_OF_MAGES: FactionInfo(
                "Council of Mages",
                "The governing body of magical practice and research in Eldoria.",
                ["Preserve magical knowledge", "Regulate magical use", "Protect against magical threats"],
                [Faction.KNIGHTS_OF_ELDORIA, Faction.DRUID_CIRCLE],
                [Faction.CULT_OF_THE_DRAGON],
                "The Arcane Spire",
                "Archmage Eldric the Wise"
            ),
            Faction.KNIGHTS_OF_ELDORIA: FactionInfo(
                "Knights of Eldoria",
                "The noble order of warriors dedicated to protecting the realm.",
                ["Maintain peace and order", "Defend against external threats", "Uphold justice"],
                [Faction.COUNCIL_OF_MAGES, Faction.MERCHANT_GUILD],
                [Faction.SHADOW_THIEVES, Faction.CULT_OF_THE_DRAGON],
                "The Grand Citadel",
                "Sir Galahad the Valiant"
            ),
            Faction.SHADOW_THIEVES: FactionInfo(
                "Shadow Thieves",
                "A secretive organization of rogues and information brokers.",
                ["Gather intelligence", "Control the underworld", "Maintain balance through shadows"],
                [Faction.MERCHANT_GUILD],
                [Faction.KNIGHTS_OF_ELDORIA],
                "The Hidden Den",
                "Shadow, the Unseen"
            ),
            Faction.DRUID_CIRCLE: FactionInfo(
                "Druid Circle",
                "Guardians of nature and the balance between civilization and wilderness.",
                ["Protect nature", "Maintain balance", "Preserve ancient knowledge"],
                [Faction.COUNCIL_OF_MAGES],
                [Faction.CULT_OF_THE_DRAGON],
                "The Sacred Grove",
                "Druidess Sylva"
            ),
            Faction.MERCHANT_GUILD: FactionInfo(
                "Merchant Guild",
                "The economic backbone of Eldoria, controlling trade and commerce.",
                ["Expand trade routes", "Protect merchant interests", "Maintain economic stability"],
                [Faction.KNIGHTS_OF_ELDORIA],
                [Faction.SHADOW_THIEVES],
                "The Grand Market",
                "Guildmaster Goldhand"
            ),
            Faction.CULT_OF_THE_DRAGON: FactionInfo(
                "Cult of the Dragon",
                "A secretive group seeking to restore dragonkind to its former glory.",
                ["Awaken ancient dragons", "Gather dragon artifacts", "Spread dragon worship"],
                [],
                [Faction.COUNCIL_OF_MAGES, Faction.KNIGHTS_OF_ELDORIA, Faction.DRUID_CIRCLE],
                "The Dragon's Lair",
                "Dragon Priest Malakar"
            )
        }
    
    def learn_event(self, event_name: str) -> None:
        self.known_events.add(event_name)
    
    def update_faction_relation(self, faction: Faction, change: int) -> None:
        self.faction_relations[faction] = max(-100, min(100, self.faction_relations[faction] + change))
    
    def get_faction_status(self, faction: Faction) -> str:
        relation = self.faction_relations[faction]
        if relation >= 75: return "Allied"
        elif relation >= 25: return "Friendly"
        elif relation >= -25: return "Neutral"
        elif relation >= -75: return "Unfriendly"
        else: return "Hostile"
    
    def get_random_lore_tidbit(self) -> str:
        tidbits = [
            "The Arcane Spire was built on the site of the first magical ley line convergence.",
            "The Shadow Thieves were originally founded to protect the poor from corrupt nobles.",
            "The Druid Circle maintains the last known dragon egg in their Sacred Grove.",
            "The Merchant Guild's secret vaults contain artifacts from every era of Eldoria.",
            "The Knights of Eldoria's armor is forged from the scales of the last great dragon.",
            "The Cult of the Dragon believes the current age is the 'Age of Rebirth' for dragonkind."
        ]
        return random.choice(tidbits) 