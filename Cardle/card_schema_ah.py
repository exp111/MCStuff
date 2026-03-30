from typing import Any, Literal, TypedDict, List, Optional, Union


class DeckOption(TypedDict, total=False):
    limit: int
    name_limit: int
    trait: List[str]
    type: List[str]
    use_deck_limit: bool


class DeckRequirement(TypedDict, total=False):
    aspects: int
    limit: int


class Card(TypedDict, total=False):
    # Required fields
    code: str  # Pattern: ^[0-9]{5}[a-z]{0,2}?$
    pack_code: str  # Length 2-10
    position: int  # Minimum: 1
    quantity: int  # Minimum: 1
    
    # Basic card info
    name: str
    faction_code: str
    type_code: str
    subname: Optional[str]
    subtype_code: Optional[str]
    illustrator: Optional[str]
    flavor: Optional[str]
    text: Optional[str]
    traits: Optional[str]
    tags: Optional[str]
    
    # Variant/linking properties
    alternate_of: Optional[str]  # Pattern: ^[0-9]{5}[a-z]{0,2}?$
    duplicate_of: Optional[str]  # Pattern: ^[0-9]{5}[a-z]{0,2}?$
    bonded_to: Optional[str]
    bonded_count: Optional[int]  # Minimum: 1
    
    # Double-sided card properties
    double_sided: Optional[bool]
    back_name: Optional[str]
    back_subname: Optional[str]
    back_text: Optional[str]
    back_flavor: Optional[str]
    back_traits: Optional[str]
    back_illustrator: Optional[str]
    back_link: Optional[str]  # Pattern: ^[0-9]{5}[a-z]{0,2}?$
    
    # Card properties
    is_unique: Optional[bool]
    exceptional: Optional[bool]
    permanent: Optional[bool]
    exile: Optional[bool]
    myriad: Optional[bool]
    hidden: Optional[bool]
    
    # Numeric values (can be -4, -3, -2, null, or >= 0)
    cost: Optional[Union[int, None, Literal[-4, -3, -2]]]
    health: Optional[Union[int, None, Literal[-4, -3, -2]]]
    sanity: Optional[Union[int, None, Literal[-4, -3, -2]]]
    shroud: Optional[Union[int, None, Literal[-4, -3, -2]]]
    clues: Optional[Union[int, None, Literal[-4, -3, -2]]]
    doom: Optional[Union[int, None, Literal[-4, -3, -2]]]
    
    # Enemy properties
    enemy_fight: Optional[Union[int, None, Literal[-4, -3, -2]]]
    enemy_evade: Optional[Union[int, None, Literal[-4, -3, -2]]]
    enemy_damage: Optional[int]  # Minimum: 1
    enemy_horror: Optional[int]  # Minimum: 1
    health_per_investigator: Optional[bool]
    
    # Location/Act/Agenda properties
    stage: Optional[int]  # Minimum: 0
    encounter_code: Optional[str]
    encounter_position: Optional[int]  # Minimum: 1
    clues_fixed: Optional[bool]
    
    # Asset properties
    slot: Optional[str]
    deck_limit: Optional[int]  # Minimum: 0
    
    # Investigator properties
    deck_requirements: Optional[Union[str, None]]
    deck_options: Optional[Union[List[Any], None]]
    side_deck_requirements: Optional[str]
    side_deck_options: Optional[List[Any]]
    
    # Skills (can be -4, -3, -2, null, or >= 0)
    skill_willpower: Optional[Union[int, None, Literal[-4, -3, -2]]]
    skill_intellect: Optional[Union[int, None, Literal[-4, -3, -2]]]
    skill_combat: Optional[Union[int, None, Literal[-4, -3, -2]]]
    skill_agility: Optional[Union[int, None, Literal[-4, -3, -2]]]
    skill_wild: Optional[int]
    
    # Card values
    xp: Optional[int]  # Minimum: 0
    victory: Optional[int]  # Minimum: 0
    vengeance: Optional[int]  # Minimum: 0
    
    # Customization
    customization_text: Optional[str]
    customization_change: Optional[str]
    customization_options: Optional[List[Any]]
    
    # Multi-faction
    faction2_code: Optional[str]
    faction3_code: Optional[str]
    
    # Other
    restrictions: Optional[str]
    errata_date: Optional[str]  # Format: YYYY-MM-DD (minLength: 10)
