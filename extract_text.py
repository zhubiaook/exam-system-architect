"""
PDF Chapter Text Extractor for System Architecture Designer Textbook (2nd Edition)

Usage:
    python extract_text.py                  # Extract all chapters
    python extract_text.py 5                 # Extract only chapter 5
    python extract_text.py 1 3 5             # Extract chapters 1, 3, and 5

PDF Structure:
    - Table of Contents (ToC): PDF pages 5-13 (1-indexed)
    - Content starts at: PDF page 14 (1-indexed)
    - ToC page X corresponds to PDF page X + 12

Output:
    - Files are saved to ./text/第X章_章节名.txt
"""

import os
import sys

from pypdf import PdfReader

# =============================================================================
# Configuration
# =============================================================================
PDF_FILE = "materials/textbook_system_architect_2nd.pdf"
OUTPUT_DIR = "materials/text"

# Page offset: ToC page number + PAGE_OFFSET = Actual PDF page number (1-indexed)
PAGE_OFFSET = 12

# Chapter definitions from the Table of Contents
# Format: (chapter_number, chapter_name, toc_start_page, toc_end_page)
# Pages are as shown in the ToC (not the actual PDF page numbers)
CHAPTERS = [
    (1, "绪论", 3, 23),
    (2, "计算机系统基础知识", 24, 104),
    (3, "信息系统基础知识", 105, 144),
    (4, "信息安全技术基础知识", 145, 174),
    (5, "软件工程基础知识", 175, 217),
    (6, "数据库设计基础知识", 218, 247),
    (7, "系统架构设计基础知识", 248, 270),
    (8, "系统质量属性与架构评估", 271, 304),
    (9, "软件可靠性基础知识", 305, 329),
    (10, "软件架构的演化和维护", 330, 368),
    (11, "未来信息综合技术", 369, 404),
    (12, "信息系统架构设计理论与实践", 405, 450),
    (13, "层次式架构设计理论与实践", 451, 481),
    (14, "云原生架构设计理论与实践", 482, 511),
    (15, "面向服务架构设计理论与实践", 512, 540),
    (16, "嵌入式系统架构设计理论与实践", 541, 598),
    (17, "通信系统架构设计理论与实践", 599, 632),
    (18, "安全架构设计理论与实践", 633, 675),
    (19, "大数据架构设计理论与实践", 676, 701),
    (20, "系统架构设计师论文写作要点", 702, 712),
]


# =============================================================================
# Functions
# =============================================================================
def toc_page_to_pdf_page(toc_page: int) -> int:
    """Convert a ToC page number to the actual 1-indexed PDF page number."""
    return toc_page + PAGE_OFFSET


def pdf_page_to_index(pdf_page: int) -> int:
    """Convert a 1-indexed PDF page number to a 0-indexed list index."""
    return pdf_page - 1


def extract_chapter(
    reader: PdfReader,
    chapter_num: int,
    chapter_name: str,
    toc_start: int,
    toc_end: int,
    output_dir: str,
) -> str:
    """
    Extract a single chapter's text.

    Args:
        reader: PdfReader instance
        chapter_num: Chapter number
        chapter_name: Chapter title
        toc_start: Start page from ToC
        toc_end: End page from ToC
        output_dir: Directory to save output

    Returns:
        Path to the created file
    """
    start_pdf_page = toc_page_to_pdf_page(toc_start)
    end_pdf_page = toc_page_to_pdf_page(toc_end)

    start_idx = pdf_page_to_index(start_pdf_page)
    end_idx = pdf_page_to_index(end_pdf_page)  # Inclusive

    text_parts = []
    for i in range(start_idx, end_idx + 1):
        if i < len(reader.pages):
            text_parts.append(f"--- Page {i + 1} ---")
            page_text = reader.pages[i].extract_text()
            if page_text:
                text_parts.append(page_text)
            else:
                text_parts.append("[Page content could not be extracted]")

    output_filename = f"第{chapter_num}章_{chapter_name}.txt"
    output_path = os.path.join(output_dir, output_filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(text_parts))

    return output_path


def extract_chapters(chapter_nums: list[int] | None = None):
    """
    Extract specified chapters (or all if none specified).

    Args:
        chapter_nums: List of chapter numbers to extract, or None for all.
    """
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load PDF
    print(f"Loading PDF: {PDF_FILE}")
    try:
        reader = PdfReader(PDF_FILE)
        print(f"Total PDF pages: {len(reader.pages)}")
    except FileNotFoundError:
        print(f"Error: PDF file '{PDF_FILE}' not found.")
        return
    except Exception as e:
        print(f"Error loading PDF: {e}")
        return

    # Determine which chapters to extract
    if chapter_nums is None:
        chapters_to_extract = CHAPTERS
    else:
        chapters_to_extract = [ch for ch in CHAPTERS if ch[0] in chapter_nums]
        if not chapters_to_extract:
            print(f"Error: No matching chapters found for: {chapter_nums}")
            print(f"Available chapters: {[ch[0] for ch in CHAPTERS]}")
            return

    # Extract each chapter
    for chapter_num, chapter_name, toc_start, toc_end in chapters_to_extract:
        print(
            f"Extracting Chapter {chapter_num}: {chapter_name} "
            f"(ToC pages {toc_start}-{toc_end} -> PDF pages "
            f"{toc_page_to_pdf_page(toc_start)}-{toc_page_to_pdf_page(toc_end)})"
        )

        try:
            output_path = extract_chapter(
                reader, chapter_num, chapter_name, toc_start, toc_end, OUTPUT_DIR
            )
            print(f"  -> Saved to: {output_path}")
        except Exception as e:
            print(f"  -> Error extracting chapter {chapter_num}: {e}")

    print("\nExtraction complete!")


# =============================================================================
# Main Entry Point
# =============================================================================
if __name__ == "__main__":
    # Parse command-line arguments
    if len(sys.argv) > 1:
        try:
            chapter_nums = [int(arg) for arg in sys.argv[1:]]
            extract_chapters(chapter_nums)
        except ValueError:
            print("Usage: python extract_text.py [chapter_numbers...]")
            print("Examples:")
            print("  python extract_text.py          # Extract all chapters")
            print("  python extract_text.py 5        # Extract chapter 5")
            print("  python extract_text.py 1 3 5    # Extract chapters 1, 3, 5")
    else:
        extract_chapters()
