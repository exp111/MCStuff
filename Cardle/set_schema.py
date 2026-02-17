from typing import TypedDict, Optional


class Set(TypedDict):
    code: str
    name: str
    card_set_type_code: str
    parent_code: Optional[str]  # Can be a string or None