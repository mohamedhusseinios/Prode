"""Export research results to a Markdown file."""

import os
import re
from datetime import datetime
from typing import Dict

from stages import STAGES


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = text.replace("..", "")
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
