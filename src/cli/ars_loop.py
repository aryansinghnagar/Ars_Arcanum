#!/usr/bin/env python3
"""
/usr/local/bin/ars-loop — Ars Arcanum Non-Linear Narrative & Loop State Engine
Tracks character knowledge matrices, timeline branches, and loop iteration checkpoints.
"""

import json
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common.config import resolve_world_path


def generate_sample_loop_schema(world_dir: Path) -> Path:
    """Generate sample non-linear loop schema in 05-Timelines."""
    timelines_dir = world_dir / "05-Timelines"
    timelines_dir.mkdir(parents=True, exist_ok=True)
    loop_file = timelines_dir / "loop_matrix.json"

    if not loop_file.exists():
        sample_data = {
            "world": world_dir.name,
            "narrative_structure": "Time Loop / Branching Reality",
            "anchor_checkpoint": "The Festival of the Twin Moons — Eve",
            "loops": [
                {
                    "iteration": 1,
                    "title": "The Ignorant Beginning",
                    "cause_of_reset": "Assassination by the Shadow Cult",
                    "checkpoint_state": {
                        "protagonist_injuries": "None",
                        "inventory": ["Silver Dagger", "30 Gold Drachmas"],
                        "trauma_level": 1
                    },
                    "knowledge_matrix": {
                        "Protagonist": ["Unaware of time loop until demise"],
                        "Allied Knight": ["Loyal to Queen", "Unaware of loop"],
                        "Shadow Assassin": ["Knows target location", "Unaware of loop"]
                    }
                },
                {
                    "iteration": 2,
                    "title": "The First Paranoia",
                    "cause_of_reset": "Poisoned wine at banquet",
                    "checkpoint_state": {
                        "protagonist_injuries": "Phantom chest pain",
                        "inventory": ["Silver Dagger", "Antidote Vial"],
                        "trauma_level": 4
                    },
                    "knowledge_matrix": {
                        "Protagonist": ["Knows assassin attacks at midnight", "Knows festival layout"],
                        "Allied Knight": ["Suspects protagonist has lost sanity"],
                        "Shadow Assassin": ["Changes attack vector to poison"]
                    }
                },
                {
                    "iteration": 3,
                    "title": "The Counter-Ambush",
                    "cause_of_reset": "Loop broken / Narrative convergence",
                    "checkpoint_state": {
                        "protagonist_injuries": "Scar on right shoulder",
                        "inventory": ["Cult Seal", "Royal Pardon Letter"],
                        "trauma_level": 6
                    },
                    "knowledge_matrix": {
                        "Protagonist": ["Knows cult mastermind identity", "Has memorized palace guard schedules"],
                        "Allied Knight": ["Fully convinced after specific prophetic warnings"],
                        "Shadow Assassin": ["Caught and interrogated"]
                    }
                }
            ]
        }
        loop_file.write_text(json.dumps(sample_data, indent=2), encoding="utf-8")
    return loop_file


def inspect_loop_matrix(world_dir: Path) -> None:
    loop_file = generate_sample_loop_schema(world_dir)
    try:
        data = json.loads(loop_file.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[!] Error reading loop matrix {loop_file}: {e}")
        return

    print("\n=======================================================")
    print("       ARS ARCANUM NON-LINEAR LOOP MATRIX             ")
    print(f"       World: {data.get('world', world_dir.name)}     ")
    print("=======================================================")
    print(f"Anchor Checkpoint: {data.get('anchor_checkpoint')}\n")

    for loop in data.get("loops", []):
        try:
            iteration = int(loop.get("iteration", "?"))
        except (TypeError, ValueError):
            iteration = "?"
        title = str(loop.get("title", "Untitled"))[:120]
        print(f"--- LOOP ITERATION #{iteration}: {title} ---")
        print(f"  Reset Cause:     {loop.get('cause_of_reset', 'unknown')}")
        state = loop.get("checkpoint_state", {}) if isinstance(loop.get("checkpoint_state"), dict) else {}
        try:
            trauma = int(state.get("trauma_level", 1))
        except (TypeError, ValueError):
            trauma = 1
        trauma = max(0, min(10, trauma))
        print(f"  Trauma Level:    [{'#' * trauma}{'.' * (10 - trauma)}] ({trauma}/10)")
        inv = state.get("inventory", [])
        inv = inv if isinstance(inv, list) else [inv]
        print(f"  Inventory:       {', '.join(str(x)[:80] for x in inv)}")
        print("  Knowledge States:")
        km = loop.get("knowledge_matrix", {}) if isinstance(loop.get("knowledge_matrix"), dict) else {}
        for char, facts in km.items():
            print(f"    • {str(char)[:80]}:")
            facts = facts if isinstance(facts, list) else [facts]
            for fact in facts:
                print(f"        - {str(fact)[:300]}")
        print()
    print("=======================================================\n")


def export_drawio_timeline(world_dir: Path) -> Path:
    """Export draw.io compatible XML graph representing timeline loops."""
    timelines_dir = world_dir / "05-Timelines"
    timelines_dir.mkdir(parents=True, exist_ok=True)
    out_xml = timelines_dir / "loop_diagram.drawio"

    xml_content = """<mxfile host="ArsArcanum">
  <diagram id="loops" name="Branching Loops">
    <mxGraphModel dx="1000" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="2" value="Anchor Checkpoint (Loop Start)" style="rounded=1;fillColor=#1a1a2e;strokeColor=#c9a96e;fontColor=#f5e6c8;fontStyle=1" vertex="1" parent="1">
          <mxGeometry x="80" y="180" width="200" height="60" as="geometry"/>
        </mxCell>
        <mxCell id="3" value="Loop #1 (Assassination Reset)" style="rounded=1;fillColor=#4a1942;strokeColor=#c9a96e;fontColor=#f5e6c8;" vertex="1" parent="1">
          <mxGeometry x="340" y="100" width="180" height="50" as="geometry"/>
        </mxCell>
        <mxCell id="4" value="Loop #2 (Poison Reset)" style="rounded=1;fillColor=#4a1942;strokeColor=#c9a96e;fontColor=#f5e6c8;" vertex="1" parent="1">
          <mxGeometry x="340" y="190" width="180" height="50" as="geometry"/>
        </mxCell>
        <mxCell id="5" value="Loop #3 (Convergence / Victory)" style="rounded=1;fillColor=#1b2d1b;strokeColor=#d4a017;fontColor=#f0ead6;" vertex="1" parent="1">
          <mxGeometry x="340" y="280" width="180" height="50" as="geometry"/>
        </mxCell>
        <mxCell id="6" edge="1" parent="1" source="2" target="3" style="strokeColor=#c9a96e;"/>
        <mxCell id="7" edge="1" parent="1" source="2" target="4" style="strokeColor=#c9a96e;"/>
        <mxCell id="8" edge="1" parent="1" source="2" target="5" style="strokeColor=#d4a017;"/>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>"""
    out_xml.write_text(xml_content, encoding="utf-8")
    print(f"[+] Exported draw.io timeline graph: {out_xml}")
    return out_xml


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Non-Linear Loop & Knowledge Tracker")
    parser.add_argument("world", nargs="?", help="World project directory name or path (optional)")
    parser.add_argument("--export-drawio", action="store_true", help="Export draw.io XML diagram")
    args = parser.parse_args()

    world_path = resolve_world_path(args.world)
    if not world_path or not world_path.is_dir():
        print(f"[!] No active world found: {args.world or ''}")
        sys.exit(1)

    if args.export_drawio:
        export_drawio_timeline(world_path)
    else:
        inspect_loop_matrix(world_path)


if __name__ == "__main__":
    main()
