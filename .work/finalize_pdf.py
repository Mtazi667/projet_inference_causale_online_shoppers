from __future__ import annotations

import argparse
from pathlib import Path

from pypdf import PdfReader, PdfWriter


def finalize_pdf(source: Path, destination: Path) -> None:
    reader = PdfReader(source)
    if len(reader.pages) != 20:
        raise SystemExit(f"Expected 20 pages, found {len(reader.pages)}")

    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    writer.metadata = {
        "/Title": "Inférence causale sur les transactions en ligne",
        "/Author": "Mohamed Tazi",
        "/Subject": "Effet du weekend sur la probabilité de transaction",
        "/Keywords": "inférence causale, AIPW, IPW, FCI, Online Shoppers",
    }
    writer.root_object.pop("/Metadata", None)

    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as handle:
        writer.write(handle)

    check = PdfReader(destination)
    if len(check.pages) != 20:
        raise SystemExit("The finalized PDF has an unexpected page count")
    text = "\n".join(page.extract_text() or "" for page in check.pages)
    required = (
        "Inférence causale sur les transactions en ligne",
        "Résumé",
        "Références",
        "Annexe A. Arêtes du PAG FCI",
    )
    missing = [item for item in required if item not in text]
    if missing:
        raise SystemExit(f"Missing required PDF text: {missing}")
    forbidden = ("Mettre à jour la table", "Error! Reference source not found", "ChatGPT")
    present = [item for item in forbidden if item.casefold() in text.casefold()]
    if present:
        raise SystemExit(f"Forbidden PDF text found: {present}")

    print(f"pages={len(check.pages)}")
    print(f"metadata={dict(check.metadata or {})}")
    print(f"bytes={destination.stat().st_size}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    finalize_pdf(args.source.resolve(), args.destination.resolve())


if __name__ == "__main__":
    main()
