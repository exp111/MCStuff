from typing import TypedDict, Optional


class Pack(TypedDict):
    code: str
    name: str
    pack_type_code: str
    position: int
    date_release: Optional[str]  # Can be a string or None
    size: Optional[int]  # Can be an integer or None
    cgdb_id: Optional[int]  # Optional because it's not in "required"
    octgn_id: Optional[str]  # Optional because it's not in "required"