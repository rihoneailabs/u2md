import json
from datetime import datetime
from pathlib import Path
from typing import Tuple

import streamlit as st

from u2md import URLContentExtractor
from u2md.exceptions import URLToMarkdownError


def initialize_session_state():
    if "conversion_history" not in st.session_state:
        st.session_state.conversion_history = []


def save_to_file(content: str, file_path: str) -> None:
    Path(file_path).write_text(content)


def process_url(url: str, api_key: str) -> Tuple[str, dict]:
    extractor = URLContentExtractor(gemini_api_key=api_key)
    content = extractor.extract_content(url=url)
    return content.markdown, content.metadata


def main():
    st.set_page_config(page_title="URL to Markdown Converter", page_icon="📝", layout="wide")
    initialize_session_state()

    # Sidebar configuration
    with st.sidebar:
        st.header("Settings")
        api_key = st.text_input("Gemini API Key", type="password", help="Enter your Gemini API key")
        temperature = st.slider(
            "Temperature", min_value=0.0, max_value=1.0, value=0.2, step=0.1, help="Controls randomness in the output"
        )

        st.markdown("---")
        st.markdown("### History")
        for idx, (url, time) in enumerate(st.session_state.conversion_history[-5:]):
            st.markdown(f"{idx+1}. [{url[:20]}]({url})")

    # Main content
    st.title("URL to Markdown Converter")
    st.markdown(
        """
        Convert web content to clean markdown format using AI.
        Simply enter a URL below to get started.
        """
    )

    url = st.text_input("Enter URL", placeholder="https://docs.python.org/3/library/security_warnings.html")
    col1, col2 = st.columns(2)

    if col1.button("Convert to Markdown", type="primary"):
        if not api_key:
            st.error("Please enter your Gemini API key in the sidebar")
            return

        if not url:
            st.error("Please enter a URL")
            return

        try:
            with st.spinner("Converting..."):
                markdown, metadata = process_url(
                    url=url, 
                    api_key=api_key, 
                    # temperature=temperature
                )

                st.session_state.conversion_history.append((url, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                tab1, tab2, tab3 = st.tabs(["Raw", "Preview", "Metadata"])

                with tab1:
                    st.text_area("Generated Markdown", markdown, height=400)

                with tab2:
                    st.markdown(markdown)

                with tab3:
                    st.json(metadata)

                # horizontal rule
                st.markdown("---")

                # Export options
                st.markdown("### Export Options")
                col1, col2 = st.columns(2)

                markdown_file = col1.text_input("Markdown filename", value="output.md")
                metadata_file = col2.text_input("Metadata filename", value="metadata.json")

                if st.button("Save Files"):
                    try:
                        save_to_file(markdown, markdown_file)
                        save_to_file(json.dumps(metadata, indent=2), metadata_file)
                        st.success("Files saved successfully!")
                    except Exception as e:
                        st.error(f"Error saving files: {str(e)}. Please try again.")

        except URLToMarkdownError as e:
            st.error(f"Error processing URL: {str(e)}")
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    main()
