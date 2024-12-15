from dataclasses import dataclass
from typing import List, Optional

@dataclass
class HTMLContent:
    """Data class to store processed HTML content."""
    raw_text: str
    markdown: Optional[str] = None
    elements: List[str] = None
    metadata: dict = None