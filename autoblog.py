import os
import random
import requests
import google.generativeai as genai
from pymed import PubMed
from datetime import datetime

# --- CONFIGURATION ---
# These are pulled from your GitHub Secrets
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# Using the 2026 stable flagship model
model = genai.GenerativeModel('gemini-2.0-flash')

def get_research():
    """Fetches a paper: 50% chance of a NEW study, 50% chance of a CLASSIC study."""
    pubmed = PubMed(tool="BioStrategist", email="your@email.com")
    is_classic = random.choice([True, False])
    
    if is_classic:
        # High-impact foundational papers from the gold-standard era of poultry research
        query = "poultry physiology[Title] AND (1990[PDAT] : 2012[PDAT])"
        source_label = "Classic Scientific Foundation"
    else:
        # Current innovation from the last 12 months
        query = f"poultry physiology[Title/Abstract] AND {datetime.now().year}[Date - Publication]"
        source_label = "Modern Research Digest"
        
    results = list(pubmed.query(query, max_results=1))
    if results:
        return results[0], source_label
    return None, None

def get_image(query):
    """Fetches a relevant scientific or farm image from Pexels API."""
    headers = {"Authorization": os.getenv("PEXELS_API_KEY")}
    url = f"https://api.pexels.com/v1/search?query={query}&per_page=1"
    try:
        res = requests.get(url, headers=headers).json()
        return res['photos'][0]['src']['large']
    except Exception:
        # Default high-quality fallback image
        return "https://images.pexels.com/photos/1769279/pexels-photo-1769279.jpeg"

def main():
    # 50/50 Logic: Flip a coin between PubMed Research and Textbook Fundamentals
    mode = random.choice(["research", "textbook"])
    
    if mode == "research":
        paper, source_label = get_research()
        if not paper: 
            mode = "textbook" # Fallback if PubMed returns no results
        else:
            title = paper.title
            prompt = f"""Act as a PhD Bio-Strategist. Summarize this {source_label} for our farm blog. 
            Paper Title: {paper.title}
            Abstract Body: {paper.abstract}
            
            Structure:
            1. The Scientific Discovery (What was found?)
            2. Biological Mechanism (How does it work inside the hen?)
            3. Farm Application (What should a manager do with this info?)
            4. Future Outlook.
            Write in a professional, insightful, and sophisticated tone."""
            image_query = "laboratory"

    if mode == "textbook":
        # Critical biological systems for high-level farm strategy
        topics = [
            "Medullary Bone and Calcium Mobilization in High-Production Layers",
            "The Ovarian Hierarchy: Selection and Maturation of Follicles",
            "Avian Thermoregulation: Evaporative Cooling and Heat Stress Biology",
            "Gut-Associated Lymphoid Tissue (GALT) and Avian Immunity",
            "Liver Metabolism: Lipogenesis and the Logistics of Yolk Formation",
            "Gizzard Function and Mechanical Digestion Efficiency",
            "The Endocrine Control of the Ovulatory Cycle"
        ]
        topic = random.choice(topics)
        title = f"Bio-Fundamentals: {topic}"
        prompt = f"""Act as a PhD Bio-Strategist. Provide a comprehensive summary of '{topic}' 
        based on the knowledge found in standard textbooks like 'Sturkie's Avian Physiology'. 
        Explain the fundamental biological systems involved and how they relate to hen health 
        and production efficiency. Use 5 clear, detailed paragraphs."""
        image_query = "anatomy diagram"

    # Execute the AI Synthesis
    response = model.generate_content(prompt)
    blog_text = response.text

    # Formatting for Jekyll
    date_str = datetime.now().strftime("%Y-%m-%d")
    # Sanitize title for filename
    clean_title = "".join(c for c in title if c.isalnum() or c.isspace()).replace(" ", "-").lower()[:50]
    filename = f"_posts/{date_str}-{clean_title}.md"
    img_url = get_image(image_query)

    # Construct the Markdown file with YAML Front Matter
    jekyll_content = f"""---
layout: post
title: "{title}"
date: {date_str}
image: {img_url}
category: {mode}
---

{blog_text}

---
*This digest was synthesized by the Farm Bio-Strategist AI, utilizing both recent literature and foundational avian science textbooks.*
"""
    # Write the file to the _posts folder
    with open(filename, "w", encoding="utf-8") as f:
        f.write(jekyll_content)
    
    print(f"Success! Published {mode} post: {title}")

if __name__ == "__main__":
    main()
