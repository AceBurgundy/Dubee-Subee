from datetime import datetime, timedelta
import re
import os
from typing import List


class Subtitle:
    """
    Represents a single subtitle entry in an SRT file.
    """

    def __init__(self, index: int, start: str, end: str, text: str):
        self.index: int = index
        self.start: str = start
        self.end: str = end
        self.text: str = text.strip()

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Subtitle) and self.start == other.start and self.end == other.end

    def __hash__(self) -> int:
        return hash((self.start, self.end))

    def __str__(self) -> str:
        return f"{self.index}\n{self.start} --> {self.end}\n{self.text}\n"

    def start_ms(self) -> int:
        return self.time_to_ms(self.start)

    def end_ms(self) -> int:
        return self.time_to_ms(self.end)

    @staticmethod
    def time_to_ms(time_str: str) -> int:
        try:
            time = datetime.strptime(time_str.strip(), "%H:%M:%S,%f")
        except ValueError:
            raise ValueError(f"Invalid timestamp format: {time_str}")
        delta = timedelta(
            hours=time.hour, minutes=time.minute, seconds=time.second, microseconds=time.microsecond
        )
        return int(delta.total_seconds() * 1000)


def remove_html_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)


def parse_subtitles(content: str) -> List[Subtitle]:
    """
    Parses raw subtitle file content into a list of Subtitle objects.
    """
    entries = re.split(r"\n\s*\n", content.strip())
    subtitles: List[Subtitle] = []

    for entry in entries:
        lines = entry.strip().splitlines()
        if len(lines) < 2:
            continue

        try:
            index = int(lines[0].strip())
        except ValueError:
            continue  # Skip blocks without a valid index

        timing_match = re.match(r"(.+?)\s*-->\s*(.+)", lines[1])
        if not timing_match:
            continue  # Skip if timing line is malformed

        start = timing_match.group(1).strip()
        end = timing_match.group(2).strip()
        text = "\n".join(lines[2:]).strip()
        cleaned_text = remove_html_tags(text)
        subtitles.append(Subtitle(index, start, end, cleaned_text))

    return subtitles


def save_file(content: str, output_path: str) -> None:
    """
    Saves the given content to a file at the specified path.

    Parameters:
    -----------
    content : str
        The string content to write.
    output_path : str
        The full path to the output file.
    """
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(content)
    print(f"File saved: {output_path}")


def flatten_subtitle(filepath: str) -> None:
    """
    Converts a subtitle file into a single plain text string and writes to a new .txt file.

    Parameters:
    -----------
    filepath : str
        Path to the original subtitle file.
    """
    with open(filepath, "r", encoding="utf-8-sig") as file:
        content = file.read()

    subtitles = parse_subtitles(content)
    plain_text = ' '.join(sub.text for sub in subtitles if sub.text).strip()
    cleaned_text = re.sub(r"[\r\n\t]+", " ", plain_text).strip()
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()   # collapse and trim extra spaces
    
    dir_name, base_name = os.path.split(filepath)
    name, _ = os.path.splitext(base_name)
    output_path = os.path.join(dir_name, f"{name} - plain.txt")

    save_file(cleaned_text + "\n", output_path)


def clean_subtitle_file(filepath: str) -> None:
    """
    Cleans and merges subtitle entries from an SRT file and writes the result to a new SRT file.

    Parameters:
    -----------
    filepath : str
        Path to the original subtitle file.
    """
    with open(filepath, "r", encoding="utf-8-sig") as file:
        content = file.read()

    subtitles = parse_subtitles(content)
    if not subtitles:
        print("No valid subtitles found.")
        return

    for subtitle in subtitles:
        subtitle.text = remove_html_tags(subtitle.text)
        subtitle.text = re.sub(r"\s+", " ", subtitle.text).strip()

    merged_subtitles: List[Subtitle] = []
    buffer = subtitles[0]

    for current in subtitles[1:]:
        same_text = current.text == buffer.text
        gap = current.start_ms() - buffer.end_ms()

        if same_text and 0 <= gap <= 100:
            buffer.end = current.end
        elif same_text and buffer.end_ms() >= current.start_ms():
            buffer.end = max(buffer.end, current.end, key=Subtitle.time_to_ms)
        else:
            merged_subtitles.append(buffer)
            buffer = current

    merged_subtitles.append(buffer)
    cleaned_content = "\n".join(str(sub) for sub in merged_subtitles)

    dir_name, base_name = os.path.split(filepath)
    name, ext = os.path.splitext(base_name)
    new_path = os.path.join(dir_name, f"{name} - clean{ext}")

    save_file(cleaned_content, new_path)
