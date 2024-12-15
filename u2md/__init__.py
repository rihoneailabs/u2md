__version__ = "0.1.0rc1"
__author__ = "Ndamulelo Nemakhavhani"

from .core.extractor import URLContentExtractor
from .models import HTMLContent

__all__ = [
    "URLContentExtractor",
    "HTMLContent"
]
