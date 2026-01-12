import os
import requests
import google.generativeai as genai
from pymed import PubMed
from datetime import datetime

# --- SETUP ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

def get_poultry_research():
    pubmed = PubMed(tool="BioStrategist", email="your@email.com")
    # Search for poultry physiology papers from the current year
    query = f"poultry physiology[Title/Abstract] AND {datetime.now().year}[Date - Publication]"
    results = list(pubmed.query(query, max_results=1))
    return results[0] if results else None

def get_image(query):
    headers = {"Authorization": os.getenv("PEXELS_API_KEY")}
    url = f"https://api.pexels.com/v1/search?query={query}&per_page=1"
    try:
        res = requests.get(url, headers=headers).json()
        return res['photos'][0]['src']['large']
    except:
        return "https://images.pexels.com/photos/1769279/pexels-photo-1769279.jpeg" # Fallback chicken image

def main():
    paper = get_poultry_research()
    if not paper:
        print("No new research found today.")
        return

    # Generate Blog content
    prompt = f"""
    Act as a PhD Bio-Strategist for a farm. 
    Summarize this research paper for a general audience in 5 engaging paragraphs.
    Include sections on: Hook, The Science, Farm Impact, and Future Outlook.
    Research Title: {paper.title}
    Abstract: {paper.abstract}
    """
    response = model.generate_content(prompt)
    blog_text = response.text

    # Prepare Jekyll File
    date_str = datetime.now().strftime("%Y-%m-%d")
    # Clean title for filename (remove special characters)
    clean_title = "".join(c for c in paper.title if c.isalnum() or c.isspace()).replace(" ", "-").lower()[:50]
    filename = f"_posts/{date_str}-{clean_title}.md"
    
    img_url = get_image("poultry farm")

    # Jekyll Header (Front Matter)
    jekyll_content = f"""---
layout: post
title: "{paper.title}"
date: {date_str}
image: {img_url}
---

{blog_text}

*Source: PubMed Research Digest*
"""
    # Write the file
    with open(filename, "w", encoding="utf-8") as f:
        f.write(jekyll_content)
    print(f"Successfully created: {filename}")

if __name__ == "__main__":
    main()
