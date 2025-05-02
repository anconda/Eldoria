from typing import Dict, List
from dataclasses import dataclass

@dataclass
class NPC:
    name: str
    role: str
    location: str
    dialogue: Dict[str, str]
    trades: Dict[str, Dict] = None
    friendship: int = 0
    status_effects: List = None

    def __post_init__(self):
        if self.trades is None:
            self.trades = {}
        if self.status_effects is None:
            self.status_effects = []

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
    # ... other NPCs ...
} 