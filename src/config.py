"""
Configuration Manager
Handles loading and validation of environment variables and configuration settings
"""

import os
from pathlib import Path
from typing import Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Central configuration class"""
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER', 'output')
    CAPCUT_PROJECTS_FOLDER = os.getenv('CAPCUT_PROJECTS_FOLDER', 'capcut_projects')
    ICONS_FOLDER = os.getenv('ICONS_FOLDER', 'icons')
    VOSK_MODEL_PATH = os.getenv('VOSK_MODEL_PATH', 'models/vosk-model-small-en-us-0.15')
    
    # Input
    INPUT_SOURCE = os.getenv('INPUT_SOURCE', '')
    FINAL_VIDEO_NAME = os.getenv('FINAL_VIDEO_NAME', 'final_output.mp4')
    
    # Video Processing
    DOWNLOAD_VIDEO = os.getenv('DOWNLOAD_VIDEO', 'true').lower() == 'true'
    MAX_VIDEO_HEIGHT = int(os.getenv('MAX_VIDEO_HEIGHT', '720'))
    OUTPUT_FPS = int(os.getenv('OUTPUT_FPS', '24'))
    VIDEO_CODEC = os.getenv('VIDEO_CODEC', 'libx264')
    AUDIO_CODEC = os.getenv('AUDIO_CODEC', 'aac')
    THREADS = int(os.getenv('THREADS', '4'))
    
    # Transcription
    SAMPLE_RATE = int(os.getenv('SAMPLE_RATE', '16000'))
    
    # Semantic Chunking
    ENABLE_SEMANTIC_CHUNKING = os.getenv('ENABLE_SEMANTIC_CHUNKING', 'true').lower() == 'true'
    SIMILARITY_THRESHOLD = float(os.getenv('SIMILARITY_THRESHOLD', '0.7'))
    MAX_SENTENCES_PER_CHUNK = int(os.getenv('MAX_SENTENCES_PER_CHUNK', '5'))
    MAX_PAUSE_GAP = float(os.getenv('MAX_PAUSE_GAP', '1.5'))
    MAX_WORDS_PER_SENTENCE = int(os.getenv('MAX_WORDS_PER_SENTENCE', '15'))
    
    # Emotion Classification
    ENABLE_ADVANCED_EMOTIONS = os.getenv('ENABLE_ADVANCED_EMOTIONS', 'true').lower() == 'true'
    EMOTION_MODEL = os.getenv('EMOTION_MODEL', 'j-hartmann/emotion-english-distilroberta-base')
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
    
    # Visual Settings
    VIDEO_WIDTH = int(os.getenv('VIDEO_WIDTH', '1280'))
    VIDEO_HEIGHT = int(os.getenv('VIDEO_HEIGHT', '720'))
    BACKGROUND_COLOR = tuple(map(int, os.getenv('BACKGROUND_COLOR', '20,20,20').split(',')))
    FONT_NAME = os.getenv('FONT_NAME', 'Arial')
    SUBTITLE_FONT_SIZE = int(os.getenv('SUBTITLE_FONT_SIZE', '36'))
    # Icon size as ratio of video height (0.12 = 12% of height)
    ICON_SIZE_RATIO = float(os.getenv('ICON_SIZE_RATIO', '0.12'))
    ICON_POSITION_X = int(os.getenv('ICON_POSITION_X', '50'))
    SUBTITLE_BACKGROUND_OPACITY = float(os.getenv('SUBTITLE_BACKGROUND_OPACITY', '0.8'))
    
    # Advanced
    KEEP_INTERMEDIATE_FILES = os.getenv('KEEP_INTERMEDIATE_FILES', 'false').lower() == 'true'
    VERBOSE_LOGGING = os.getenv('VERBOSE_LOGGING', 'true').lower() == 'true'
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        os.makedirs(cls.OUTPUT_FOLDER, exist_ok=True)
        os.makedirs(cls.CAPCUT_PROJECTS_FOLDER, exist_ok=True)
        os.makedirs(cls.ICONS_FOLDER, exist_ok=True)
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        errors = []
        
        if not cls.INPUT_SOURCE:
            errors.append("INPUT_SOURCE is required in .env file")
        
        if not os.path.exists(cls.VOSK_MODEL_PATH):
            errors.append(f"Vosk model not found at: {cls.VOSK_MODEL_PATH}")
        
        if not os.path.exists(cls.ICONS_FOLDER):
            errors.append(f"Icons folder not found at: {cls.ICONS_FOLDER}")
        
        if errors:
            raise ValueError("\n".join(["Configuration Errors:"] + errors))
        
        return True
    
    @classmethod
    def is_youtube_url(cls, source: str) -> bool:
        """Check if source is a YouTube URL"""
        return 'youtube.com' in source or 'youtu.be' in source
    
    @classmethod
    def is_video_file(cls, source: str) -> bool:
        """Check if source is a video file"""
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']
        return any(source.lower().endswith(ext) for ext in video_extensions)
    
    @classmethod
    def is_audio_file(cls, source: str) -> bool:
        """Check if source is an audio file"""
        audio_extensions = ['.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac']
        return any(source.lower().endswith(ext) for ext in audio_extensions)
    
    @classmethod
    def get_output_path(cls) -> str:
        """Get full output video path"""
        return os.path.join(cls.OUTPUT_FOLDER, cls.FINAL_VIDEO_NAME)
