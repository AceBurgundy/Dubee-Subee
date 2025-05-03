from PIL import Image # type: ignore
from typing import List, Optional
import ffmpeg # type: ignore
import subprocess
import io


class FfmpegUtilities:
    """`
    Utility class for ffmpeg operations to inspect and manipulate audio and subtitle streams in video files.
    """

    @staticmethod
    def get_audio_streams(filepath: str) -> List[str]:
        """
        Retrieves all audio stream information from a video file.

        Parameters
        ----------
        filepath (str): Path to the video file.

        Usage
        -----
        FfmpegUtilities.get_audio_streams("video.mkv")

        Returns
        -------
        List[str]
            List of audio stream descriptions, each formatted as "stream_index=INDEX | language=LANG | title=TITLE".
        """
        probe = ffmpeg.probe(filepath)
        audio_streams = []

        for stream in probe['streams']:
            if stream['codec_type'] == 'audio':
                tags = stream.get('tags', {})
                lang = tags.get('language', 'unknown')
                title = tags.get('title', '')
                desc = f"stream_index={stream['index']} | language={lang} | title={title}"
                audio_streams.append(desc)

        return audio_streams

    @staticmethod
    def get_subtitle_streams(filepath: str) -> List[str]:
        """
        Retrieves all subtitle stream information from a video file.

        Parameters
        ----------
        filepath (str): Path to the video file.

        Usage
        -----
        FfmpegUtilities.get_subtitle_streams("video.mkv")

        Returns
        -------
        List[str]
            List of subtitle stream descriptions, each formatted as "stream_index=INDEX | language=LANG | title=TITLE".
        """
        probe = ffmpeg.probe(filepath)
        subtitle_streams = []

        for stream in probe['streams']:
            if stream['codec_type'] == 'subtitle':
                tags = stream.get('tags', {})
                lang = tags.get('language', 'unknown')
                title = tags.get('title', '')
                desc = f"stream_index={stream['index']} | language={lang} | title={title}"
                subtitle_streams.append(desc)

        return subtitle_streams

    @staticmethod
    def remove_audio_streams(filepath: str, output_path: str, audio_streams_to_remove: List[str]) -> bool:
        """
        Removes specific audio streams from a video file.

        Parameters
        ----------
        filepath (str): Path to the original video file.
        output_path (str): Path where the processed file will be saved.
        audio_streams_to_remove (List[str]): List of audio stream descriptions from `get_audio_streams()` to remove.

        Usage
        -----
        FfmpegUtilities.remove_audio_streams("input.mkv", "output.mkv", audio_list)

        Returns
        -------
        bool
            True if the operation was successful, False otherwise.
        """
        return FfmpegUtilities._remove_streams_by_index(
            filepath, output_path, audio_streams_to_remove
        )

    @staticmethod
    def remove_subtitle_streams(filepath: str, output_path: str, subtitle_streams_to_remove: List[str]) -> bool:
        """
        Removes specific subtitle streams from a video file.

        Parameters
        ----------
        filepath (str): Path to the original video file.
        output_path (str): Path where the processed file will be saved.
        subtitle_streams_to_remove (List[str]): List of subtitle stream descriptions from `get_subtitle_streams()` to remove.

        Usage
        -----
        FfmpegUtilities.remove_subtitle_streams("input.mkv", "output.mkv", subtitle_list)

        Returns
        -------
        bool
            True if the operation was successful, False otherwise.
        """
        return FfmpegUtilities._remove_streams_by_index(
            filepath, output_path, subtitle_streams_to_remove
        )

    @staticmethod
    def _remove_streams_by_index(filepath: str, output_path: str, streams_to_remove: List[str]) -> bool:
        """
        Internal helper to remove specified stream indices from a video file.

        Parameters
        ----------
        filepath (str): Path to the original video file.
        output_path (str): Path where the processed file will be saved.
        streams_to_remove (List[str]): List of stream descriptions including "stream_index=...".

        Returns
        -------
        bool
            True if the removal succeeded, False otherwise.
        """
        try:
            remove_indices = set()
            for stream in streams_to_remove:
                if stream.startswith("stream_index="):
                    index_str = stream.split('=')[1].split('|')[0].strip()
                    remove_indices.add(int(index_str))

            probe = ffmpeg.probe(filepath)
            all_streams = probe['streams']

            map_options = []
            for stream in all_streams:
                index = int(stream['index'])  # type: ignore
                if index not in remove_indices:
                    map_options.extend(['-map', f'0:{index}'])

            command = ['ffmpeg', '-i', filepath] + map_options + ['-c', 'copy', output_path]
            subprocess.run(command, check=True)
            return True
        except Exception as error:
            print(f"Error during stream removal: {error}")
            return False

    @staticmethod
    def get_video_thumbnail(filepath: str, time_seconds: int = 1) -> Optional[Image.Image]:
        """
        Extracts a thumbnail image from the video at a given timestamp.

        Parameters
        ----------
        filepath (str): Path to the video file.
        time_seconds (int): Timestamp in seconds to grab the thumbnail (default is 1).

        Usage
        -----
        thumbnail = FfmpegUtilities.get_video_thumbnail("video.mkv")

        Returns
        -------
        Image.Image
            A PIL Image object that can be passed directly to customtkinter.CTkImage.
        """
        try:
            out, _ = (
                ffmpeg
                .input(filepath, ss=time_seconds)
                .output('pipe:', vframes=1, format='image2', vcodec='mjpeg')
                .run(capture_stdout=True, capture_stderr=True)
            )
        
            return Image.open(
                io.BytesIO(out)
            )
        
        except Exception as error:
            print(f"Failed to generate thumbnail: {error}")
            return None