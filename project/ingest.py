import os
import re
import sys
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Import config settings
try:
    from config import PDF_PATH, CHUNK_SIZE, CHUNK_OVERLAP
except ImportError:
    # Fallback to defaults if run directly
    PDF_PATH = "data/final_geeta.pdf"
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 100


def clean_line(line: str) -> str:
    """Cleans up leading/trailing whitespaces from a line."""
    return line.strip()


def is_ignored_line(line: str) -> bool:
    """
    Checks if a line matches header, footer, or page number patterns.
    
    Examples:
      - 'Srimad Bhagavad Gita - Adhyay 16 Study Guide'
      - 'Confidential - For Personal Study Only'
      - 'Page 1' or 'Page 2'
    """
    cleaned = line.strip().lower()
    if not cleaned:
        return False
        
    # Ignore Header lines
    if "adhyay 16 study guide" in cleaned or "srimad bhagavad gita" in cleaned:
        return True
        
    # Ignore Footer lines
    if "confidential - for personal study only" in cleaned:
        return True
        
    # Ignore Page numbers (e.g. "page 1", "page 12")
    if re.match(r'^page\s+\d+$', cleaned):
        return True
        
    # Ignore standalone numbers at edge
    if re.match(r'^\d+$', cleaned):
        return True
        
    return False


def load_pdf(pdf_path: str) -> list[dict]:
    """
    Ingests the PDF page-by-page, filters out ignored lines (headers, footers, pages),
    and aggregates cleaned text metadata.
    
    Returns:
        list: A list of dicts containing page number and cleaned page text.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at: {pdf_path}")
        
    reader = PdfReader(pdf_path)
    pages_data = []
    
    print(f"Loading and extracting pages from: {pdf_path}")
    for idx, page in enumerate(reader.pages):
        page_num = idx + 1
        raw_text = page.extract_text() or ""
        
        # Clean lines and filter headers/footers/page numbers
        filtered_lines = []
        for line in raw_text.splitlines():
            line_cleaned = clean_line(line)
            if not is_ignored_line(line_cleaned):
                filtered_lines.append(line_cleaned)
                
        # Reconstruct page text preserving structure
        cleaned_page_text = "\n".join(filtered_lines)
        
        # Collapse excessive newlines
        cleaned_page_text = re.sub(r'\n{3,}', '\n\n', cleaned_page_text)
        
        pages_data.append({
            "page": page_num,
            "text": cleaned_page_text.strip()
        })
        
    return pages_data


def detect_metadata(text: str) -> tuple[str, str]:
    """
    Analyses chunk content to infer its dominant language and text classification type.
    
    Returns:
        tuple: (language, text_type)
    """
    # Devanagari range is U+0900 to U+097F
    has_devanagari = bool(re.search(r'[\u0900-\u097f]', text))
    has_english = bool(re.search(r'[a-zA-Z]', text))
    
    # Detect structural type
    if "॥" in text or "।" in text:
        text_type = "Shloka"
    elif "translation" in text.lower() or "अनुवाद" in text or "अर्थ" in text:
        text_type = "Translation"
    else:
        text_type = "Explanation"
        
    # Detect language representation
    if has_devanagari and has_english:
        language = "Hindi + English"
    elif has_devanagari:
        language = "Hindi"
    else:
        language = "English"
        
    return language, text_type


def get_verse_number(text: str) -> int:
    """Attempts to find a verse index referenced in the chunk (e.g. Verse 3 or Verse 21)."""
    match = re.search(r'\[Verse\s+(\d+)\]', text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    match_num = re.search(r'॥\s*(\d+)\s*॥', text)
    if match_num:
        return int(match_num.group(1))
    return None


def get_chapter_and_source(pdf_path: str, pages_data: list) -> tuple[int, str]:
    """Dynamically extracts the chapter number and source description from the PDF context and filename."""
    first_page_text = pages_data[0]["text"] if pages_data else ""
    
    # Try matching "Adhyay <num>" or "Chapter <num>"
    match = re.search(r'(adhyay|chapter|अध्याय)\s+(\d+)', first_page_text, re.IGNORECASE)
    if match:
        chapter = int(match.group(2))
    else:
        # Fallback to reading digits from the filename
        digits = re.findall(r'\d+', os.path.basename(pdf_path))
        chapter = int(digits[0]) if digits else 16
        
    filename_base = os.path.splitext(os.path.basename(pdf_path))[0]
    source_clean = filename_base.replace("_", " ").replace("-", " ").title()
    
    # Prepend 'Bhagavad Gita' if referencing geeta/gita
    if "geeta" in source_clean.lower() or "gita" in source_clean.lower():
        # Keep clean title
        pass
    else:
        source_clean = f"Bhagavad Gita {source_clean}"
        
    return chapter, source_clean


def get_chunks() -> list[dict]:
    """
    Ingests and chunks the Bhagavad Gita document, adding structured metadata to each chunk.
    
    Returns:
        list[dict]: List of chunks with 'text' and 'metadata'.
    """
    pages_data = load_pdf(PDF_PATH)
    chapter_num, source_name = get_chapter_and_source(PDF_PATH, pages_data)
    print(f"Extracted Metadata context - Chapter: {chapter_num}, Source: '{source_name}'")
    
    # Initialize recursive text splitter with custom delimiters to avoid breaking shlokas
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""]
    )
    
    processed_chunks = []
    chunk_id_counter = 1
    
    for page_info in pages_data:
        page_num = page_info["page"]
        text_content = page_info["text"]
        
        # Split text of the page
        splits = splitter.split_text(text_content)
        
        for split in splits:
            lang, txt_type = detect_metadata(split)
            verse_num = get_verse_number(split)
            
            # Construct chunk dictionary matching specification metadata
            chunk_data = {
                "text": split,
                "metadata": {
                    "chapter": chapter_num,
                    "page": page_num,
                    "chunk_id": chunk_id_counter,
                    "language": lang,
                    "source": source_name,
                    "text_type": txt_type,
                    "verse": verse_num
                }
            }
            processed_chunks.append(chunk_data)
            chunk_id_counter += 1
            
    print(f"Successfully processed {len(processed_chunks)} metadata-annotated chunks.")
    return processed_chunks


def safe_print(text: str):
    """Prints text safely to standard output by handling console encoding mismatches on Windows."""
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback to replacing unencodable characters with '?' or similar
        encoding = sys.stdout.encoding or 'utf-8'
        print(text.encode(encoding, errors='replace').decode(encoding))


if __name__ == "__main__":
    chunks = get_chunks()
    if chunks:
        print("\nSample Chunk 1 Metadata:")
        print(chunks[0]["metadata"])
        print("\nSample Chunk 1 Text:")
        safe_print(chunks[0]["text"])
