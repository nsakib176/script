# Image Gallery Downloader

A Python tool that automatically downloads full-resolution images from gallery URLs into organized folders. Available as both a GUI application and command-line script.

## Features

- **Easy-to-use GUI** with folder selection, progress tracking, and status updates
- Downloads images from any gallery URL supported by [gallery-dl](https://github.com/mikf/gallery-dl)
- Automatically creates folders named after the gallery (uses page title or URL slug)
- Preserves original filenames when available
- Supports batch processing of multiple URLs
- Windows-optimized (sanitizes folder names for Windows compatibility)
- Real-time progress bar and per-gallery status indicators

## Requirements

- Python 3.8 or higher
- Windows PowerShell (or any terminal)

## Setup

### 1. Create Virtual Environment

Open PowerShell in the project directory (`E:\sort\script`) and run:

```powershell
# Create virtual environment
py -3 -m venv .venv

# Activate it
.\.venv\Scripts\Activate.ps1
```

**Note:** If you get an execution policy error, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Install Dependencies

With the virtual environment activated:

```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install required packages
pip install -r requirements.txt
```

This will install:

- `gallery-dl` - The core downloader library
- `requests` - For fetching page titles
- `beautifulsoup4` - For parsing HTML

**Note:** The GUI uses Tkinter, which is built into Python - no separate installation needed!

## Usage

### GUI Application (Recommended)

The easiest way to use the downloader is through the graphical interface:

1. Activate the virtual environment if not already active:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

2. Run the GUI:

   ```powershell
   python gui.py
   ```

3. In the GUI window:
   - **Download Folder**: Select where you want to save the galleries (defaults to `downloads` folder)
   - **Gallery URLs**: Paste one or more gallery URLs (one per line)
   - Click **Download** to start
   - Watch the progress bar and status updates for each gallery
   - A popup will notify you when all downloads are complete

**GUI Features:**

- Overall progress bar showing completion across all galleries
- Per-gallery status showing: Queued → Analyzing → Downloading → ✓ Success / ✗ Failed
- Ability to change download location for each batch
- Console output still visible in the terminal for detailed logs

### Command-Line Usage

If you prefer the command line, you can use the original script:

#### Basic Usage (Single URL)

1. Activate the virtual environment if not already active:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

2. Run the script:

   ```powershell
   python download_gallery.py
   ```

3. Paste your gallery URL and press Enter twice:

   ```
   Paste one or more gallery URLs (space or newline separated).
   Press Enter twice when done:

   https://example.com/gallery/12345
   [press Enter twice]
   ```

#### Multiple URLs at Once

You can paste multiple URLs separated by spaces or newlines:

```
https://example.com/gallery/12345
https://example.com/album/67890
https://another-site.com/collection/abc
[press Enter twice]
```

#### How It Works

For each URL:

1. The script fetches the page and tries to extract the `<title>` tag
2. If found, it uses the title as the folder name (sanitized for Windows)
3. If not found, it uses the last segment of the URL path
4. Creates a folder: `E:\sort\script\downloads\<folder-name>`
5. Runs `gallery-dl` to download all images in full resolution

#### Examples

**Example 1: Gallery with a title**

```
URL: https://imgur.com/a/abcd1234
Title: "My Vacation Photos"
Downloads to: E:\sort\script\downloads\My Vacation Photos\
```

**Example 2: URL with no accessible title**

```
URL: https://example.com/galleries/artwork_collection
Title: (not accessible)
Downloads to: E:\sort\script\downloads\artwork_collection\
```

## Output Location

All downloads are saved to:

```
E:\sort\script\downloads\<gallery-folder-name>\
```

Each gallery gets its own folder automatically created.

## Supported Sites

This script supports any site that [gallery-dl](https://github.com/mikf/gallery-dl#supported-sites) supports, including:

- Imgur
- Flickr
- DeviantArt
- ArtStation
- Reddit
- Tumblr
- Twitter/X
- Many more (500+ sites)

## Troubleshooting

### GUI Issues

**GUI window doesn't open**

The GUI uses Tkinter, which is built into Python. If the window doesn't appear:

- Check if it's hidden behind other windows
- Make sure you're running Python 3.8 or higher
- On some minimal Python installations, you may need to install `python3-tk` (Linux) or reinstall Python with Tkinter support (Windows)

**No progress shown during download**

The progress bar updates per-gallery, not per-image. For very large galleries, it may appear stuck while downloading. Check the console output for detailed progress from gallery-dl.

**Download fails but no error shown**

Check the console/terminal window where you launched `gui.py`. Detailed error messages from gallery-dl will appear there.

### Command-Line Issues

#### "gallery-dl not found" error

Make sure you've installed the requirements:

```powershell
pip install -r requirements.txt
```

#### Empty title causes weird folder names

The script will fall back to using the URL path segment. This is normal for sites that don't expose titles easily.

#### Downloads fail for certain sites

Some sites require authentication or have rate limits. Check the [gallery-dl documentation](https://github.com/mikf/gallery-dl/blob/master/docs/configuration.rst) for site-specific configuration options.

#### Script can't fetch page title

This is normal for some sites. The script will automatically fall back to using the URL path as the folder name.

## Advanced Configuration

### Custom gallery-dl Options

If you need to customize gallery-dl behavior (e.g., for sites requiring login), create a `gallery-dl.conf` file in your home directory or use command-line options.

See: https://github.com/mikf/gallery-dl/blob/master/docs/configuration.rst

### Changing the Download Location

Edit line 18 in `download_gallery.py`:

```python
BASE_DIR = Path(__file__).parent / "downloads"
```

Change `"downloads"` to your preferred location.

## Notes

- **Full Resolution**: gallery-dl downloads the highest quality available by default for most sites
- **Duplicate Prevention**: gallery-dl automatically skips already-downloaded files
- **Original Filenames**: The script uses the `-f /O` flag to preserve original filenames when available

## License

This script is provided as-is for personal use.
