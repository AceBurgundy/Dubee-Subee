from PIL import Image # type: ignore
from typing import List, Optional
from datetime import datetime   
import ffmpeg # type: ignore
import subprocess
import io
import os
class FFmpegUtilities:
    """
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
        FFmpegUtilities.get_audio_streams("video.mkv")

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
        FFmpegUtilities.get_subtitle_streams("video.mkv")

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
        FFmpegUtilities.remove_audio_streams("input.mkv", "output.mkv", audio_list)

        Returns
        -------
        bool
            True if the operation was successful, False otherwise.
        """
        return FFmpegUtilities._remove_streams_by_index(
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
        FFmpegUtilities.remove_subtitle_streams("input.mkv", "output.mkv", subtitle_list)

        Returns
        -------
        bool
            True if the operation was successful, False otherwise.
        """
        return FFmpegUtilities._remove_streams_by_index(
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
        thumbnail = FFmpegUtilities.get_video_thumbnail("video.mkv")

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
        
    @staticmethod
    def get_video_duration(video_path: str) -> float:
        """
        Get the total duration of a video in seconds.

        Parameters:
            video_path (str): Path to the video file.

        Returns:
            float: Duration of the video in seconds.
        """
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', video_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        return float(result.stdout.decode().strip())

    @staticmethod
    def trim_video(
        video_path: str,
        start_hour: int = 0,
        start_minute: int = 0,
        start_second: int = 0,
        start_milliseconds: int = 0,
        end_hour: Optional[int] = None,
        end_minute: Optional[int] = None,
        end_second: Optional[int] = None,
        end_milliseconds: Optional[int] = None
    ) -> Optional[str]:
        """
        Trims a video using FFmpeg from a specified start time to end time.

        If no start time is provided, trimming starts from the beginning of the video.
        At least one end time component must be provided. If the computed end time
        exceeds the video duration, an error is raised.

        Parameters:
            video_path (str): Path to the input video file.
            start_hour (int): Start hour. Defaults to 0.
            start_minute (int): Start minute. Defaults to 0.
            start_second (int): Start second. Defaults to 0.
            start_milliseconds (int): Start milliseconds. Defaults to 0.
            end_hour (int, optional): End hour. Required if no other end argument is provided.
            end_minute (int, optional): End minute.
            end_second (int, optional): End second.
            end_milliseconds (int, optional): End milliseconds.

        Usage:
            trimmed = trim_video_ffmpeg("video.mp4", start_minute=1, end_minute=2)

        Returns:
            Optional[str]: Path to the trimmed video file, or None if trimming failed.
        """
        if all(v is None for v in [end_hour, end_minute, end_second, end_milliseconds]):
            raise ValueError("At least one end time argument must be provided.")

        start = (
            (start_hour or 0) * 3600 +
            (start_minute or 0) * 60 +
            (start_second or 0) +
            (start_milliseconds or 0) / 1000.0
        )

        end = (
            (end_hour or 0) * 3600 +
            (end_minute or 0) * 60 +
            (end_second or 0) +
            (end_milliseconds or 0) / 1000.0
        )

        duration = FFmpegUtilities.get_video_duration(video_path)
        if end > duration:
            raise ValueError(f"End time ({end}s) exceeds video duration ({duration}s).")

        clip_duration = end - start
        base, extension = os.path.splitext(video_path)
        timestamp = datetime.now().strftime("%I-%M%p").lower()
        output_path = f"{base} - trimmed {timestamp}{extension}"

        try:
            ffmpeg.input(video_path, ss=start)\
                .output(output_path, t=clip_duration, c='copy')\
                .run(overwrite_output=True)
            print(f"Trimmed video saved to: {output_path}")
            return output_path
        
        except Exception as error:
            print(f"Failed to trim video: {error}")
            return None

    @staticmethod
    def add_subtitles_to_video(video_path: str, subtitle_paths: List[str]) -> Optional[str]:
        """
        Adds one or more subtitle files as subtitle streams to a video file.

        Parameters
        ----------
        video_path : str
            Path to the input video file.
        subtitle_paths : List[str]
            List of paths to subtitle files to add.

        Returns
        -------
        Optional[str]
            Path to the new video file with subtitles added, or None if failed.
        """
        if not subtitle_paths:
            print("No subtitle files provided.")
            return None

        # Prepare output path: same folder, same base name + "_with_subs" + same extension
        base, extension = os.path.splitext(video_path)
        output_path = f"{base} with_subtitles {extension}"

        try:
            # Start building input streams: first the video
            input_streams = [ffmpeg.input(video_path)]
            
            # Add each subtitle as input
            for sub_path in subtitle_paths:
                input_streams.append(ffmpeg.input(sub_path))

            # Build the output stream with mapping
            # Map all streams from video (index 0) and map all subtitles from subtitle inputs
            # For the subtitles, their inputs start at 1, 2, 3,... indexes accordingly
            # Use -c copy for video and audio, -c:s mov_text for subtitles if mp4, or copy if mkv

            # Determine codec for subtitles based on container extension
            ext_lower = extension.lower()
            if ext_lower in ['.mp4', '.mov', '.m4v']:
                subtitle_codec = 'mov_text'
            else:
                subtitle_codec = 'copy'

            # Prepare ffmpeg output with maps
            # Map video and audio streams from input 0
            map_options = ['-map', '0:v', '-map', '0:a?']  # audio is optional
            # Map subtitle streams from each subtitle input (inputs 1, 2, ...)
            for i in range(1, len(input_streams)):
                map_options.extend(['-map', f'{i}:0'])

            # Set codec copy for video and audio, codec for subtitles
            # Build codec options
            codec_options = ['-c:v', 'copy', '-c:a', 'copy', '-c:s', subtitle_codec]

            # Run ffmpeg
            (
                ffmpeg
                .concat(*input_streams, v=1, a=1, n=len(input_streams))  # concat is tricky here; better not use it
            )

            # Instead of concat, run with inputs and output with maps directly:
            process = (
                ffmpeg
                .input(video_path)
            )

            # Since ffmpeg-python does not have a straightforward way to add multiple inputs and map them,
            # we will build the command manually and run subprocess.

            # Build ffmpeg command manually:
            cmd = ['ffmpeg', '-y', '-i', video_path]
            for sub_path in subtitle_paths:
                cmd.extend(['-i', sub_path])

            # Map video and audio from first input
            cmd.extend(['-map', '0:v', '-map', '0:a?'])

            # Map subtitles from subtitle inputs
            for i in range(len(subtitle_paths)):
                cmd.extend(['-map', f'{i+1}:0'])

            # Set codec for streams
            cmd.extend(['-c:v', 'copy', '-c:a', 'copy', '-c:s', subtitle_codec])

            cmd.append(output_path)

            subprocess.run(cmd, check=True)

            print(f"Subtitles added. Output saved to: {output_path}")
            return output_path

        except Exception as error:
            print(f"Failed to add subtitles: {error}")
            return None
        
    @staticmethod
    def extract_audio(video_path: str) -> Optional[str]:
        """
        Extracts the audio from a video file and saves it as an audio file in the same directory.

        Parameters
        ----------
        video_path : str
            Path to the input video file.

        The audio is saved with the same filename but with an audio extension (.m4a).
        
        Returns
        -------
        Optional[str]
            Path to the saved audio file or None if error has been caught.
        """
        base, _ = os.path.splitext(video_path)
        output_path = f"{base}.mp3"

        try:
            (
                ffmpeg
                .input(video_path)
                .output(output_path, acodec='libmp3lame', vn=None)
                .run(overwrite_output=True)
            )
            print(f"Audio extracted and saved to: {output_path}")
            return output_path
        except Exception as error:
            print(f"Failed to extract audio: {error}")
            return None

    @staticmethod
    def replace_audio(video_path: str, new_audio_path: str) -> Optional[str]:
        """
        Replaces the audio in a video with a new audio file.

        Parameters
        ----------
        video_path : str
            Path to the input video file.

        new_audio_path : str
            Path to the new audio file to be used.

        Returns
        -------
        Optional[str]
            Path to the video with the new audio, or None if replacement failed.
        """
        base, extension = os.path.splitext(video_path)
        output_path = f"{base} - replaced audio{extension}"

        try:
            cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-i', new_audio_path,
                '-c:v', 'copy',
                '-map', '0:v:0',
                '-map', '1:a:0',
                '-shortest',
                output_path
            ]
            subprocess.run(cmd, check=True)
            print(f"Audio replaced successfully. Saved to: {output_path}")
            return output_path
        except subprocess.CalledProcessError as error:
            print(f"Failed to replace audio: {error}")
            return None
