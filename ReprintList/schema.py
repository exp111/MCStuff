from typing import TypedDict, List, Optional


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
    code: str
    pack_code: str
    position: int
    quantity: int
    name: Optional[str]
    faction_code: Optional[str]
    type_code: Optional[str]
    attack: Optional[int]
    attack_cost: Optional[int]
    attack_star: Optional[bool]
    back_flavor: Optional[str]
    back_text: Optional[str]
    base_threat: Optional[int]
    base_threat_fixed: Optional[bool]
    boost: Optional[int]
    boost_star: Optional[bool]
    cost: Optional[int]
    cost_per_hero: Optional[bool]
    deck_limit: Optional[int]
    deck_options: Optional[List[DeckOption]]
    deck_requirements: Optional[List[DeckRequirement]]
    defense: Optional[int]
    defense_star: Optional[bool]
    double_sided: Optional[bool]
    duplicate_of: Optional[str]
    errata: Optional[str]
    escalation_threat: Optional[int]
    escalation_threat_fixed: Optional[bool]
    escalation_threat_star: Optional[bool]
    flavor: Optional[str]
    hand_size: Optional[int]
    health: Optional[int]
    health_per_hero: Optional[bool]
    health_star: Optional[bool]
    illustrator: Optional[str]
    is_unique: Optional[bool]
    permanent: Optional[bool]
    recover: Optional[int]
    recover_star: Optional[bool]
    resource_energy: Optional[int]
    resource_mental: Optional[int]
    resource_physical: Optional[int]
    resource_wild: Optional[int]
    restrictions: Optional[str]
    scheme_acceleration: Optional[int]
    scheme_crisis: Optional[int]
    scheme_hazard: Optional[int]
    scheme_star: Optional[bool]
    set_code: Optional[str]
    stage: Optional[int]
    subname: Optional[str]
    text: Optional[str]
    threat: Optional[int]
    threat_fixed: Optional[bool]
    threat_star: Optional[bool]
    thwart: Optional[int]
    thwart_cost: Optional[int]
    thwart_star: Optional[bool]
    traits: Optional[str]
