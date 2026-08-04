from __future__ import annotations
import os
import tempfile
from dataclasses import dataclass
from typing import Optional, List

try:
    from PIL import Image
    _HAS_PIL = True
except ImportError:
    _HAS_PIL = False
    Image = None

try:
    from pdf2image import convert_from_path
    _HAS_PDF2IMAGE = True
except ImportError:
    _HAS_PDF2IMAGE = False

try:
    import pypdf
    _HAS_PYPDF = True
except ImportError:
    _HAS_PYPDF = False

_MODE = os.getenv('CLAUSEIQ_MODE', 'lite')

@dataclass
class PageData:
    page_number: int
    file_path: str
    image: Optional[Image.Image] = None
    text: Optional[str] = None

@dataclass
class DocumentPages:
    pages: List[PageData]

def preprocess_document(file_path: str) -> DocumentPages:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    pages = []
    
    if ext == '.pdf':
        if _HAS_PDF2IMAGE and _HAS_PIL:
            try:
                images = convert_from_path(file_path)
                for i, img in enumerate(images):
                    temp_dir = tempfile.mkdtemp()
                    img_path = os.path.join(temp_dir, f"page_{i+1}.png")
                    img.save(img_path)
                    
                    text = None
                    if _HAS_PYPDF:
                        try:
                            reader = pypdf.PdfReader(file_path)
                            if i < len(reader.pages):
                                text = reader.pages[i].extract_text()
                        except Exception:
                            pass
                            
                    pages.append(PageData(
                        page_number=i+1,
                        file_path=img_path,
                        image=img,
                        text=text
                    ))
            except Exception as e:
                # fallback to pypdf text only
                if _HAS_PYPDF:
                    reader = pypdf.PdfReader(file_path)
                    for i, page in enumerate(reader.pages):
                        pages.append(PageData(
                            page_number=i+1,
                            file_path="",
                            text=page.extract_text()
                        ))
        elif _HAS_PYPDF:
            reader = pypdf.PdfReader(file_path)
            for i, page in enumerate(reader.pages):
                pages.append(PageData(
                    page_number=i+1,
                    file_path="",
                    text=page.extract_text()
                ))
    elif ext in ['.png', '.jpg', '.jpeg']:
        if _HAS_PIL:
            img = Image.open(file_path)
            pages.append(PageData(
                page_number=1,
                file_path=file_path,
                image=img,
                text=None
            ))
            
    return DocumentPages(pages=pages)
