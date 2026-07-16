from __future__ import annotations

import json
import sys
from pathlib import Path


path = Path(sys.argv[1])
notebook = json.loads(path.read_text(encoding="utf-8"))
mode = sys.argv[2] if len(sys.argv) > 2 else "outline"

if mode == "outline":
    for index, cell in enumerate(notebook["cells"]):
        source = "".join(cell.get("source", []))
        first = source.splitlines()[0] if source.splitlines() else ""
        print(f"{index:02d} {cell['cell_type']}: {first[:180]}")
elif mode == "markdown":
    start = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    end = int(sys.argv[4]) if len(sys.argv) > 4 else len(notebook["cells"])
    for index, cell in enumerate(notebook["cells"][start:end], start=start):
        if cell["cell_type"] == "markdown":
            print(f"\n===== MARKDOWN CELL {index} =====\n")
            print("".join(cell.get("source", [])))
elif mode == "code":
    start = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    end = int(sys.argv[4]) if len(sys.argv) > 4 else len(notebook["cells"])
    for index, cell in enumerate(notebook["cells"][start:end], start=start):
        if cell["cell_type"] == "code":
            print(f"\n===== CODE CELL {index} / EXEC {cell.get('execution_count')} =====\n")
            print("".join(cell.get("source", [])))
            for output_index, output in enumerate(cell.get("outputs", [])):
                print(f"\n--- OUTPUT {output_index} ({output.get('output_type')}) ---")
                if "text" in output:
                    print("".join(output["text"]))
                elif "data" in output:
                    data = output["data"]
                    if "text/plain" in data:
                        print("".join(data["text/plain"]))
                    else:
                        print("[non-text output]")
                elif "ename" in output:
                    print(f"{output['ename']}: {output.get('evalue', '')}")
else:
    raise SystemExit(f"Unknown mode: {mode}")
