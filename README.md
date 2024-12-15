# U2md

This utility package extracts structured markdown content from web URLs using `unstructured` and `Google's Gemini API`


## Installation

- Install from GitHub

    ```bash
    pip install git+git://github.com/ndamulelonemakh/u2md.git
    ```

## Usage

- Setup the API key

    ```bash
    export GEMINI_API_KEY=<your-api-key>
    ```
- Run from the command line

    ```bash
    u2md <url>
    ```
- Run from Python

    ```python
    from u2md import URLContentExtractor

    # see ./demo.py for more details
    ```

## Run Demo

- Streamlit app

    ```bash
    streamlit run demo.py
    ```

- [Live demo](https://u2md-live.streamlit.app/)

