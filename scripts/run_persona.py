#!/usr/bin/env python3
"""
UX Review — Playwright capture script.
Captures screenshot, cleaned DOM, and accessibility tree for a given URL.

Usage:
    python run_persona.py --url URL --output-dir DIR [--device DEVICE] [--timeout MS]
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Capture page artifacts for UX review")
    parser.add_argument("--url", required=True, help="URL to capture")
    parser.add_argument("--output-dir", required=True, help="Directory to write artifacts")
    parser.add_argument(
        "--device",
        default="Desktop Chrome",
        help='Playwright device descriptor (e.g. "iPhone 14", "Desktop Chrome")',
    )
    parser.add_argument(
        "--timeout", type=int, default=30000, help="Page load timeout in milliseconds"
    )
    return parser.parse_args()


def clean_dom(html: str) -> str:
    """Strip <script> tags and their contents, keep <style> for context."""
    cleaned = re.sub(r"<script[\s\S]*?</script>", "", html, flags=re.IGNORECASE)
    # Remove inline event handlers
    cleaned = re.sub(r'\s+on\w+="[^"]*"', "", cleaned)
    cleaned = re.sub(r"\s+on\w+='[^']*'", "", cleaned)
    return cleaned


def format_a11y_tree(node: dict, indent: int = 0) -> str:
    """Recursively format the accessibility tree into readable text."""
    if node is None:
        return ""

    lines = []
    prefix = "  " * indent
    role = node.get("role", "")
    name = node.get("name", "")

    # Build the node description
    parts = [role]
    if name:
        parts.append(f'"{name}"')

    # Add relevant properties
    for prop in ["value", "description", "checked", "pressed", "level", "expanded"]:
        if prop in node:
            parts.append(f"{prop}={node[prop]}")

    if node.get("disabled"):
        parts.append("(disabled)")
    if node.get("required"):
        parts.append("(required)")

    lines.append(f"{prefix}{' '.join(parts)}")

    # Recurse into children
    for child in node.get("children", []):
        lines.append(format_a11y_tree(child, indent + 1))

    return "\n".join(lines)


def main():
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        error_msg = (
            "Playwright is not installed.\n"
            "Run the following to set up:\n\n"
            "  python3 -m venv ~/.claude/skills/ux-review/venv\n"
            "  source ~/.claude/skills/ux-review/venv/bin/activate\n"
            "  pip install playwright\n"
            "  playwright install chromium\n"
        )
        (output_dir / "error.txt").write_text(error_msg)
        print(error_msg, file=sys.stderr)
        sys.exit(1)

    try:
        with sync_playwright() as p:
            # Resolve device settings
            device_config = p.devices.get(args.device, {})

            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                **device_config,
                ignore_https_errors=True,
            )
            page = context.new_page()

            # Navigate
            print(f"Navigating to {args.url} ...", file=sys.stderr)
            page.goto(args.url, wait_until="networkidle", timeout=args.timeout)

            # 1. Full-page screenshot
            screenshot_path = output_dir / "screenshot.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"Screenshot saved: {screenshot_path}", file=sys.stderr)

            # 2. Cleaned DOM
            raw_html = page.content()
            cleaned = clean_dom(raw_html)
            dom_path = output_dir / "dom.html"
            dom_path.write_text(cleaned, encoding="utf-8")
            print(f"DOM saved: {dom_path}", file=sys.stderr)

            # 3. Accessibility tree (aria_snapshot for Playwright 1.49+)
            try:
                tree_text = page.locator(":root").aria_snapshot()
            except Exception:
                # Fallback for older Playwright versions
                try:
                    a11y_snapshot = page.accessibility.snapshot()
                    tree_text = format_a11y_tree(a11y_snapshot) if a11y_snapshot else ""
                except Exception:
                    tree_text = ""
            if not tree_text:
                tree_text = "(No accessibility tree available for this page)"
            a11y_path = output_dir / "a11y-tree.txt"
            a11y_path.write_text(tree_text, encoding="utf-8")
            print(f"Accessibility tree saved: {a11y_path}", file=sys.stderr)

            # Write metadata
            metadata = {
                "url": args.url,
                "device": args.device,
                "viewport": device_config.get("viewport", {"width": 1280, "height": 720}),
                "user_agent": device_config.get("user_agent", "default"),
            }
            (output_dir / "metadata.json").write_text(
                json.dumps(metadata, indent=2), encoding="utf-8"
            )

            browser.close()
            print("Capture complete.", file=sys.stderr)

    except Exception as e:
        error_msg = f"Capture failed: {type(e).__name__}: {e}"
        (output_dir / "error.txt").write_text(error_msg)
        print(error_msg, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
