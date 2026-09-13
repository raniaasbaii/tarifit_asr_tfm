from __future__ import annotations

import csv
import subprocess
import sys
import time
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CSV_PATH = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "manual_transcription_pilot.csv"
)

PILOT_AUDIO_DIR = (
    PROJECT_ROOT
    / "data"
    / "pilot_audio"
)


class TranscriptionApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Tarifit Manual Transcription")
        self.root.geometry("900x650")

        self.rows = self.load_csv()
        self.current_index = self.find_first_unfinished()
        self.segment_start_time = time.time()

        self.create_widgets()
        self.load_segment()

    def load_csv(self) -> list[dict[str, str]]:
        if not CSV_PATH.exists():
            raise FileNotFoundError(
                f"CSV file not found:\n{CSV_PATH}"
            )

        with CSV_PATH.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as file:
            rows = list(csv.DictReader(file))

        if not rows:
            raise ValueError("The transcription CSV is empty.")

        return rows

    def find_first_unfinished(self) -> int:
        for index, row in enumerate(self.rows):
            if row.get("transcription_status") != "completed":
                return index

        return 0

    def create_widgets(self) -> None:
        main_frame = ttk.Frame(
            self.root,
            padding=15,
        )
        main_frame.pack(
            fill="both",
            expand=True,
        )

        self.progress_label = ttk.Label(
            main_frame,
            font=("Arial", 12, "bold"),
        )
        self.progress_label.pack(anchor="w")

        self.segment_label = ttk.Label(
            main_frame,
            font=("Arial", 16, "bold"),
        )
        self.segment_label.pack(
            anchor="w",
            pady=(10, 5),
        )

        self.metadata_label = ttk.Label(
            main_frame,
            justify="left",
        )
        self.metadata_label.pack(
            anchor="w",
            pady=(0, 15),
        )

        audio_frame = ttk.Frame(main_frame)
        audio_frame.pack(
            fill="x",
            pady=(0, 15),
        )

        ttk.Button(
            audio_frame,
            text="▶ Play audio",
            command=self.play_audio,
        ).pack(side="left")

        ttk.Button(
            audio_frame,
            text="▶ Play again",
            command=self.play_audio,
        ).pack(
            side="left",
            padx=10,
        )

        ttk.Label(
            main_frame,
            text="Manual transcription",
            font=("Arial", 11, "bold"),
        ).pack(anchor="w")

        self.transcription_text = tk.Text(
            main_frame,
            height=7,
            wrap="word",
            font=("Arial", 15),
        )
        self.transcription_text.pack(
            fill="x",
            pady=(5, 15),
        )

        ttk.Label(
            main_frame,
            text="Uncertainty notes",
            font=("Arial", 11, "bold"),
        ).pack(anchor="w")

        self.notes_text = tk.Text(
            main_frame,
            height=4,
            wrap="word",
        )
        self.notes_text.pack(
            fill="x",
            pady=(5, 15),
        )

        status_frame = ttk.Frame(main_frame)
        status_frame.pack(
            fill="x",
            pady=(0, 15),
        )

        ttk.Label(
            status_frame,
            text="Status:",
        ).pack(side="left")

        self.status_var = tk.StringVar(
            value="not_started"
        )

        self.status_menu = ttk.Combobox(
            status_frame,
            textvariable=self.status_var,
            values=[
                "not_started",
                "in_progress",
                "completed",
                "uncertain",
            ],
            state="readonly",
            width=20,
        )
        self.status_menu.pack(
            side="left",
            padx=10,
        )

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")

        ttk.Button(
            button_frame,
            text="← Previous",
            command=self.previous_segment,
        ).pack(side="left")

        ttk.Button(
            button_frame,
            text="Save",
            command=self.save_current,
        ).pack(
            side="left",
            padx=10,
        )

        ttk.Button(
            button_frame,
            text="Save & Next →",
            command=self.next_segment,
        ).pack(side="left")

        ttk.Button(
            button_frame,
            text="Quit",
            command=self.close_app,
        ).pack(side="right")

        self.message_label = ttk.Label(
            main_frame,
            text="",
        )
        self.message_label.pack(
            anchor="w",
            pady=(15, 0),
        )

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close_app,
        )

    def get_audio_path(self) -> Path:
        segment_id = self.rows[
            self.current_index
        ]["segment_id"]

        return (
            PILOT_AUDIO_DIR
            / f"{segment_id}.wav"
        )

    def load_segment(self) -> None:
        row = self.rows[self.current_index]

        self.progress_label.config(
            text=(
                f"Segment {self.current_index + 1} "
                f"of {len(self.rows)}"
            )
        )

        self.segment_label.config(
            text=row["segment_id"]
        )

        self.metadata_label.config(
            text=(
                f"Recording: {row.get('recording_id', '')}\n"
                f"Speaker: {row.get('speaker_group_id', '')}\n"
                f"Split: {row.get('dataset_split', '')}\n"
                f"Duration: {row.get('duration_seconds', '')} seconds"
            )
        )

        self.transcription_text.delete(
            "1.0",
            tk.END,
        )
        self.transcription_text.insert(
            "1.0",
            row.get("manual_transcription", ""),
        )

        self.notes_text.delete(
            "1.0",
            tk.END,
        )
        self.notes_text.insert(
            "1.0",
            row.get("uncertainty_notes", ""),
        )

        self.status_var.set(
            row.get(
                "transcription_status",
                "not_started",
            )
            or "not_started"
        )

        self.segment_start_time = time.time()
        self.message_label.config(text="")

        self.transcription_text.focus_set()

    def play_audio(self) -> None:
        audio_path = self.get_audio_path()

        if not audio_path.exists():
            messagebox.showerror(
                "Audio not found",
                str(audio_path),
            )
            return

        try:
            if sys.platform == "darwin":
                subprocess.Popen(
                    ["afplay", str(audio_path)]
                )
            elif sys.platform.startswith("win"):
                import os

                os.startfile(audio_path)  # type: ignore[attr-defined]
            else:
                subprocess.Popen(
                    ["aplay", str(audio_path)]
                )

        except Exception as error:
            messagebox.showerror(
                "Playback error",
                str(error),
            )

    def save_csv(self) -> None:
        fieldnames = list(self.rows[0].keys())

        with CSV_PATH.open(
            "w",
            encoding="utf-8",
            newline="",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames,
            )
            writer.writeheader()
            writer.writerows(self.rows)

    def save_current(self) -> None:
        row = self.rows[self.current_index]

        row["manual_transcription"] = (
            self.transcription_text
            .get("1.0", tk.END)
            .strip()
        )

        row["uncertainty_notes"] = (
            self.notes_text
            .get("1.0", tk.END)
            .strip()
        )

        row["transcription_status"] = (
            self.status_var.get()
        )

        elapsed = int(
            time.time() - self.segment_start_time
        )

        previous_time = row.get(
            "transcription_time_seconds",
            "0",
        )

        try:
            previous_seconds = int(
                float(previous_time or 0)
            )
        except ValueError:
            previous_seconds = 0

        row["transcription_time_seconds"] = str(
            previous_seconds + elapsed
        )

        self.save_csv()
        self.segment_start_time = time.time()

        self.message_label.config(
            text="Saved successfully."
        )

    def next_segment(self) -> None:
        self.save_current()

        if self.current_index < len(self.rows) - 1:
            self.current_index += 1
            self.load_segment()
        else:
            messagebox.showinfo(
                "Finished",
                "You reached the final pilot segment.",
            )

    def previous_segment(self) -> None:
        self.save_current()

        if self.current_index > 0:
            self.current_index -= 1
            self.load_segment()

    def close_app(self) -> None:
        self.save_current()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()

    try:
        TranscriptionApp(root)
    except Exception as error:
        messagebox.showerror(
            "Application error",
            str(error),
        )
        root.destroy()
        return

    root.mainloop()


if __name__ == "__main__":
    main()