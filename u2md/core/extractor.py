import io
import logging
import re
from typing import Optional

import google.generativeai as genai
from unstructured.partition.html import partition_html

from ..exceptions import URLFetchError, URLToMarkdownError, ContentProcessingError
from ..models import HTMLContent

logger = logging.getLogger(__name__)


class ContentPreprocessor:
    def __init__(self):
        self.markdown_pattern = re.compile(r'```markdown(.*?)```', re.DOTALL)

    @staticmethod
    def process_elements(elements: list) -> str:
        try:
            processed_text = io.StringIO('')
            for element in elements:
                processed_text.write(f"{type(element)} : {str(element)}\n")
            return processed_text.getvalue()
        except Exception as e:
            logger.error(f"Error processing elements: {str(e)}")
            raise ContentProcessingError(f"Failed to process HTML elements: {str(e)}")

    def extract_markdown(self, text: str) -> Optional[str]:
        try:
            matches = self.markdown_pattern.findall(text)
            if matches:
                return matches[0].strip()
            return None
        except Exception as e:
            logger.error(f"Error extracting markdown: {str(e)}")
            raise ContentProcessingError(f"Failed to extract markdown: {str(e)}")


class URLContentExtractor:

    def __init__(
            self,
            gemini_api_key: str
    ):
        self.preprocessor = ContentPreprocessor()
        self._setup_gemini(gemini_api_key)

    def _setup_gemini(
            self,
            api_key: str,
            model_name: str = 'gemini-2.0-flash-exp',
    ) -> None:
        """Setup Gemini model configuration.

        Args:
            api_key: Gemini API key obtained from Google Cloud Console
        """
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                model_name=model_name,
                generation_config={
                    "temperature": 0,
                    "max_output_tokens": 8192,
                    "response_mime_type": "text/plain",
                }
            )
            self.chat_session = self.model.start_chat(history=[])
        except Exception as e:
            logger.error(f"Failed to setup Gemini model: {str(e)}")
            raise URLToMarkdownError(f"Gemini model initialization failed: {str(e)}")

    def _format_with_gemini(self, raw_text: str) -> str:
        """Convert to markdown using Gemini LLM"""
        prompt = f"""Given the following unstructured text obtained from reading an html page. Please kindly infer the appropriate markdown format \
using the type of each line item as a hint for the corresponding markdown element.
Raw Text:
###
{raw_text}
###

Special instructions:
  - Return, just the markdown text within ```markdown ``` delimeter
  - Where applicable, ignore footer text which does not add anything valuable to the rest of the content
"""
        response = self.chat_session.send_message(prompt)
        return response.text

    def extract_content(self, url: str, **kwargs) -> HTMLContent:
        """Extract content from a URL and convert to markdown.

        Args:
            url: URL to extract content from
            **kwargs: Additional keyword arguments to be passed to `unsupervised.partition_html()`

        Returns:
            HTMLContent object containing processed content

        Raises:
            URLFetchError: If URL content cannot be fetched
            ContentProcessingError: If content processing fails
        """
        try:
            logger.info(f"Extracting content from URL: {url}")
            elements = partition_html(url=url, **kwargs)
            logger.debug(f"Found {len(elements)} HTML elements")
            raw_text = self.preprocessor.process_elements(elements)

            gemini_response = self._format_with_gemini(raw_text)
            markdown = self.preprocessor.extract_markdown(gemini_response)
            content = HTMLContent(
                raw_text=raw_text,
                markdown=markdown,
                elements=elements,
                metadata={
                    "url": url,
                    "element_count": len(elements)
                }
            )

            logger.info("Successfully extracted and processed content")
            return content

        except Exception as e:
            logger.error(f"Failed to extract content: {str(e)}")
            raise URLFetchError(f"Failed to extract content from URL: {str(e)}")
