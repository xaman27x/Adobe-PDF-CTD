import fitz  # PyMuPDF
import numpy as np
from sklearn.cluster import KMeans
from collections import defaultdict
from .utils import clean_text, is_heading_candidate

def extract_headings_from_pdf(file_path):
    doc = fitz.open(file_path)
    text_blocks = []
    font_sizes = []

    # First pass: collect all text blocks and font sizes
    for page_num, page in enumerate(doc, start=1):
        page_height = page.rect.height
        
        for block in page.get_text("dict")["blocks"]:
            if block["type"] != 0:  # Skip non-text blocks
                continue
                
            block_text = ""
            block_font_sizes = []
            is_bold = False
            line_count = 0
            
            for line in block.get("lines", []):
                line_text = ""
                line_font_sizes = []
                
                for span in line.get("spans", []):
                    line_text += span["text"]
                    line_font_sizes.append(span["size"])
                    if "bold" in span["font"].lower():
                        is_bold = True
                
                if line_text.strip():
                    block_text += line_text + " "
                    block_font_sizes.extend(line_font_sizes)
                    line_count += 1
            
            clean_block = clean_text(block_text)
            if clean_block and line_count <= 3:  # Headings are usually 1-3 lines
                avg_font_size = np.mean(block_font_sizes) if block_font_sizes else 0
                y_position = block["bbox"][1]
                y_ratio = y_position / page_height
                
                text_blocks.append({
                    "text": clean_block,
                    "font_size": avg_font_size,
                    "is_bold": is_bold,
                    "y_ratio": y_ratio,
                    "page": page_num,
                    "bbox": block["bbox"]  # For spatial analysis
                })
                font_sizes.append(avg_font_size)

    if not text_blocks:
        return ("Untitled Document", [])

    # Determine heading levels using font size distribution
    if len(font_sizes) > 3:
        percentiles = np.percentile(font_sizes, [75, 90, 95])
    else:
        percentiles = [max(font_sizes)*0.9, max(font_sizes)*0.95, max(font_sizes)]

    # Classify headings
    headings = []
    for block in text_blocks:
        if not is_heading_candidate(block["text"]):
            continue
            
        if block["font_size"] >= percentiles[2]:
            level = "H1"
        elif block["font_size"] >= percentiles[1]:
            level = "H2"
        elif block["font_size"] >= percentiles[0]:
            level = "H3"
        else:
            continue  # Not a heading
            
        headings.append({
            "level": level,
            "text": block["text"],
            "page": block["page"]
        })

    # Post-process to fix hierarchy
    headings = validate_hierarchy(headings)
    
    # Extract title - first H1 or largest text on first page
    title = "Untitled Document"
    first_page_blocks = [b for b in text_blocks if b["page"] == 1]
    if first_page_blocks:
        title_candidates = [
            b for b in first_page_blocks 
            if (b["font_size"] >= np.percentile(font_sizes, 90) or 
                b["y_ratio"] < 0.2)
        ]
        if title_candidates:
            title = max(title_candidates, key=lambda x: x["font_size"])["text"]
        else:
            title = max(first_page_blocks, key=lambda x: x["font_size"])["text"]
    
    # If we found H1s, use the first one as title if better match
    h1s = [h for h in headings if h["level"] == "H1"]
    if h1s and (len(title) < len(h1s[0]["text"]) or len(title.split()) > 10):
        title = h1s[0]["text"]

    return title, headings

def validate_hierarchy(headings):
    """Ensure proper heading nesting and remove duplicates"""
    if not headings:
        return []
    
    # Remove consecutive duplicates
    cleaned = []
    last_text = None
    for h in headings:
        if h["text"] != last_text:
            cleaned.append(h)
            last_text = h["text"]
    
    # Fix hierarchy - H2 must follow H1, etc.
    fixed = []
    current_level = 0
    level_map = {"H1": 1, "H2": 2, "H3": 3}
    
    for h in cleaned:
        new_level = level_map[h["level"]]
        if new_level > current_level + 1:
            # Skip or demote the heading
            continue
        current_level = new_level
        fixed.append(h)
    
    return fixed