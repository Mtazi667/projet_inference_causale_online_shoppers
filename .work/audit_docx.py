from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

from lxml import etree


path = Path(sys.argv[1])
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
CP = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
DC = "http://purl.org/dc/elements/1.1/"

with ZipFile(path) as archive:
    names = archive.namelist()
    xml_parts = {
        name: etree.fromstring(archive.read(name))
        for name in names
        if name.endswith(".xml")
    }

document = xml_parts["word/document.xml"]
texts = document.xpath(".//w:t/text() | .//m:t/text()", namespaces={
    "w": W,
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
})
visible_text = " ".join(texts)
words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+(?:['’][A-Za-zÀ-ÖØ-öø-ÿ0-9]+)*", visible_text)

fonts = Counter()
theme_refs = Counter()
for name, root in xml_parts.items():
    if not name.startswith("word/"):
        continue
    for node in root.xpath(".//w:rFonts", namespaces={"w": W}):
        for attr in ("ascii", "hAnsi", "eastAsia", "cs"):
            value = node.get(f"{{{W}}}{attr}")
            if value:
                fonts[value] += 1
        for attr in ("asciiTheme", "hAnsiTheme", "eastAsiaTheme", "cstheme"):
            value = node.get(f"{{{W}}}{attr}")
            if value:
                theme_refs[f"{attr}={value}"] += 1

theme = xml_parts.get("word/theme/theme1.xml")
theme_latin = []
if theme is not None:
    theme_latin = theme.xpath(
        ".//a:fontScheme/a:majorFont/a:latin/@typeface | .//a:fontScheme/a:minorFont/a:latin/@typeface",
        namespaces={"a": A},
    )

core = xml_parts.get("docProps/core.xml")
creator = core.xpath("string(.//dc:creator)", namespaces={"dc": DC}) if core is not None else ""
last_modified = core.xpath("string(.//cp:lastModifiedBy)", namespaces={"cp": CP}) if core is not None else ""

forbidden_patterns = [
    r"\bOpenAI\b",
    r"\bChatGPT\b",
    r"python-docx",
    r"intelligence artificielle",
    r"\bTODO\b",
    r"\bTBD\b",
    r"Lorem ipsum",
    r"table des matières sera mise à jour",
]
forbidden = [pattern for pattern in forbidden_patterns if re.search(pattern, visible_text, re.I)]

report = {
    "file": str(path.resolve()),
    "paragraphs": len(document.xpath(".//w:body/w:p", namespaces={"w": W})),
    "tables": len(document.xpath(".//w:tbl", namespaces={"w": W})),
    "images": len(document.xpath(".//w:drawing", namespaces={"w": W})),
    "word_count_visible": len(words),
    "headings": {
        "h1": len(document.xpath(".//w:p[w:pPr/w:pStyle[@w:val='Heading1']]", namespaces={"w": W})),
        "h2": len(document.xpath(".//w:p[w:pPr/w:pStyle[@w:val='Heading2']]", namespaces={"w": W})),
        "h3": len(document.xpath(".//w:p[w:pPr/w:pStyle[@w:val='Heading3']]", namespaces={"w": W})),
    },
    "numbered_paragraphs": len(document.xpath(".//w:p[w:pPr/w:numPr]", namespaces={"w": W})),
    "table_captions": visible_text.count("Tableau "),
    "figure_captions": visible_text.count("Figure "),
    "tracked_insertions": len(document.xpath(".//w:ins", namespaces={"w": W})),
    "tracked_deletions": len(document.xpath(".//w:del", namespaces={"w": W})),
    "comments_part": "word/comments.xml" in names,
    "theme_font_refs": dict(theme_refs),
    "explicit_fonts": dict(fonts),
    "theme_latin": theme_latin,
    "creator": creator,
    "last_modified_by": last_modified,
    "forbidden_text_patterns": forbidden,
}
print(json.dumps(report, ensure_ascii=False, indent=2))
