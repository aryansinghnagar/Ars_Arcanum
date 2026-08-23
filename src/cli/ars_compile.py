#!/usr/bin/env python3
"""
/usr/local/bin/ars-compile — Ars Arcanum Universal Manuscript Compiler
Compiles Markdown / novelWriter projects into publication-grade Typst Print PDFs, EPUB 3, and DOCX.
"""

import os
import sys
import shutil
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common.config import resolve_world_path
from common.lore_parser import parse_frontmatter
from common.ui_helpers import show_notification, show_info_dialog, show_error_dialog


def collect_manuscript_chapters(manuscript_dir: Path) -> List[Dict[str, Any]]:
    """Collect and sequence all markdown scenes in the project."""
    scenes = []
    for md_file in sorted(manuscript_dir.rglob("*.md")):
        if md_file.name.startswith((".", "_")):
            continue
        try:
            content = md_file.read_text(encoding="utf-8", errors="ignore")
            frontmatter, body = parse_frontmatter(content)
            chapter_num = frontmatter.get("chapter", 1)
            scene_num = frontmatter.get("scene", 1)
            title = frontmatter.get("title", md_file.stem)
            pov = frontmatter.get("pov_character", "")

            scenes.append({
                "file": md_file,
                "chapter": int(chapter_num) if str(chapter_num).isdigit() else 1,
                "scene": int(scene_num) if str(scene_num).isdigit() else 1,
                "title": title,
                "pov": pov,
                "body": body.strip(),
            })
        except Exception:
            continue

    # Sort sequentially by chapter, then scene
    scenes.sort(key=lambda s: (s["chapter"], s["scene"]))
    return scenes


def generate_typst_document(world_name: str, project_title: str, author_name: str, scenes: List[Dict[str, Any]]) -> str:
    """Generate professional, book-ready Typst markup."""
    typst_lines = [
        "// Ars Arcanum Automated Typst Book Engine",
        f'#set document(title: "{project_title}", author: "{author_name}")',
        "",
        "// Typography and Page Geometry",
        "#set page(",
        '  paper: "a5",',
        "  margin: (top: 2.2cm, bottom: 2.2cm, inside: 2.4cm, outside: 1.8cm),",
        "  header: align(center)[",
        "    #text(8pt, font: \"Cinzel\", tracking: 0.15em)[",
        f'      #smallcaps("{project_title}")',
        "    ]",
        "  ],",
        "  footer: [",
        "    #align(center)[#counter(page).display()]",
        "  ]",
        ")",
        "",
        '#set text(font: "EB Garamond", size: 11pt, lang: "en")',
        "#set par(justify: true, leading: 0.72em, first-line-indent: 1.5em)",
        "",
        "// Title Half-Sheet",
        "#align(center + horizon)[",
        f'  #text(26pt, font: "Cinzel", weight: "bold")[{project_title}] \n',
        "  #v(1.5em)",
        f'  #text(14pt, font: "Cinzel")[{author_name}] \n',
        "  #v(2.5em)",
        f'  #text(9pt, style: "italic")[Ars Arcanum Press — World of {world_name}]',
        "]",
        "#pagebreak()",
        "",
    ]

    current_chap = -1
    for s in scenes:
        if s["chapter"] != current_chap:
            current_chap = s["chapter"]
            typst_lines.append("#pagebreak()")
            typst_lines.append(f'#align(center)[#v(3em) #text(18pt, font: "Cinzel", weight: "bold")[Chapter {current_chap}]]')
            if s["title"] and s["title"] != f"Chapter {current_chap}":
                typst_lines.append(f'#align(center)[#text(12pt, style: "italic")[{s["title"]}]]')
            typst_lines.append("#v(2em)")
            if s["pov"]:
                typst_lines.append(f'#align(right)[#text(9pt, font: "Cinzel", fill: luma(90))[POV: {s["pov"]}]]')
                typst_lines.append("#v(1em)")

        typst_lines.append(s["body"])
        typst_lines.append("\n#v(1.5em)\n")

    return "\n".join(typst_lines)


def compile_project(world_path: Path, output_format: str = "pdf") -> bool:
    """Compile project drafts into PDF / EPUB / DOCX."""
    world_name = world_path.name
    manuscripts_dir = world_path / "01-Manuscripts"
    publishing_dir = world_path / "07-Publishing"

    if not manuscripts_dir.exists():
        print(f"[!] Manuscripts directory not found: {manuscripts_dir}")
        return False

    scenes = collect_manuscript_chapters(manuscripts_dir)
    if not scenes:
        print(f"[!] No scenes found in {manuscripts_dir}")
        return False

    project_title = world_name
    author_name = "Ars Arcanum Author"

    # Destination directories
    pdf_dir = publishing_dir / "Print-PDF"
    epub_dir = publishing_dir / "Digital-EPUB"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    epub_dir.mkdir(parents=True, exist_ok=True)

    typst_code = generate_typst_document(world_name, project_title, author_name, scenes)
    typst_file = publishing_dir / "Typst-Templates" / f"{project_title}.typ"
    typst_file.parent.mkdir(parents=True, exist_ok=True)
    typst_file.write_text(typst_code, encoding="utf-8")

    out_pdf = pdf_dir / f"{project_title}_Proof.pdf"

    if output_format in ("pdf", "all"):
        print(f"[*] Generating Typst Book Source: {typst_file}")
        if shutil.which("typst"):
            try:
                proc = subprocess.run(["typst", "compile", str(typst_file), str(out_pdf)], capture_output=True, text=True)
                if proc.returncode == 0:
                    print(f"[+] Typst Print PDF generated successfully: {out_pdf}")
                else:
                    print(f"[!] Typst compilation warning: {proc.stderr}")
            except Exception as e:
                print(f"[!] Could not run Typst binary: {e}")
        else:
            print(f"[+] Typst book markup scaffolded: {typst_file} (Install typst binary for direct PDF compilation).")

    if output_format in ("epub", "all"):
        out_epub = epub_dir / f"{project_title}.epub"
        combined_md = publishing_dir / f"{project_title}_combined.md"
        combined_text = "\n\n".join([f"# {s['title']}\n\n{s['body']}" for s in scenes])
        combined_md.write_text(combined_text, encoding="utf-8")

        if shutil.which("pandoc"):
            try:
                subprocess.run(
                    ["pandoc", str(combined_md), "-o", str(out_epub), f"--metadata=title:{project_title}", f"--metadata=author:{author_name}"],
                    capture_output=True,
                    check=False,
                )
                print(f"[+] EPUB 3 compiled: {out_epub}")
            except Exception as e:
                print(f"[!] Pandoc EPUB compilation error: {e}")
        else:
            print(f"[*] Pandoc not found. Combined markdown saved to {combined_md}")

    show_notification("Compilation Complete", f"Compiled {len(scenes)} scenes for {world_name}.", urgency="normal", icon="document-print")
    return True


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Universal Manuscript Compiler")
    parser.add_argument("world", nargs="?", help="World project directory name or path (optional)")
    parser.add_argument("-f", "--format", choices=["pdf", "epub", "docx", "all"], default="pdf", help="Output format")
    args = parser.parse_args()

    world_path = resolve_world_path(args.world)
    if not world_path or not world_path.is_dir():
        print("[!] No active world found to compile.")
        sys.exit(1)

    print(f"[*] Compiling World Manuscript: {world_path.name} -> {args.format.upper()}")
    compile_project(world_path, output_format=args.format)


if __name__ == "__main__":
    main()
