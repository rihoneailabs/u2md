import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional

from .core.extractor import URLContentExtractor
from .exceptions import URLToMarkdownError
from .utils.logger import setup_logging


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description="Extract and convert URL content to markdown format.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://example.com --output markdown.md
  %(prog)s https://example.com --metadata meta.json --log-file conversion.log
        """
    )

    parser.add_argument(
        "url",
        help="URL to extract content from"
    )

    parser.add_argument(
        "-o", "--output",
        help="Output file for markdown content (default: stdout)",
        type=str
    )

    parser.add_argument(
        "--metadata",
        help="Output file for metadata in JSON format",
        type=str
    )

    parser.add_argument(
        "--log-file",
        help="Log file path (default: url_to_markdown.log)",
        default="url_to_markdown.log"
    )

    parser.add_argument(
        "--api-key",
        help="Gemini API key (can also be set via GEMINI_API_KEY env variable)",
        type=str,
        required=False
    )

    parser.add_argument(
        "-v", "--verbose",
        help="Enable verbose output",
        action="store_true"
    )

    return parser


def write_output(content: str, output_file: Optional[str] = None) -> None:
    """Write content to file or stdout."""
    if output_file:
        Path(output_file).write_text(content)
    else:
        print(content)


def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    log_level = "DEBUG" if args.verbose else "INFO"
    logger = setup_logging(
        level=getattr(logging, log_level),
        log_file=args.log_file
    )

    try:
        api_key = args.api_key or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            logger.error("No Gemini API key provided. Use --api-key or set GEMINI_API_KEY environment variable")
            return 1

        extractor = URLContentExtractor(gemini_api_key=api_key)

        logger.info(f"Extracting content from {args.url}..")
        content = extractor.extract_content(url=args.url)

        # Write markdown content
        if content.markdown:
            write_output(content.markdown, args.output)
            logger.info(
                f"Markdown content written to {args.output if args.output else 'stdout'}"
            )
        else:
            logger.warning("No markdown content extracted")

        # Write metadata if requested
        if args.metadata and content.metadata:
            Path(args.metadata).write_text(
                json.dumps(content.metadata, indent=2)
            )
            logger.info(f"Metadata written to {args.metadata}")

        return 0

    except URLToMarkdownError as e:
        logger.exception(f"Error processing URL: {str(e)}")
        return 1
    except Exception as e:
        logger.exception(f"Unexpected error occurred\n{str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
