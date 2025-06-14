import os
import datetime
from urllib.parse import urlparse, parse_qs
from typing import List
from youtube_transcript_api import YouTubeTranscriptApi  # type: ignore
from youtube_transcript_api.formatters import SRTFormatter  # type: ignore

def extract_transcript(
    url: str,
    languages: None | List[str],
    srt_folder_destination: str,
    plain_text: bool = False
) -> None:
    """
    Extracts the transcript of a YouTube video and saves it as an SRT file.

    Parameters
    ----------
    url (str): Full YouTube video URL.
    languages : Optional[Union[str, List[str]]]
        A list of language codes, in order of preference.
        If None, defaults to ['en'].
    srt_folder_destination (str):
        Directory where the SRT file will be saved.
    plain_text (bool):If True, saves plain text (no formatting/timestamps). Else, saves SRT.

    Returns
    -------
    None
    """
    try:
        # Parse the video ID
        parsed_url = urlparse(url)
        video_id = parse_qs(parsed_url.query).get("v", [None])[0]

        if not video_id:
            raise ValueError("Invalid YouTube URL: cannot extract video ID.")

        if languages is None:
            languages = ['en']
        elif isinstance(languages, str):
            languages = [languages]

        # Fetch transcript
        api_instance = YouTubeTranscriptApi()
        transcript = api_instance.fetch(video_id=video_id, languages=languages)
        os.makedirs(srt_folder_destination, exist_ok=True)

        # Prepare filename
        now = datetime.datetime.now()
        lang_code = transcript[0].get('language_code', languages[0]) if isinstance(transcript, list) and transcript else languages[0]
        filename = now.strftime(f"%d-%m-%Y %H%M {lang_code.upper()}")

        if plain_text:
            filename = ''.join([filename, ".txt"])
            file_path = os.path.join(srt_folder_destination, filename)

            # Extract and clean text
            text_only = " ".join(
                snippet.text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').strip()
                for snippet in transcript.snippets
            )

            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text_only)
        else:
            filename = ''.join([filename, ".srt"])
            file_path = os.path.join(srt_folder_destination, filename)

            # Save as SRT
            formatter = SRTFormatter()
            srt_text = formatter.format_transcript(transcript)
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(srt_text)

        print(f"Transcript saved to: {file_path}")
        return None

    except Exception as error:
        print(f"An error occurred: {error}")
        return None
    