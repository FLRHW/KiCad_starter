"""Update internal project names and install workflows after template creation.

Run: python3 scripts/setup_project.py
Use --force to replace an existing workflow that has different contents.
"""
import argparse
import json
from pathlib import Path
import shutil


def prepare_project_names(root, parser):
    projects = sorted(root.glob("*.kicad_pro"))
    if len(projects) != 1:
        parser.error("Expected exactly one .kicad_pro file in the project root")
    project = projects[0]
    data = json.loads(project.read_text(encoding="utf-8"))
    old_filename = data.get("meta", {}).get("filename", project.name)
    old_name = Path(old_filename).stem
    new_name = project.stem
    updates = []
    if old_name != new_name:
        old_record = '(project "' + old_name + '"'
        new_record = '(project "' + new_name + '"'
        for sheet in sorted(root.rglob("*.kicad_sch")):
            if any(part.startswith(".") or part == "output" for part in sheet.relative_to(root).parts):
                continue
            content = sheet.read_text(encoding="utf-8")
            if old_record not in content:
                continue
            if new_record in content:
                parser.error(f"Both old and new instance records exist in {sheet.name}; review them before renaming")
            updates.append((sheet, content.replace(old_record, new_record)))

    def rename_metadata(value):
        if isinstance(value, dict):
            return {key: rename_metadata(item) for key, item in value.items()}
        if isinstance(value, list):
            return [rename_metadata(item) for item in value]
        if isinstance(value, str) and old_name != new_name:
            if value in (old_name + ".kicad_pro", old_name + ".kicad_sch", old_name + ".kicad_pcb"):
                return new_name + value[len(old_name):]
        return value

    data = rename_metadata(data)
    data.setdefault("meta", {})["filename"] = project.name
    return project, data, updates, old_name, new_name


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    source = root / "ci" / "workflows"
    workflows = sorted(source.glob("*.yml")) + sorted(source.glob("*.yaml"))
    if not workflows:
        parser.error(f"No workflow files found in {source}")
    destination = root / ".github" / "workflows"
    # Check every conflict before copying any files.
    for workflow in workflows:
        target = destination / workflow.name
        if target.exists() and target.read_bytes() != workflow.read_bytes() and not args.force:
            parser.error(f"Existing workflow differs: {target}. Use --force to replace it.")
    project, data, updates, old_name, new_name = prepare_project_names(root, parser)
    for sheet, content in updates:
        sheet.write_text(content, encoding="utf-8")
    original = json.loads(project.read_text(encoding="utf-8"))
    if data != original:
        project.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    if old_name != new_name:
        print(f"Updated internal project name: {old_name} -> {new_name}; {len(updates)} schematic files")
    destination.mkdir(parents=True, exist_ok=True)
    for workflow in workflows:
        target = destination / workflow.name
        if target.exists() and target.read_bytes() == workflow.read_bytes():
            print(f"Already current: .github/workflows/{workflow.name}")
        else:
            shutil.copy2(workflow, target)
            print(f"Installed: .github/workflows/{workflow.name}")


if __name__ == "__main__":
    main()
