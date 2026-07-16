from __future__ import annotations

import argparse
import os
import re
import tempfile
import zipfile
from pathlib import Path


def normalize(path: Path) -> None:
    with zipfile.ZipFile(path, "r") as source:
        if source.testzip() is not None:
            raise SystemExit("Input DOCX failed its CRC check")
        infos = source.infolist()
        payloads = {info.filename: source.read(info.filename) for info in infos}

    core_name = "docProps/core.xml"
    core = payloads[core_name]
    core, count = re.subn(
        rb"<cp:revision>[^<]*</cp:revision>",
        b"<cp:revision>1</cp:revision>",
        core,
        count=1,
    )
    if count != 1:
        raise SystemExit("Could not normalize the DOCX revision field")
    payloads[core_name] = core

    handle, temp_name = tempfile.mkstemp(suffix=".docx", dir=path.parent)
    os.close(handle)
    temp_path = Path(temp_name)
    try:
        with zipfile.ZipFile(temp_path, "w", allowZip64=True) as destination:
            for info in infos:
                destination.writestr(info, payloads[info.filename])
        with zipfile.ZipFile(temp_path, "r") as check:
            if check.testzip() is not None:
                raise SystemExit("Normalized DOCX failed its CRC check")
            normalized_core = check.read(core_name)
            if b"<cp:revision>1</cp:revision>" not in normalized_core:
                raise SystemExit("DOCX revision field was not normalized")
        os.replace(temp_path, path)
    finally:
        temp_path.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("docx", type=Path)
    args = parser.parse_args()
    normalize(args.docx.resolve())


if __name__ == "__main__":
    main()
