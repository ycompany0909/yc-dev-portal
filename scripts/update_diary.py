#!/usr/bin/env python3
"""
Auto-update YC Dev Diary from git commit history.

Runs daily via GitHub Actions (JST midnight).
Manual run: DATE=2026-05-18 python scripts/update_diary.py

Required env vars:
  ANTHROPIC_API_KEY   Claude API key
  GH_TOKEN            GitHub PAT with repo read access
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import anthropic

JST = timezone(timedelta(hours=9))
DIARY_HTML = Path(__file__).parent.parent / "docs" / "diary.html"

# (github_repo, display_name, css_tag)
REPOS = [
    ("ycompany0909/Operation-Management", "Operation-Management", "tag-op"),
    ("ycompany0909/yc-workers",           "yc-workers",           "tag-workers"),
    ("ycompany0909/yc-accounting",        "yc-accounting",        "tag-accounting"),
    ("ycompany0909/yc-dotfiles",          "yc-dotfiles",          "tag-dotfiles"),
    ("ycompany0909/orzugul-portal",       "orzugul-portal",       "tag-portal"),
    ("ycompany0909/Setagaya-seiji",       "Setagaya-seiji",       "tag-setagaya"),
    ("ycompany0909/timetree-mail",        "timetree-mail",        "tag-other"),
    ("ycompany0909/demoday-2026",         "demoday-2026",         "tag-other"),
    ("ycompany0909/yc-dev-portal",        "yc-dev-portal",        "tag-dotfiles"),
    ("ycompany0909/YC-Brain",             "YC-Brain",             "tag-other"),
]


def target_date() -> str:
    """Yesterday in JST. Override with DATE env var for backfill/testing."""
    if d := os.environ.get("DATE"):
        return d
    return (datetime.now(JST) - timedelta(days=1)).strftime("%Y-%m-%d")


def fetch_commits(repo: str, date_str: str) -> list[str]:
    since = f"{date_str}T00:00:00+09:00"
    until = f"{date_str}T23:59:59+09:00"
    result = subprocess.run(
        [
            "gh", "api",
            f"repos/{repo}/commits"
            f"?since={since}&until={until}&per_page=100",
            "--paginate",
            "-q", '[.[].commit.message | split("\\n")[0]] | .[]',
        ],
        capture_output=True, text=True,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return []
    msgs = []
    for line in result.stdout.strip().splitlines():
        line = line.strip()
        if line and not line.lower().startswith("merge"):
            msgs.append(line)
    return msgs


def summarize(repo_name: str, commits: list[str]) -> list[dict]:
    client = anthropic.Anthropic()
    commits_text = "\n".join(f"- {c}" for c in commits)

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=800,
        messages=[{
            "role": "user",
            "content": (
                f"以下は「{repo_name}」の本日のgitコミット一覧です。\n"
                "開発日記用にグループ化・日本語要約してください。\n\n"
                f"{commits_text}\n\n"
                "JSON配列のみで返してください（説明文・コードブロック不要）:\n"
                "[\n"
                '  {"type": "feat", "text": "日本語説明（60文字以内）"},\n'
                '  {"type": "fix",  "text": "日本語説明"}\n'
                "]\n\n"
                "type は feat/fix/docs/refactor/init のいずれか。\n"
                "重複・細かいものはまとめる。必ず日本語で記述。"
            ),
        }],
    )

    text = response.content[0].text.strip()
    match = re.search(r'\[.*?\]', text, re.DOTALL)
    if not match:
        return [{"type": "feat", "text": c[:60]} for c in commits[:8]]
    try:
        items = json.loads(match.group())
        # Ensure text is within 80 chars
        for item in items:
            item["text"] = item["text"][:80]
        return items
    except json.JSONDecodeError:
        return [{"type": "feat", "text": c[:60]} for c in commits[:8]]


def build_entry_js(date_str: str, sections: list[dict]) -> str:
    lines = [f'  "{date_str}": [']
    for sec in sections:
        lines.append(f'    {{ repo: "{sec["repo"]}", tag: "{sec["tag"]}", items: [')
        for item in sec["items"]:
            text = item["text"].replace("\\", "\\\\").replace('"', '\\"').replace("</", "<\\/")
            lines.append(f'      {{ type: "{item["type"]}", text: "{text}" }},')
        lines.append('    ]},')
    lines.append('  ]')
    return "\n".join(lines)


def update_diary(date_str: str, sections: list[dict]) -> bool:
    html = DIARY_HTML.read_text(encoding="utf-8")

    if f'"{date_str}"' in html:
        print(f"Entry for {date_str} already exists — skipping.")
        return False

    entry_js = build_entry_js(date_str, sections)

    # The DIARY object tail pattern (last entry has no trailing comma):
    #   ...
    #   ]
    # };
    #
    # let currentYear
    old_tail = "  ]\n};\n\nlet currentYear"
    new_tail = f"  ],\n{entry_js}\n}};\n\nlet currentYear"

    if old_tail not in html:
        print("ERROR: insertion point not found in diary.html", file=sys.stderr)
        sys.exit(1)

    DIARY_HTML.write_text(html.replace(old_tail, new_tail, 1), encoding="utf-8")
    return True


def main():
    date_str = target_date()
    print(f"Fetching commits for {date_str} (JST)...")

    sections = []
    for repo_path, repo_name, tag in REPOS:
        commits = fetch_commits(repo_path, date_str)
        if not commits:
            print(f"  {repo_name}: no commits")
            continue
        print(f"  {repo_name}: {len(commits)} commits → summarizing with Claude...")
        items = summarize(repo_name, commits)
        sections.append({"repo": repo_name, "tag": tag, "items": items})

    if not sections:
        print(f"No commits found on {date_str}. Diary unchanged.")
        return

    if update_diary(date_str, sections):
        print(f"✓ diary.html updated: {date_str} ({len(sections)} repos, "
              f"{sum(len(s['items']) for s in sections)} items)")


if __name__ == "__main__":
    main()
