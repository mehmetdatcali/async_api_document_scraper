# Async API Document Scraper to Markdown

This tool is designed to crawl documentation websites concurrently, extract specific content areas using CSS selectors, and convert the output into clean **Markdown (`.md`)** files. It is optimized for building local knowledge bases, datasets for **RAG (Retrieval-Augmented Generation)** systems, or offline archiving.

## Tech Stack & Logic

*   **Asynchronous I/O:** Utilizes `asyncio` and `aiohttp` to handle multiple network requests concurrently, significantly reducing scrape time compared to synchronous methods.
*   **Content Extraction:** Uses `BeautifulSoup` to parse HTML and isolate content based on user-defined **CSS Selectors**, ensuring only relevant text is captured.
*   **Format Conversion:** Automatically transforms HTML structures (tables, lists, code blocks) into Markdown using `markdownify`.
*   **Politeness:** Implements random delays between requests to respect server load.

## Usage Guide

1.  **Settings (Sidebar):**
    *   **Base URL:** The starting point of the documentation (e.g., `https://docs.streamlit.io/develop/api-reference/`).
    *   **Target Selector:** The **HTML Tag**, **CSS ID**, or **Class** of the main content area (e.g., `#documentation`).
    *   **Excluded Selector:** Tags or classes to remove from the content (e.g., `nav, a, .version-select, .callout_Container__TMaoi, .psa_Container__YutqA`).
2.  **Execution:** Click **Start**. The tool will fetch pages matching the base path.
3.  **Output:** You can **preview** the scraped Markdown content directly within the **App** tab or download all files as a `.zip` archive.