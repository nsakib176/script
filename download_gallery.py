#!/usr/bin/env python3
"""
Image Gallery Downloader
Downloads full-resolution images from gallery URLs into organized folders.
"""

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


# Base download directory
BASE_DIR = Path(__file__).parent / "downloads"


def sanitize_folder_name(name: str) -> str:
    """
    Sanitize a string to be a valid Windows folder name.
    Removes invalid characters: < > : " / \\ | ? *
    Trims leading/trailing spaces and dots.
    """
    # Replace invalid characters with underscore
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, "_", name)

    # Remove control characters
    sanitized = "".join(char for char in sanitized if ord(char) >= 32)

    # Trim spaces and dots from ends
    sanitized = sanitized.strip(" .")

    # Ensure not empty
    if not sanitized:
        sanitized = "gallery"

    # Truncate if too long (Windows has 255 char limit for folder names)
    if len(sanitized) > 200:
        sanitized = sanitized[:200].strip(" .")

    return sanitized


def get_page_title(url: str) -> str:
    """
    Fetch the page and extract its <title> tag.
    Returns empty string if unable to fetch or parse.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        title_tag = soup.find("title")

        if title_tag and title_tag.string:
            return title_tag.string.strip()
    except Exception as e:
        print(f"  Warning: Could not fetch page title ({e})")

    return ""


def get_folder_name_from_url(url: str) -> str:
    """
    Extract a folder name from the URL path (last non-empty segment).
    """
    parsed = urlparse(url)
    path_parts = [p for p in parsed.path.split("/") if p]

    if path_parts:
        # Use the last path segment
        return path_parts[-1]
    elif parsed.netloc:
        # Fallback to domain name if no path
        return parsed.netloc.replace(".", "_")
    else:
        return "gallery"


def derive_folder_name(url: str) -> str:
    """
    Determine folder name: prefer page title, fallback to URL slug.
    Returns a sanitized, Windows-safe folder name.
    """
    print(f"  Analyzing URL: {url}")

    # Try to get page title first
    title = get_page_title(url)

    if title:
        print(f"  Found title: {title}")
        folder_name = sanitize_folder_name(title)
    else:
        print("  No title found, using URL path")
        url_slug = get_folder_name_from_url(url)
        folder_name = sanitize_folder_name(url_slug)

    print(f"  Folder name: {folder_name}")
    return folder_name


def download_gallery(url: str, folder_name: str, base_dir: Path | None = None) -> bool:
    """
    Download a gallery using gallery-dl to the specified folder.
    Returns True if successful, False otherwise.
    """
    target_root = base_dir if base_dir is not None else BASE_DIR
    target_dir = target_root / folder_name
    target_dir.mkdir(parents=True, exist_ok=True)

    print(f"  Downloading to: {target_dir}")

    # Build gallery-dl command
    cmd = [
        sys.executable,
        "-m",
        "gallery_dl",
        "-f",
        "/O",  # Use original filenames when available
        "-D",
        str(target_dir),  # Exact target directory
        url,
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"  Error: gallery-dl failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print("  Error: gallery-dl not found. Make sure it's installed:")
        print("    pip install gallery-dl")
        return False


def parse_urls(input_text: str) -> list[str]:
    """
    Parse input text into individual URLs.
    Supports space-separated and newline-separated URLs.
    """
    # Split by whitespace and filter out empty strings
    urls = input_text.split()

    # Basic URL validation (starts with http:// or https://)
    valid_urls = []
    for url in urls:
        url = url.strip()
        if url.startswith(("http://", "https://")):
            valid_urls.append(url)
        elif url:
            print(f"Warning: Skipping invalid URL: {url}")

    return valid_urls


def main():
    """Main entry point."""
    print("=" * 60)
    print("Image Gallery Downloader")
    print("=" * 60)
    print()
    print("Paste one or more gallery URLs (space or newline separated).")
    print("Press Enter twice when done:")
    print()

    # Read multi-line input
    lines = []
    try:
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
    except EOFError:
        pass

    if not lines:
        print("No URLs provided. Exiting.")
        return

    input_text = " ".join(lines)
    urls = parse_urls(input_text)

    if not urls:
        print("No valid URLs found. Exiting.")
        return

    print()
    print(f"Found {len(urls)} URL(s) to process")
    print()

    # Process each URL
    success_count = 0
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] Processing: {url}")

        # Derive folder name
        folder_name = derive_folder_name(url)

        # Download
        if download_gallery(url, folder_name):
            success_count += 1
            print("  ✓ Success")
        else:
            print("  ✗ Failed")

        print()

    # Summary
    print("=" * 60)
    print(f"Download complete: {success_count}/{len(urls)} successful")
    print(f"Files saved to: {BASE_DIR.absolute()}")
    print("=" * 60)


if __name__ == "__main__":
    main()
