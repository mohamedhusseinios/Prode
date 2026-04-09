"""Export research results to a Markdown file."""

import os
import re
from datetime import datetime
from typing import Dict

from stages import STAGES


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text[:50].strip("-")


def export_results(idea: str, results: Dict[str, str], output_dir: str = ".") -> str:
    """
    Write all stage results to a single markdown file.

    Returns the full path of the saved file.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = slugify(idea)
    filename = f"research_{slug}_{timestamp}.md"
    filepath = os.path.join(output_dir, filename)

    lines: list[str] = [
        f"# AI Product Research: {idea}",
        f"",
        f"*Generated on {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}*",
        f"",
        "---",
        "",
    ]

    for stage in STAGES:
        content = results.get(stage.id, "").strip()
        lines.append(f"## {stage.name}")
        lines.append("")
        lines.append(content if content else "*Stage not completed.*")
        lines.append("")
        lines.append("---")
        lines.append("")

    with open(filepath, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))

    return filepath


def export_all_stages(idea: str, results: Dict[str, str], output_dir: str = ".") -> list[str]:
    """
    Write each completed stage to its own markdown file.

    Returns a list of file paths that were written.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = slugify(idea)
    written_paths = []

    for stage in STAGES:
        content = results.get(stage.id, "").strip()

        # Skip stages with empty/missing content
        if not content:
            continue

        filename = f"research_{slug}_{stage.id}_{timestamp}.md"
        filepath = os.path.join(output_dir, filename)

        lines: list[str] = [
            f"# {stage.name}: {idea}",
            "",
            f"*Generated on {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}*",
            "",
            "---",
            "",
            content,
        ]

        with open(filepath, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))

        written_paths.append(filepath)

    return written_paths
