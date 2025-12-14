import os
import asyncio
import aiohttp
import random
import shutil
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from markdownify import markdownify as md


async def fetch(session, url):
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()

async def get_links(session, url, base_url):
    try:
        html = await fetch(session, url)
    except aiohttp.ClientError as e:
        print(f"Error accessing base URL: {url}. Details: {e}")
        return set()

    soup = BeautifulSoup(html, "html.parser")
    links = set()

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith("#"): continue
        
        full_url = urljoin(url, href)
        parsed = urlparse(full_url)

        if parsed.fragment: continue
        
        if not full_url.startswith(base_url): continue

        links.add(full_url)

    return links

async def process_url(session, url, output_folder, target_selector, exclude_tags, progress_bar, task_count, total_tasks):
    await asyncio.sleep(random.uniform(1, 3))

    try:
        html = await fetch(session, url)
        soup = BeautifulSoup(html, "html.parser")
             
        articles = soup.select(target_selector) 
        
        all_markdown_parts = []
        
        if articles:
            exclude_list = [s.strip() for s in exclude_tags.split(',') if s.strip()]

            for article in articles:
                if exclude_list:
                    for selector in exclude_list:
                        for element in article.select(selector): 
                            element.decompose()

                all_markdown_parts.append(md(str(article)))
                
            markdown_text = "\n\n---\n\n".join(all_markdown_parts)

        else:
            markdown_text = f"Error: No elements found for selector '{target_selector}' on this page."

        filename = urlparse(url).path.strip("/").replace("/", "_") or "index"
        filepath = os.path.join(output_folder, f"{filename}.md")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(markdown_text)
        
        task_count[0] += 1
        if progress_bar:
            progress_bar.progress(task_count[0] / total_tasks, text=f"SUCCESS: {task_count[0]}/{total_tasks} - {url}")
        
        return True

    except Exception as e:
        print(f"Error processing {url}: {e}")
        
    task_count[0] += 1
    if progress_bar:
        progress_bar.progress(task_count[0] / total_tasks, text=f"ERROR: {task_count[0]}/{total_tasks} - {url}")
    
    return False

async def run_scraper(base_url, output_folder, target_selector, exclude_tags_str, progress_bar, include_base_url):
    os.makedirs(output_folder, exist_ok=True)
    
    async with aiohttp.ClientSession() as session:
        urls = await get_links(session, base_url, base_url)
        
        if include_base_url:
            urls.add(base_url)
        
        total_tasks = len(urls)
        
        if total_tasks == 0:
            return 0, 0
            
        task_count = [0]
        tasks = [process_url(session, url, output_folder, target_selector, exclude_tags_str, progress_bar, task_count, total_tasks) for url in urls]
        results = await asyncio.gather(*tasks)
        successful_count = results.count(True)
        return successful_count, total_tasks

def clear_scraped_data(folder_path):
    if os.path.exists(folder_path):
        try:
            shutil.rmtree(folder_path) 
            return True
        except Exception as e:
            return f"Deletion Error: {e}"
    return True