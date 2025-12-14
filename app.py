import streamlit as st
import os
import io
import asyncio
import glob
import zipfile
import scraper

DEFAULT_OUTPUT_FOLDER = "files"
DEFAULT_BASE_URL = "https://fastapi.tiangolo.com/reference/"
DEFAULT_TARGET_SELECTOR = "article"
DEFAULT_EXCLUDE_TAGS = ".mkdocstrings-source"

st.set_page_config(layout="wide", page_title="Async API Document Scraper", initial_sidebar_state="expanded")

output_folder = DEFAULT_OUTPUT_FOLDER
app_tab, read_tab = st.tabs(["App", "Read"])

with st.sidebar:
    st.header("Settings")
    
    user_base_url = st.text_input("Base URL (Required)", value=DEFAULT_BASE_URL)
    user_target_selector = st.text_input("Target Selector (Required)", value=DEFAULT_TARGET_SELECTOR, help="Use comma for multiple selection. (e.g., tagname, #idname, .classname)")
    user_exclude_tags = st.text_area("Excluded Selector", value=DEFAULT_EXCLUDE_TAGS, help="Use comma for multiple selection. (e.g., tagname, #idname, .classname)")
    include_base_url_check = st.checkbox("Include Base URL", value=True)
    col1, col2 = st.columns(2) 

    if col1.button("Start", type="primary", use_container_width=True):
        
        if not user_base_url.strip():
            st.error("Base URL is required.")
        elif not user_target_selector.strip():
            st.error("Target Selector is required.")
        else:
            with app_tab:
                progress_bar_container = st.empty()
                progress_bar = progress_bar_container.progress(0, text="Starting...")

            try:
                scraper.clear_scraped_data(output_folder)
                
                with st.spinner("Scraping in progress..."):
                    successful_count, total_tasks = asyncio.run(scraper.run_scraper(
                        user_base_url, 
                        output_folder, 
                        user_target_selector, 
                        user_exclude_tags, 
                        progress_bar,
                        include_base_url_check
                    ))
                    
                    with app_tab:
                        if total_tasks > 0:
                            if successful_count > 0:
                                progress_bar_container.success(f"Scraping Completed! ({successful_count}/{total_tasks} pages saved)")
                            else:
                                progress_bar_container.error(f"Scraping completed but no pages were saved. ({successful_count}/{total_tasks}).")
                        else:
                             progress_bar_container.warning("No links found to scrape.")
                        
            except Exception as e:
                with app_tab:
                    st.exception(e)
                    progress_bar_container.error(f"Critical Error: {e}")

    if col2.button("Clear", use_container_width=True):
        result = scraper.clear_scraped_data(output_folder)
        if result is True:
            st.success("Folder and contents deleted.")
        else:
            st.error(f"Error during clear operation: {result}")


with app_tab:
    if os.path.exists(output_folder):
        md_files = glob.glob(os.path.join(output_folder, "*.md"))
        
        if md_files:
            st.subheader("Markdown Files")
            
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file_path in md_files:
                    zip_file.write(file_path, os.path.basename(file_path))
            
            st.download_button(
                label="Download All (.zip)",
                data=zip_buffer.getvalue(),
                file_name="documents.zip",
                mime="application/zip",
                key="download_zip_app" 
            )
            
            md_files.sort()
            
            for file_path in md_files:
                file_name = os.path.basename(file_path)
                with st.expander(file_name):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        st.markdown(content) 
                    except Exception as e:
                        st.error(f"File read error: {e}")
        else:
            st.info(f"Adjust the settings and start scraping.")
    else:
        st.warning(f"Adjust the settings and start scraping.")


with read_tab:
    st.markdown("""
    ### Async API Document Scraper to Markdown

    This tool is designed to crawl documentation websites concurrently, extract specific content areas using CSS selectors, and convert the output into clean **Markdown (`.md`)** files. It is optimized for building local knowledge bases, datasets for **RAG (Retrieval-Augmented Generation)** systems, or offline archiving.

    #### Tech Stack & Logic
    *   **Asynchronous I/O:** Utilizes `asyncio` and `aiohttp` to handle multiple network requests concurrently, significantly reducing scrape time compared to synchronous methods.
    *   **Content Extraction:** Uses `BeautifulSoup` to parse HTML and isolate content based on user-defined **CSS Selectors**, ensuring only relevant text is captured.
    *   **Format Conversion:** Automatically transforms HTML structures (tables, lists, code blocks) into Markdown using `markdownify`.
    *   **Politeness:** Implements random delays between requests to respect server load.

    #### Usage Guide
    1.  **Settings (Sidebar):**
        *   **Base URL:** The starting point of the documentation (e.g., `https://docs.streamlit.io/develop/api-reference/`).
        *   **Target Selector:** The **HTML Tag**, **CSS ID**, or **Class** of the main content area (e.g., `#documentation`).
        *   **Excluded Selector:** Tags or classes to remove from the content (e.g., `nav, a, .version-select, .callout_Container__TMaoi, .psa_Container__YutqA`).
    2.  **Execution:** Click **Start**. The tool will fetch pages matching the base path.
    3.  **Output:** You can **preview** the scraped Markdown content directly within the **App** tab or download all files as a `.zip` archive.
    """)