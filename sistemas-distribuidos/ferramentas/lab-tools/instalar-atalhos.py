#!/usr/bin/env python3
"""Copia atalhos lab.ps1/lab.sh/lab.cmd para cada pasta com docker-compose.yml
e insere o aviso Linux/Windows nos README e tutoriais."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "ferramentas" / "lab-tools"
GUIDE = "ferramentas/linux-e-windows.md"

PS1 = (TOOLS / "trampoline.ps1").read_text(encoding="utf-8")
SH = (TOOLS / "trampoline.sh").read_text(encoding="utf-8")
CMD = (TOOLS / "trampoline.cmd").read_text(encoding="utf-8")


def rel_guide(from_dir: Path) -> str:
    depth = len(from_dir.relative_to(ROOT).parts)
    return "../" * depth + GUIDE


def note_block(from_dir: Path) -> str:
    rel = rel_guide(from_dir)
    return (
        f"> **Linux e Windows:** `docker compose` é o mesmo nos dois. "
        f"No PowerShell, `./scripts/foo.sh` vira `.\\lab.ps1 foo` (nesta pasta) "
        f"e `curl` vira `curl.exe`. Guia: [{GUIDE.split('/')[-1]}]({rel}).\n"
    )


def so_line(from_file: Path) -> str:
    rel = rel_guide(from_file.parent)
    return (
        f"**SO:** Linux, macOS e Windows — "
        f"[como rodar os comandos]({rel}).  \n"
    )


def write_trampolines() -> int:
    n = 0
    for compose in ROOT.rglob("docker-compose.yml"):
        lab = compose.parent
        (lab / "lab.ps1").write_text(PS1, encoding="utf-8", newline="\n")
        (lab / "lab.sh").write_text(SH, encoding="utf-8", newline="\n")
        (lab / "lab.cmd").write_text(CMD, encoding="utf-8", newline="\r\n")
        n += 1
    return n


def patch_lab_readme(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if "lab.ps1" in text or "linux-e-windows.md" in text or "**Linux e Windows:**" in text:
        return False
    note = note_block(path.parent)
    marker = "## Subir e testar"
    if marker in text:
        text = text.replace(marker, note + "\n" + marker, 1)
    else:
        # depois do primeiro bloco de título
        lines = text.splitlines(keepends=True)
        insert_at = 0
        for i, line in enumerate(lines):
            if line.startswith("# "):
                insert_at = i + 1
                break
        lines.insert(insert_at, "\n" + note)
        text = "".join(lines)
    path.write_text(text, encoding="utf-8", newline="\n")
    return True


def patch_tutorial(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if "linux-e-windows.md" in text:
        return False
    line = so_line(path)
    lines = text.splitlines(keepends=True)
    for i, raw in enumerate(lines):
        if raw.startswith("**Apoio:**"):
            lines.insert(i + 1, line)
            path.write_text("".join(lines), encoding="utf-8", newline="\n")
            return True
    return False


def main() -> None:
    n = write_trampolines()
    readmes = labs = tuts = 0
    for compose in ROOT.rglob("docker-compose.yml"):
        readme = compose.parent / "README.md"
        if readme.exists() and patch_lab_readme(readme):
            labs += 1
    for md in ROOT.rglob("tutorial*.md"):
        if patch_tutorial(md):
            tuts += 1
    print(f"atalhos em {n} labs; README labs +{labs}; tutoriais +{tuts}")


if __name__ == "__main__":
    main()
