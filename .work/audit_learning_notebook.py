from __future__ import annotations

import argparse
from pathlib import Path

import nbformat


REQUIRED_TEXT = (
    "Carnet d’apprentissage — Inférence causale",
    "Module 0 — Comprendre l’histoire générale du projet",
    "Module 1 — Proportions, points de pourcentage, association et incertitude",
    "12 330",
    "11 079",
    "18,06 %",
    "16,03 %",
    "+1,506",
    "ANCRE_PROCHAIN_MODULE",
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("notebook", type=Path)
    args = parser.parse_args()

    with args.notebook.open("r", encoding="utf-8") as handle:
        notebook = nbformat.read(handle, as_version=4)
    nbformat.validate(notebook)

    ids = [cell.get("id") for cell in notebook.cells]
    if len(ids) != len(set(ids)) or any(not cell_id for cell_id in ids):
        raise SystemExit("Les identifiants de cellule sont absents ou dupliqués")

    code_cells = [cell for cell in notebook.cells if cell.cell_type == "code"]
    errors = [
        output
        for cell in code_cells
        for output in cell.get("outputs", [])
        if output.get("output_type") == "error"
    ]
    if errors:
        raise SystemExit(f"Le notebook contient {len(errors)} sortie(s) d'erreur")
    if any(cell.get("execution_count") is None for cell in code_cells):
        raise SystemExit("Toutes les cellules de code ne sont pas exécutées")

    full_source = "\n".join(cell.source for cell in notebook.cells)
    missing = [text for text in REQUIRED_TEXT if text not in full_source]
    if missing:
        raise SystemExit(f"Éléments pédagogiques manquants : {missing}")

    forbidden_writes = ("to_csv(", "to_excel(", "nbformat.write(", "open(\"w")
    code_source = "\n".join(cell.source for cell in code_cells)
    detected = [token for token in forbidden_writes if token in code_source]
    if detected:
        raise SystemExit(f"Écriture interdite détectée dans le notebook : {detected}")

    tags = [tag for cell in notebook.cells for tag in cell.metadata.get("tags", [])]
    response_cells = sum("reponse-apprenant" in cell.metadata.get("tags", []) for cell in notebook.cells)
    oral_cells = sum("oral" in cell.metadata.get("tags", []) for cell in notebook.cells)
    exercise_cells = sum("exercice" in cell.metadata.get("tags", []) for cell in notebook.cells)
    if response_cells < 5 or oral_cells < 3 or exercise_cells < 5:
        raise SystemExit("Le carnet ne contient pas assez d'activités ou de zones de réponse")

    output_text = "\n".join(
        str(output.get("text", ""))
        for cell in code_cells
        for output in cell.get("outputs", [])
        if output.get("output_type") == "stream"
    )
    for expected in ("12 330 sessions", "Différence absolue : 2.026", "14 % en semaine contre 22 %"):
        if expected not in output_text:
            raise SystemExit(f"Sortie de calcul attendue absente : {expected}")

    print(f"notebook={args.notebook.resolve()}")
    print(f"cellules={len(notebook.cells)}")
    print(f"code={len(code_cells)}")
    print(f"erreurs={len(errors)}")
    print(f"exercices={exercise_cells}")
    print(f"reponses={response_cells}")
    print(f"oral={oral_cells}")
    print(f"tags_uniques={sorted(set(tags))}")


if __name__ == "__main__":
    main()
