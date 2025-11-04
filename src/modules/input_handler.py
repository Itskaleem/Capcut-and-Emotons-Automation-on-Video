"""
Input Handler Module
Handles downloading from YouTube or processing local files
"""

import os
import subprocess
import glob
from pathlib import Path
from typing import Tuple, Optional
from yt_dlp import YoutubeDL
from src.config import Config
from src.utils.logger import logger


class InputHandler:
    """Handles various input sources: YouTube, local video, local audio"""
    
    @staticmethod
    def process_input(source: str) -> Tuple[Optional[str], str, str]:
        """
        Process input source and return video_path, audio_path, title
        
        Args:
            source: YouTube URL, video path, or audio path
            
        Returns:
            Tuple of (video_path, audio_path, title)
        """
        logger.info(f"Processing input source: {source[:50]}...")
        
        if Config.is_youtube_url(source):
            return InputHandler._handle_youtube(source)
        elif Config.is_video_file(source):
            return InputHandler._handle_video_file(source)
        elif Config.is_audio_file(source):
            return InputHandler._handle_audio_file(source)
        else:
            raise ValueError(f"Unsupported input source: {source}")
    
    @staticmethod
    def _handle_youtube(url: str) -> Tuple[Optional[str], str, str]:
        """Download and process YouTube video"""
        logger.info("Downloading from YouTube...", "📥")
        
        if Config.DOWNLOAD_VIDEO:
            return InputHandler._download_youtube_video(url)
        else:
            return InputHandler._download_youtube_audio(url)
    
    @staticmethod
    def _download_youtube_video(url: str) -> Tuple[str, str, str]:
        """Download YouTube video with audio"""
        ydl_opts = {
            "format": f"best[height<={Config.MAX_VIDEO_HEIGHT}]/best",
            "outtmpl": "%(title)s.%(ext)s",
            "skip_download": False,
            "quiet": not Config.VERBOSE_LOGGING,
            "ignoreerrors": True,
        }
        
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get("title")
                ext = info.get("ext", "mp4")
                video_file = f"{title}.{ext}"
                
                # Handle special characters in filename
                if not os.path.exists(video_file):
                    logger.warning(f"Filename mismatch, searching for downloaded file...")
                    possible_files = glob.glob("*.mp4")
                    if possible_files:
                        video_file = possible_files[0]
                        title = os.path.splitext(video_file)[0]
                        logger.success(f"Found video: {video_file}")
                
                # Extract audio
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                audio_file = f"{safe_title}.mp3"
                
                logger.info("Extracting audio for transcription...", "🎵")
                subprocess.run([
                    "ffmpeg", "-y", "-i", video_file,
                    "-q:a", "0", "-map", "a", audio_file
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                
                logger.success(f"Audio extracted: {audio_file}")
                return video_file, audio_file, title
                
        except Exception as e:
            logger.error(f"YouTube download failed: {e}")
            # Try to recover partial downloads
            mp4_files = glob.glob("*.mp4")
            if mp4_files:
                logger.warning("Found partial download, attempting to continue...")
                video_file = mp4_files[0]
                title = os.path.splitext(video_file)[0]
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                audio_file = f"{safe_title}.mp3"
                
                try:
                    subprocess.run([
                        "ffmpeg", "-y", "-i", video_file,
                        "-q:a", "0", "-map", "a", audio_file
                    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                    return video_file, audio_file, title
                except:
                    raise Exception("Failed to extract audio from partial download")
            raise
    
    @staticmethod
    def _download_youtube_audio(url: str) -> Tuple[None, str, str]:
        """Download only YouTube audio"""
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "%(title)s.%(ext)s",
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}],
            "quiet": not Config.VERBOSE_LOGGING,
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title")
            audio_file = f"{title}.mp3"
            
            logger.success(f"Audio downloaded: {audio_file}")
            return None, audio_file, title
    
    @staticmethod
    def _handle_video_file(video_path: str) -> Tuple[str, str, str]:
        """Process local video file"""
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        logger.info(f"Processing local video: {video_path}", "🎬")
        
        title = Path(video_path).stem
        audio_file = f"{title}.mp3"
        
        # Extract audio
        logger.info("Extracting audio...", "🎵")
        subprocess.run([
            "ffmpeg", "-y", "-i", video_path,
            "-q:a", "0", "-map", "a", audio_file
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        
        logger.success(f"Audio extracted: {audio_file}")
        return video_path, audio_file, title
    
    @staticmethod
    def _handle_audio_file(audio_path: str) -> Tuple[None, str, str]:
        """Process local audio file"""
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        logger.info(f"Processing local audio: {audio_path}", "🎵")
        
        title = Path(audio_path).stem
        return None, audio_path, title
    
    @staticmethod
    def prepare_audio_for_transcription(audio_file: str, output_wav: str = "temp.wav"):
        """Convert audio to 16kHz mono WAV for Vosk"""
        logger.info("Preparing audio for transcription...", "🔧")
        
        subprocess.run([
            "ffmpeg", "-y", "-i", audio_file,
            "-ar", str(Config.SAMPLE_RATE),
            "-ac", "1", output_wav
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        
        logger.success(f"Audio prepared: {output_wav}")
        return output_wav
