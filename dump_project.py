#!/usr/bin/env python3
"""
dump_project.py

Packs an entire project into a single Markdown file so it can be pasted
into any AI chat (Claude, ChatGPT, Gemini, ...) and the AI immediately
understands the full structure and code.

Usage (run from inside your project root, e.g. C:\\Users\\Raven\\OSM):

    python dump_project.py

Output:
    project_context.md   (in the same folder you run it from)

What it does:
    - Walks the project directory.
    - Skips noisy / irrelevant folders: venv, __pycache__, .git, node_modules,
      dist, build, third-party vendored source trees (osm2pgsql, martin binaries),
      .bfg-report, *.egg-info, .pytest_cache, .mypy_cache, .idea, .vscode.
    - Skips binary / huge / irrelevant files (fonts, images, compiled libs,
      lockfiles you don't usually need to show, etc.).
    - Skips anything that looks like a secret (.env, *.pem, *.key) and just
      notes that it was skipped, so you don't leak credentials by accident.
    - Writes a folder tree + the full content of every remaining text file,
      each fenced with its relative path and a language tag for syntax
      highlighting.

Tweak the EXCLUDE_DIRS / EXCLUDE_FILE_PATTERNS / SECRET_PATTERNS lists below
to fit your project.
"""

import os
import sys
import fnmatch

# ---------------------------------------------------------------------------
# CONFIGURATION — edit this section for your project
# ---------------------------------------------------------------------------

ROOT = os.getcwd()                     # run the script from your project root
OUTPUT_FILE = "project_context.md"

# Folders to skip entirely (matched by folder name, anywhere in the tree)
EXCLUDE_DIRS = {
    "venv", ".venv", "env", "__pycache__", ".git", ".github",
    "node_modules", "dist", "build", ".pytest_cache", ".mypy_cache",
    ".idea", ".vscode", ".bfg-report",
    # third-party vendored source you almost never need to show an AI
    "osm2pgsql", "contrib", "martin",
    # generated/data dirs that are usually huge and not "code"
    "data", "fonts", "clean_fonts",
}

# File name patterns to skip (fnmatch-style, case-insensitive)
EXCLUDE_FILE_PATTERNS = [
    "*.pyc", "*.pyo", "*.so", "*.dll", "*.exe", "*.o", "*.a",
    "*.png", "*.jpg", "*.jpeg", "*.gif", "*.ico", "*.svg", "*.webp",
    "*.ttf", "*.otf", "*.woff", "*.woff2",
    "*.zip", "*.tar", "*.gz", "*.7z", "*.rar",
    "*.db", "*.sqlite3", "*.mbtiles", "*.pbf", "*.pmtiles",
    "*.pdf", "*.mp4", "*.mov",
    "*.lock",                 # poetry.lock / package-lock.json etc (often huge)
    OUTPUT_FILE,
]

# Anything matching these is treated as a SECRET: never print contents,
# just note that it exists and was skipped.
SECRET_PATTERNS = [
    ".env", ".env.*", "*.pem", "*.key", "*credentials*", "*secret*",
]

# Hard cap per file (characters) to avoid one giant generated file blowing
# up the whole dump. Files larger than this get truncated with a note.
MAX_FILE_CHARS = 20000

# Map file extensions to markdown code-fence language tags
LANG_MAP = {
    ".py": "python", ".js": "javascript", ".ts": "typescript",
    ".tsx": "tsx", ".jsx": "jsx", ".json": "json", ".yml": "yaml",
    ".yaml": "yaml", ".toml": "toml", ".ini": "ini", ".cfg": "ini",
    ".sql": "sql", ".sh": "bash", ".bat": "bat", ".ps1": "powershell",
    ".html": "html", ".css": "css", ".md": "markdown", ".txt": "",
    ".lua": "lua", ".dockerfile": "dockerfile",
}

# ---------------------------------------------------------------------------
# IMPLEMENTATION — usually no need to touch below this line
# ---------------------------------------------------------------------------


def is_excluded_dir(dirname: str) -> bool:
    return dirname in EXCLUDE_DIRS or dirname.startswith(".") and dirname not in {".env.example"}


def matches_any(name: str, patterns) -> bool:
    name_low = name.lower()
    return any(fnmatch.fnmatch(name_low, pat.lower()) for pat in patterns)


def is_secret(name: str) -> bool:
    return matches_any(name, SECRET_PATTERNS)


def is_excluded_file(name: str) -> bool:
    return matches_any(name, EXCLUDE_FILE_PATTERNS)


def lang_for(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    return LANG_MAP.get(ext, "")


def build_tree(root: str) -> str:
    lines = []
    for current_root, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if not is_excluded_dir(d))
        rel = os.path.relpath(current_root, root)
        depth = 0 if rel == "." else rel.count(os.sep) + 1
        indent = "    " * depth
        label = os.path.basename(current_root) if rel != "." else os.path.basename(root) or root
        lines.append(f"{indent}{label}/")
        sub_indent = "    " * (depth + 1)
        for f in sorted(files):
            if is_excluded_file(f):
                continue
            tag = " (secret, content skipped)" if is_secret(f) else ""
            lines.append(f"{sub_indent}{f}{tag}")
    return "\n".join(lines)


def read_text_safely(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except UnicodeDecodeError:
        return None  # binary or non-utf8, skip content
    except Exception as e:
        return f"<<could not read file: {e}>>"


def main():
    root = ROOT
    print(f"Scanning project at: {root}")

    out_lines = []
    out_lines.append("# PROJECT CONTEXT\n")
    out_lines.append(
        "This file was auto-generated to give an AI assistant full context "
        "on this project: folder structure plus the content of every "
        "relevant source file. Secrets (.env, keys, credentials) are "
        "intentionally excluded.\n"
    )

    out_lines.append("## FOLDER STRUCTURE\n")
    out_lines.append("```")
    out_lines.append(build_tree(root))
    out_lines.append("```\n")

    out_lines.append("## FILES\n")

    file_count = 0
    skipped_secret = 0
    skipped_binary = 0

    for current_root, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if not is_excluded_dir(d))
        for f in sorted(files):
            if is_excluded_file(f):
                continue

            full_path = os.path.join(current_root, f)
            rel_path = os.path.relpath(full_path, root).replace("\\", "/")

            if is_secret(f):
                skipped_secret += 1
                out_lines.append(f"### {rel_path}\n")
                out_lines.append("_Skipped: looks like a secret/credentials file._\n")
                continue

            content = read_text_safely(full_path)
            if content is None:
                skipped_binary += 1
                continue

            truncated_note = ""
            if len(content) > MAX_FILE_CHARS:
                content = content[:MAX_FILE_CHARS]
                truncated_note = "\n\n_(truncated — file exceeds size limit)_"

            lang = lang_for(rel_path)
            out_lines.append(f"### {rel_path}\n")
            out_lines.append(f"```{lang}")
            out_lines.append(content.rstrip())
            out_lines.append("```" + truncated_note + "\n")
            file_count += 1

    out_path = os.path.join(root, OUTPUT_FILE)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out_lines))

    print(f"Done. Wrote {file_count} files into: {out_path}")
    print(f"Skipped {skipped_secret} secret file(s), {skipped_binary} binary/unreadable file(s).")
    print("Review the output once before sharing it — double-check no secrets leaked in.")


if __name__ == "__main__":
    main()