from __future__ import annotations

import csv
import hashlib
import json
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

from PIL import Image
from pypdf import PdfReader


ROOT_NAME = "projet_inference_causale_online_shoppers"
FILES = (
    "01_notebooks/livrable/projet_final_inference_causale_online_shoppers.ipynb",
    "02_data/raw/online_shoppers_intention.csv",
    "03_notes/fiche_orale_questions_pieges.md",
    "04_outputs/figures/01_description_et_recouvrement.png",
    "04_outputs/figures/02_dag_de_travail.png",
    "04_outputs/figures/03_pag_fci.png",
    "04_outputs/figures/04_recouvrement_propension.png",
    "04_outputs/figures/05_equilibre_covariables.png",
    "04_outputs/figures/06_estimations_principales.png",
    "04_outputs/figures/07_robustesse_aipw.png",
    "04_outputs/notebook_html/projet_final_inference_causale_online_shoppers.html",
    "04_outputs/presentation/presentation_finale_inference_causale_online_shoppers.pptx",
    "04_outputs/rapport/rapport_final_inference_causale_online_shoppers.docx",
    "04_outputs/rapport/rapport_final_inference_causale_online_shoppers.pdf",
    "04_outputs/tableaux/01_aretes_pag_fci.csv",
    "04_outputs/tableaux/02_estimations_principales.csv",
    "04_outputs/tableaux/03_equilibre_covariables.csv",
    "04_outputs/tableaux/04_analyses_robustesse.csv",
    "README.md",
    "requirements.txt",
    "src/_construire_notebook_livrable.py",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_info(arcname: str, *, directory: bool = False) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(arcname, date_time=(2026, 7, 15, 16, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    mode = 0o40755 if directory else 0o100644
    info.external_attr = (mode & 0xFFFF) << 16
    if directory:
        info.external_attr |= 0x10
    return info


def build(source_root: Path, output: Path) -> dict[str, str]:
    missing = [relative for relative in FILES if not (source_root / relative).is_file()]
    if missing:
        raise SystemExit(f"Missing package sources: {missing}")

    output.parent.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, str] = {}
    with zipfile.ZipFile(output, "w", allowZip64=True) as archive:
        archive.writestr(file_info(f"{ROOT_NAME}/", directory=True), b"")
        for relative in FILES:
            data = (source_root / relative).read_bytes()
            manifest[relative] = sha256(data)
            archive.writestr(file_info(f"{ROOT_NAME}/{relative}"), data, compresslevel=9)
    return manifest


def safe_member(name: str) -> bool:
    if "\\" in name or name.startswith(("/", "\\")):
        return False
    path = PurePosixPath(name)
    return not any(part in ("", ".", "..") for part in path.parts)


def audit_office(path: Path) -> None:
    with zipfile.ZipFile(path) as package:
        if package.testzip() is not None:
            raise SystemExit(f"Corrupt Office package: {path}")
        names = set(package.namelist())
        if "[Content_Types].xml" not in names:
            raise SystemExit(f"Invalid Office package: {path}")


def audit_payload(extracted_root: Path) -> None:
    audit_office(extracted_root / "04_outputs/presentation/presentation_finale_inference_causale_online_shoppers.pptx")
    audit_office(extracted_root / "04_outputs/rapport/rapport_final_inference_causale_online_shoppers.docx")

    pdf = PdfReader(extracted_root / "04_outputs/rapport/rapport_final_inference_causale_online_shoppers.pdf")
    if len(pdf.pages) != 20:
        raise SystemExit(f"Expected a 20-page report PDF, found {len(pdf.pages)}")

    notebook_path = extracted_root / "01_notebooks/livrable/projet_final_inference_causale_online_shoppers.ipynb"
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    code_cells = [cell for cell in notebook.get("cells", []) if cell.get("cell_type") == "code"]
    if not code_cells or any(cell.get("execution_count") is None for cell in code_cells):
        raise SystemExit("Notebook is not fully executed")
    if any(output.get("output_type") == "error" for cell in code_cells for output in cell.get("outputs", [])):
        raise SystemExit("Notebook contains an error output")

    for relative in FILES:
        path = extracted_root / relative
        suffix = path.suffix.casefold()
        if suffix == ".csv":
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.reader(handle))
            if len(rows) < 2:
                raise SystemExit(f"CSV has no data rows: {relative}")
        elif suffix == ".png":
            with Image.open(path) as image:
                image.verify()
        elif suffix == ".py":
            compile(path.read_text(encoding="utf-8"), relative, "exec")
        elif suffix in (".md", ".txt", ".html"):
            if not path.read_text(encoding="utf-8").strip():
                raise SystemExit(f"Empty text payload: {relative}")


def audit(source_root: Path, archive_path: Path, manifest: dict[str, str]) -> None:
    expected = [f"{ROOT_NAME}/"] + [f"{ROOT_NAME}/{relative}" for relative in FILES]
    with zipfile.ZipFile(archive_path) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if names != expected:
            raise SystemExit("ZIP entries differ from the explicit ordered whitelist")
        if len(names) != len(set(names)) or len(names) != len({name.casefold() for name in names}):
            raise SystemExit("ZIP contains duplicate or case-colliding names")
        if any(not safe_member(name.rstrip("/")) for name in names):
            raise SystemExit("ZIP contains an unsafe member name")
        if {PurePosixPath(name).parts[0] for name in names} != {ROOT_NAME}:
            raise SystemExit("ZIP does not have exactly one top-level folder")
        if any(info.flag_bits & 0x1 for info in infos):
            raise SystemExit("ZIP unexpectedly contains encrypted entries")
        if archive.testzip() is not None:
            raise SystemExit("ZIP CRC test failed")
        for relative in FILES:
            archived = archive.read(f"{ROOT_NAME}/{relative}")
            if sha256(archived) != manifest[relative]:
                raise SystemExit(f"Archived payload differs from source: {relative}")

        extraction_parent = Path(tempfile.mkdtemp(prefix="zip_extract_audit_", dir=source_root / ".work"))
        archive.extractall(extraction_parent)

    extracted_root = extraction_parent / ROOT_NAME
    extracted_files = sorted(
        path.relative_to(extracted_root).as_posix()
        for path in extracted_root.rglob("*")
        if path.is_file()
    )
    if extracted_files != sorted(FILES):
        raise SystemExit("Extracted payload differs from the whitelist")
    for relative in FILES:
        if sha256((extracted_root / relative).read_bytes()) != manifest[relative]:
            raise SystemExit(f"Extracted payload hash mismatch: {relative}")
    audit_payload(extracted_root)

    forbidden_tokens = ("/.work/", "/.git/", "/.agents/", "__pycache__", ".tmp")
    with zipfile.ZipFile(archive_path) as archive:
        lowered = [f"/{name.casefold()}" for name in archive.namelist()]
    if any(token.casefold() in name for name in lowered for token in forbidden_tokens):
        raise SystemExit("ZIP contains a forbidden build or cache artifact")

    print(f"archive={archive_path.resolve()}")
    print(f"top_level={ROOT_NAME}/")
    print(f"files={len(FILES)}")
    print(f"entries={len(expected)}")
    print(f"bytes={archive_path.stat().st_size}")
    print(f"sha256={sha256(archive_path.read_bytes())}")
    print(f"extraction_audit={extracted_root.resolve()}")


def main() -> None:
    source_root = Path.cwd().resolve()
    output = source_root / ".work/rendu_final_inference_causale_online_shoppers.zip"
    manifest = build(source_root, output)
    audit(source_root, output, manifest)


if __name__ == "__main__":
    main()
