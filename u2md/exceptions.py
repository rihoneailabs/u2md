class URLToMarkdownError(Exception):
    """Base exception class for URL to Markdown converter."""
    pass


class URLFetchError(URLToMarkdownError):
    """Raised when URL content cannot be fetched."""
    pass


class ContentProcessingError(URLToMarkdownError):
    """Raised when fetched content processing fails."""
    pass
