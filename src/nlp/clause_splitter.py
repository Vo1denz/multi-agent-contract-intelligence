from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class ClauseSegment:
    text: str
    section_number: Optional[str]
    heading: Optional[str]
    start_char: int
    end_char: int

def split_into_clauses(text: str) -> List[ClauseSegment]:
    pattern = r'(?m)^(?:(?:ARTICLE|SECTION)\s+[IVX\d]+|\d+(?:\.\d+)*\.?|\([a-zivx]+\))\s*(?:[A-Z][A-Za-z\s]+[\.\:])?'
    
    matches = list(re.finditer(pattern, text, flags=re.IGNORECASE))
    
    segments = []
    
    if not matches:
        return [ClauseSegment(text=text, section_number=None, heading=None, start_char=0, end_char=len(text))]
        
    for i, match in enumerate(matches):
        start_char = match.start()
        end_char = matches[i+1].start() if i + 1 < len(matches) else len(text)
        
        clause_text = text[start_char:end_char].strip()
        
        header_text = match.group(0).strip()
        parts = header_text.split(' ', 1)
        section_number = parts[0] if parts else None
        heading = parts[1] if len(parts) > 1 else None
        
        if len(clause_text) < 50 and segments:
            segments[-1].text += "\n" + clause_text
            segments[-1].end_char = end_char
        else:
            segments.append(ClauseSegment(
                text=clause_text,
                section_number=section_number,
                heading=heading,
                start_char=start_char,
                end_char=end_char
            ))
            
    return segments
