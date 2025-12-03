#!/usr/bin/env python3
"""
Gallery Downloader GUI
Simple Tkinter interface for downloading image galleries.
"""

import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
from pathlib import Path

from download_gallery import parse_urls, derive_folder_name, download_gallery, BASE_DIR


class GalleryDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Gallery Downloader")
        self.root.geometry("800x700")

        # State variables
        self.status_items = []
        self.download_thread = None
        self.total_urls = 0
        self.completed_count = 0
        self.is_downloading = False

        self.setup_ui()

    def setup_ui(self):
        """Create the user interface."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame, text="Image Gallery Downloader", font=("Helvetica", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))

        # Separator
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(
            row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5
        )

        # Download folder selection
        row = 2
        ttk.Label(main_frame, text="Download Folder:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )

        self.folder_var = tk.StringVar(value=str(BASE_DIR.absolute()))
        folder_entry = ttk.Entry(main_frame, textvariable=self.folder_var, width=60)
        folder_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

        browse_btn = ttk.Button(
            main_frame, text="Browse...", command=self.browse_folder
        )
        browse_btn.grid(row=row, column=2, pady=5)

        main_frame.columnconfigure(1, weight=1)

        # Separator
        row += 1
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5
        )

        # URLs input
        row += 1
        ttk.Label(main_frame, text="Gallery URLs (one per line):").grid(
            row=row, column=0, columnspan=3, sticky=tk.W, pady=(5, 0)
        )

        row += 1
        self.urls_text = scrolledtext.ScrolledText(
            main_frame, width=70, height=10, font=("Courier", 10)
        )
        self.urls_text.grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5
        )
        main_frame.rowconfigure(row, weight=1)

        # Separator
        row += 1
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5
        )

        # Progress section
        row += 1
        ttk.Label(main_frame, text="Progress:").grid(
            row=row, column=0, columnspan=3, sticky=tk.W, pady=(5, 0)
        )

        row += 1
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100,
            mode="determinate",
            length=400,
        )
        self.progress_bar.grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5
        )

        # Status listbox
        row += 1
        ttk.Label(main_frame, text="Status:").grid(
            row=row, column=0, columnspan=3, sticky=tk.W, pady=(5, 0)
        )

        row += 1
        # Frame for listbox and scrollbar
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5
        )
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)

        self.status_listbox = tk.Listbox(status_frame, height=8, font=("Courier", 9))
        status_scrollbar = ttk.Scrollbar(
            status_frame, orient=tk.VERTICAL, command=self.status_listbox.yview
        )
        self.status_listbox.configure(yscrollcommand=status_scrollbar.set)

        self.status_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        status_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        main_frame.rowconfigure(row, weight=2)

        # Separator
        row += 1
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5
        )

        # Control buttons
        row += 1
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=10)

        self.download_btn = ttk.Button(
            button_frame, text="Download", command=self.start_download, width=15
        )
        self.download_btn.grid(row=0, column=0, padx=5)

        exit_btn = ttk.Button(
            button_frame, text="Exit", command=self.root.quit, width=15
        )
        exit_btn.grid(row=0, column=1, padx=5)

    def browse_folder(self):
        """Open folder browser dialog."""
        folder = filedialog.askdirectory(
            initialdir=self.folder_var.get(), title="Select Download Folder"
        )
        if folder:
            self.folder_var.set(folder)

    def start_download(self):
        """Start the download process."""
        if self.is_downloading:
            messagebox.showwarning(
                "Download in Progress", "A download is already in progress!"
            )
            return

        # Get and validate URLs
        urls_text = self.urls_text.get("1.0", tk.END).strip()
        if not urls_text:
            messagebox.showerror("No URLs", "Please enter at least one gallery URL.")
            return

        urls = parse_urls(urls_text)
        if not urls:
            messagebox.showerror(
                "Invalid URLs",
                "No valid URLs found. URLs must start with http:// or https://",
            )
            return

        # Validate download directory
        download_dir = self.folder_var.get().strip()
        if not download_dir:
            messagebox.showerror("No Folder", "Please select a download folder.")
            return

        # Initialize status tracking
        self.total_urls = len(urls)
        self.completed_count = 0
        self.status_items = [f"[Queued] {url}" for url in urls]
        self.is_downloading = True

        # Update UI
        self.status_listbox.delete(0, tk.END)
        for item in self.status_items:
            self.status_listbox.insert(tk.END, item)

        self.progress_var.set(0)
        self.progress_bar.configure(maximum=self.total_urls)
        self.download_btn.configure(state="disabled")

        print(f"\nStarting download of {self.total_urls} gallery(s)...")
        print(f"Target directory: {download_dir}")

        # Start worker thread
        self.download_thread = threading.Thread(
            target=self.worker, args=(urls, download_dir), daemon=True
        )
        self.download_thread.start()

    def worker(self, urls, base_dir):
        """Background worker thread that downloads galleries."""
        for idx, url in enumerate(urls):
            # Update status: deriving folder name
            self.update_status(idx, f"Analyzing URL...", url)

            try:
                folder_name = derive_folder_name(url)

                # Update status: downloading
                self.update_status(idx, f'Downloading to "{folder_name}"...', url)

                # Perform download
                ok = download_gallery(url, folder_name, base_dir=Path(base_dir))

                # Report completion
                self.complete_one(idx, ok, folder_name, url)

            except Exception as e:
                # Handle any unexpected errors
                self.complete_one(idx, False, "error", url, str(e))

        # All downloads complete
        self.all_complete()

    def update_status(self, idx, text, url):
        """Update status for a specific URL."""

        def update():
            if idx < len(self.status_items):
                self.status_items[idx] = f"[...] {text} - {url}"
                self.status_listbox.delete(idx)
                self.status_listbox.insert(idx, self.status_items[idx])
                self.status_listbox.see(idx)

        self.root.after(0, update)

    def complete_one(self, idx, ok, folder, url, error=None):
        """Mark one download as complete."""
        self.completed_count += 1

        def update():
            if ok:
                self.status_items[idx] = f'[✓] Success: "{folder}" - {url}'
                print(f"  [{self.completed_count}/{self.total_urls}] ✓ {url}")
            else:
                error_msg = error if error else "Download failed"
                self.status_items[idx] = f"[✗] Failed: {error_msg} - {url}"
                print(f"  [{self.completed_count}/{self.total_urls}] ✗ {url}")

            self.status_listbox.delete(idx)
            self.status_listbox.insert(idx, self.status_items[idx])
            self.status_listbox.see(idx)
            self.progress_var.set(self.completed_count)

        self.root.after(0, update)

    def all_complete(self):
        """Called when all downloads are complete."""

        def update():
            self.download_btn.configure(state="normal")
            self.is_downloading = False

            success_count = sum(1 for item in self.status_items if "[✓]" in item)

            print("\n" + "=" * 60)
            print(
                f"All downloads complete: {success_count}/{self.total_urls} successful"
            )
            print("=" * 60)

            messagebox.showinfo(
                "Download Complete",
                f"Download Complete!\n\n"
                f"Successful: {success_count}/{self.total_urls}\n"
                f"Files saved to: {self.folder_var.get()}",
            )

        self.root.after(0, update)


def main():
    """Main application entry point."""
    print("=" * 60)
    print("Gallery Downloader GUI Started")
    print("=" * 60)

    root = tk.Tk()
    app = GalleryDownloaderGUI(root)
    root.mainloop()

    print("\nGUI closed.")


if __name__ == "__main__":
    main()
