from dataclasses import dataclass

@dataclass
class Achievement:
    id: str
    name: str
    description: str
    category: str
    requirement: int
    tier: str

@dataclass
class UserAchievement:
    achievement_id: str
    unlocked_at: str
