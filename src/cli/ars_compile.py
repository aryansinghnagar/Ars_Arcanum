#!/usr/bin/env python3
"""
/usr/local/bin/ars-compile — Ars Arcanum Universal Manuscript Compiler
Compiles Markdown / novelWriter projects into publication-grade Typst Print PDFs, EPUB 3, and DOCX.
"""

import sys
import shutil
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common.config import resolve_world_path
from common.lore_parser import parse_frontmatter
from common.ui_helpers import show_notification


def _typst_escape(s: str) -> str:
    """Escape double quotes and backslashes for Typst string literals."""
    return str(s).replace("\\", "\\\\").replace('"', '\\"')


def _typst_content_escape(s: str) -> str:
    """Escape Typst markup-significant chars in running content (headings, POV lines).

    NOTE: scene *bodies* are intentionally NOT passed through this function.
    Bodies are author-controlled Markdown injected verbatim into the Typst source
    so intentional Typst markup is preserved; authors must therefore write
    Typst-compatible scene text (plain prose is compatible as-is).
    """
    out = str(s).replace("\\", "\\\\")
    for ch in ("[", "]", "#", "*", "_", "`", "$"):
        out = out.replace(ch, "\\" + ch)
    return out


def collect_manuscript_chapters(manuscript_dir: Path) -> List[Dict[str, Any]]:
    """Collect and sequence all markdown scenes in the project."""
    scenes = []
    for md_file in sorted(manuscript_dir.rglob("*.md")):
        if md_file.name.startswith((".", "_")):
            continue
        try:
            content = md_file.read_text(encoding="utf-8", errors="ignore")
        except OSError as e:
            print(f"[!] Skipping unreadable file {md_file}: {e}")
            continue
        try:
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
        except (ValueError, TypeError) as e:
            print(f"[!] Skipping malformed scene {md_file}: {e}")
            continue

    # Sort sequentially by chapter, then scene
    scenes.sort(key=lambda s: (s["chapter"], s["scene"]))
    return scenes


def generate_typst_document(world_name: str, project_title: str, author_name: str, scenes: List[Dict[str, Any]]) -> str:
    """Generate professional, book-ready Typst markup.

    String-literal positions (document title/author, smallcaps header) use
    string escaping; content positions (title page, chapter headings, POV lines)
    use content-markup escaping. Scene bodies are injected verbatim — see
    _typst_content_escape for the contract.
    """
    s_title = _typst_escape(project_title)
    s_author = _typst_escape(author_name)
    c_title = _typst_content_escape(project_title)
    c_author = _typst_content_escape(author_name)
    c_world = _typst_content_escape(world_name)
    typst_lines = [
        "// Ars Arcanum Automated Typst Book Engine",
        f'#set document(title: "{s_title}", author: "{s_author}")',
        "",
        "// Typography and Page Geometry",
        "#set page(",
        '  paper: "a5",',
        "  margin: (top: 2.2cm, bottom: 2.2cm, inside: 2.4cm, outside: 1.8cm),",
        "  header: align(center)[",
        "    #text(8pt, font: \"Cinzel\", tracking: 0.15em)[",
        f'      #smallcaps("{s_title}")',
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
        f'  #text(26pt, font: "Cinzel", weight: "bold")[{c_title}] \n',
        "  #v(1.5em)",
        f'  #text(14pt, font: "Cinzel")[{c_author}] \n',
        "  #v(2.5em)",
        f'  #text(9pt, style: "italic")[Ars Arcanum Press — World of {c_world}]',
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
            safe_title = _typst_content_escape(s["title"])
            if s["title"] and s["title"] != f"Chapter {current_chap}":
                typst_lines.append(f'#align(center)[#text(12pt, style: "italic")[{safe_title}]]')
            typst_lines.append("#v(2em)")
            if s["pov"]:
                safe_pov = _typst_content_escape(s["pov"])
                typst_lines.append(f'#align(right)[#text(9pt, font: "Cinzel", fill: luma(90))[POV: {safe_pov}]]')
                typst_lines.append("#v(1em)")

        typst_lines.append(s["body"])
        typst_lines.append("\n#v(1.5em)\n")

    return "\n".join(typst_lines)


def _pandoc_convert(combined_md: Path, out_file: Path, project_title: str, author_name: str) -> bool:
    """Convert combined markdown to epub/docx via pandoc. Returns True on success."""
    if not shutil.which("pandoc"):
        print(f"[*] Pandoc not found. Combined markdown saved to {combined_md}")
        return False
    try:
        proc = subprocess.run(
            ["pandoc", str(combined_md), "-o", str(out_file),
             f"--metadata=title={project_title}", f"--metadata=author={author_name}"],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode == 0:
            print(f"[+] {out_file.suffix.lstrip('.').upper()} compiled: {out_file}")
            return True
        print(f"[!] Pandoc {out_file.suffix} compilation warning: {proc.stderr.strip()[:500]}")
        return False
    except OSError as e:
        print(f"[!] Pandoc {out_file.suffix} compilation error: {e}")
        return False


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
    docx_dir = publishing_dir / "Digital-DOCX"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    epub_dir.mkdir(parents=True, exist_ok=True)
    if output_format in ("docx", "all"):
        docx_dir.mkdir(parents=True, exist_ok=True)

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
            except OSError as e:
                print(f"[!] Could not run Typst binary: {e}")
        else:
            print(f"[+] Typst book markup scaffolded: {typst_file} (Install typst binary for direct PDF compilation).")

    if output_format in ("epub", "docx", "all"):
        # pandoc converts the same combined markdown to each requested target
        targets = []
        if output_format in ("epub", "all"):
            targets.append(epub_dir / f"{project_title}.epub")
        if output_format in ("docx", "all"):
            targets.append(docx_dir / f"{project_title}.docx")
        combined_md = publishing_dir / f"{project_title}_combined.md"
        combined_text = "\n\n".join([f"# {s['title']}\n\n{s['body']}" for s in scenes])
        combined_md.write_text(combined_text, encoding="utf-8")

        for out_file in targets:
            _pandoc_convert(combined_md, out_file, project_title, author_name)

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
    ok = compile_project(world_path, output_format=args.format)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
