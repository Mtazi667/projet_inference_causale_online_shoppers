from __future__ import annotations

import hashlib
import sys
from pathlib import Path

from pypdf import PdfReader


def stream_digest(page) -> str:
    contents = page.get_contents()
    data = b"" if contents is None else contents.get_data()
    return hashlib.sha256(data).hexdigest()


def fonts(reader: PdfReader) -> list[str]:
    found: set[str] = set()
    for page in reader.pages:
        resources = page.get("/Resources")
        if resources is None:
            continue
        font_dict = resources.get_object().get("/Font")
        if font_dict is None:
            continue
        for font_ref in font_dict.get_object().values():
            font = font_ref.get_object()
            name = font.get("/BaseFont")
            if name:
                found.add(str(name))
    return sorted(found)


def main() -> None:
    source = PdfReader(Path(sys.argv[1]))
    final = PdfReader(Path(sys.argv[2]))
    if len(source.pages) != 20 or len(final.pages) != 20:
        raise SystemExit("Expected 20 pages in both PDFs")
    mismatches = []
    for index, (before, after) in enumerate(zip(source.pages, final.pages), start=1):
        if stream_digest(before) != stream_digest(after):
            mismatches.append(index)
        if before.mediabox != after.mediabox:
            mismatches.append(index)
    if mismatches:
        raise SystemExit(f"Page content or geometry changed: {sorted(set(mismatches))}")
    print("page_content_identical=true")
    print(f"pages={len(final.pages)}")
    print(f"fonts={fonts(final)}")
    print(f"metadata={dict(final.metadata or {})}")


if __name__ == "__main__":
    main()
