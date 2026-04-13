#!/usr/bin/env python3
"""GUI app for converting videos to Nokia 235 4G-compatible MP4 files."""

from __future__ import annotations

import subprocess
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

MAX_INPUT_SIZE_BYTES = 5 * 1024 * 1024 * 1024  # 5GB


class NokiaConverterApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Nokia 235 4G Movie Converter")
        self.root.geometry("680x420")
        self.root.minsize(680, 420)

        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.quality_mode = tk.StringVar(value="Balanced")
        self.status_text = tk.StringVar(value="Ready")
        self.running = False

        self._build_ui()

    def _build_ui(self) -> None:
        frame = ttk.Frame(self.root, padding=16)
        frame.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(
            frame,
            text="Convert videos (up to 5GB) for Nokia 235 4G",
            font=("Segoe UI", 15, "bold"),
        )
        title.pack(anchor=tk.W, pady=(0, 14))

        self._path_picker(
            frame,
            "Input movie",
            self.input_path,
            browse_command=self._choose_input,
        )

        self._path_picker(
            frame,
            "Output MP4",
            self.output_path,
            browse_command=self._choose_output,
        )

        quality_wrap = ttk.LabelFrame(frame, text="Quality profile", padding=12)
        quality_wrap.pack(fill=tk.X, pady=12)

        profiles = [
            ("High (largest file)", "High"),
            ("Balanced", "Balanced"),
            ("Data Saver (smallest file)", "Small"),
        ]
        for text, value in profiles:
            ttk.Radiobutton(
                quality_wrap,
                text=text,
                variable=self.quality_mode,
                value=value,
            ).pack(anchor=tk.W, pady=2)

        note = ttk.Label(
            frame,
            text=(
                "Preset: MP4 (H.264 Baseline + AAC), 320x240, 25fps. "
                "Optimized for feature phones."
            ),
            foreground="#444",
        )
        note.pack(anchor=tk.W, pady=(2, 10))

        controls = ttk.Frame(frame)
        controls.pack(fill=tk.X)

        self.convert_btn = ttk.Button(controls, text="Convert", command=self.start_conversion)
        self.convert_btn.pack(side=tk.LEFT)

        self.progress = ttk.Progressbar(frame, mode="indeterminate")
        self.progress.pack(fill=tk.X, pady=16)

        status = ttk.Label(frame, textvariable=self.status_text)
        status.pack(anchor=tk.W)

    def _path_picker(
        self,
        parent: ttk.Frame,
        label: str,
        variable: tk.StringVar,
        browse_command,
    ) -> None:
        wrap = ttk.Frame(parent)
        wrap.pack(fill=tk.X, pady=6)
        ttk.Label(wrap, text=label).pack(anchor=tk.W)

        row = ttk.Frame(wrap)
        row.pack(fill=tk.X, pady=(3, 0))
        ttk.Entry(row, textvariable=variable).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(row, text="Browse", command=browse_command).pack(side=tk.LEFT, padx=(8, 0))

    def _choose_input(self) -> None:
        selected = filedialog.askopenfilename(
            title="Select input movie",
            filetypes=[("Video files", "*.mp4 *.mkv *.avi *.mov *.webm"), ("All", "*.*")],
        )
        if selected:
            self.input_path.set(selected)
            default_output = str(Path(selected).with_suffix(".nokia235.mp4"))
            if not self.output_path.get().strip():
                self.output_path.set(default_output)

    def _choose_output(self) -> None:
        selected = filedialog.asksaveasfilename(
            title="Save converted movie as",
            defaultextension=".mp4",
            filetypes=[("MP4", "*.mp4")],
        )
        if selected:
            self.output_path.set(selected)

    def _ffmpeg_command(self) -> list[str]:
        quality = self.quality_mode.get()
        # Lower CRF = better quality / larger output.
        crf = {"High": "24", "Balanced": "27", "Small": "30"}.get(quality, "27")

        return [
            "ffmpeg",
            "-y",
            "-i",
            self.input_path.get(),
            "-vf",
            "scale=320:240:force_original_aspect_ratio=decrease,pad=320:240:(ow-iw)/2:(oh-ih)/2:black",
            "-r",
            "25",
            "-c:v",
            "libx264",
            "-profile:v",
            "baseline",
            "-level",
            "3.0",
            "-preset",
            "slow",
            "-crf",
            crf,
            "-maxrate",
            "380k",
            "-bufsize",
            "760k",
            "-c:a",
            "aac",
            "-ar",
            "44100",
            "-ac",
            "1",
            "-b:a",
            "64k",
            "-movflags",
            "+faststart",
            self.output_path.get(),
        ]

    def start_conversion(self) -> None:
        if self.running:
            return

        input_file = Path(self.input_path.get().strip())
        output_file = Path(self.output_path.get().strip())

        if not input_file.exists():
            messagebox.showerror("Missing input", "Please choose a valid input movie file.")
            return
        if input_file.stat().st_size > MAX_INPUT_SIZE_BYTES:
            messagebox.showerror("Too large", "Input file is bigger than 5GB.")
            return
        if not output_file.parent.exists():
            messagebox.showerror("Invalid output", "Output folder does not exist.")
            return

        self.running = True
        self.convert_btn.configure(state=tk.DISABLED)
        self.progress.start(10)
        self.status_text.set("Converting... this may take a while for big files.")

        thread = threading.Thread(target=self._convert_worker, daemon=True)
        thread.start()

    def _convert_worker(self) -> None:
        command = self._ffmpeg_command()

        try:
            process = subprocess.run(command, capture_output=True, text=True, check=False)
            if process.returncode == 0:
                self.root.after(0, self._on_success)
            else:
                self.root.after(0, self._on_error, process.stderr[-1500:])
        except FileNotFoundError:
            self.root.after(
                0,
                self._on_error,
                "ffmpeg was not found. Install ffmpeg and add it to PATH.",
            )

    def _on_success(self) -> None:
        self.running = False
        self.convert_btn.configure(state=tk.NORMAL)
        self.progress.stop()
        self.status_text.set("Done. Converted movie is ready.")
        messagebox.showinfo("Success", "Movie converted successfully for Nokia 235 4G.")

    def _on_error(self, details: str) -> None:
        self.running = False
        self.convert_btn.configure(state=tk.NORMAL)
        self.progress.stop()
        self.status_text.set("Conversion failed")
        messagebox.showerror("Conversion failed", f"Could not convert file.\n\nDetails:\n{details}")


def main() -> None:
    root = tk.Tk()
    root.style = ttk.Style(root)
    if "vista" in root.style.theme_names():
        root.style.theme_use("vista")
    NokiaConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
