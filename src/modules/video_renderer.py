"""
Video Renderer Module
Renders final video with subtitles and emotion icons
"""

import os
from moviepy.editor import (
    AudioFileClip, VideoFileClip, ColorClip,
    TextClip, ImageClip, CompositeVideoClip
)
from moviepy.video.fx.all import fadein, fadeout
from PIL import Image
from src.config import Config
from src.utils.logger import logger

# Fix PIL compatibility
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS


class VideoRenderer:
    """Renders final video with overlays"""
    
    @staticmethod
    def render(audio_path: str, video_path: str, captions: list, output_path: str):
        """
        Render final video with subtitles and emotions
        
        Args:
            audio_path: Path to audio file (used for transcription reference)
            video_path: Path to video file (or None for background)
            captions: List of caption dictionaries
            output_path: Output video path
        """
        logger.info("Starting video rendering...", "🎬")
        
        # Create base clip
        if video_path and os.path.exists(video_path):
            logger.info(f"Using original video: {os.path.basename(video_path)}")
            base = VideoFileClip(video_path)
            
            # Use the original video's audio to preserve sync
            if base.audio is not None:
                logger.info("Using original video's audio track (preserving sync)")
                duration = base.duration
            else:
                # No audio in video, use extracted audio
                logger.warning("No audio in video, using extracted audio file")
                audio = AudioFileClip(audio_path)
                duration = audio.duration
                base = base.set_audio(audio)
                
                if base.duration > duration:
                    base = base.subclip(0, duration)
                elif base.duration < duration:
                    logger.warning(f"Video ({base.duration:.1f}s) shorter than audio ({duration:.1f}s)")
                    duration = base.duration
                    audio = audio.subclip(0, duration)
            
            W, H = base.w, base.h
            logger.info(f"Video dimensions: {W}x{H}")
        else:
            logger.info("Using colored background")
            audio = AudioFileClip(audio_path)
            duration = audio.duration
            W, H = Config.VIDEO_WIDTH, Config.VIDEO_HEIGHT
            base = ColorClip(size=(W, H), color=Config.BACKGROUND_COLOR, duration=duration)
            base = base.set_audio(audio)
        
        # Create overlays
        overlays = VideoRenderer._create_overlays(captions, W, H, video_path is not None)
        
        # Composite
        final = CompositeVideoClip([base, *overlays], size=base.size)
        final = final.set_duration(duration)
        
        # Render
        logger.info(f"Writing video to: {output_path}", "🎥")
        final.write_videofile(
            output_path,
            fps=Config.OUTPUT_FPS,
            codec=Config.VIDEO_CODEC,
            audio_codec=Config.AUDIO_CODEC,
            threads=Config.THREADS
        )
        
        logger.success(f"Video rendered successfully: {output_path}")
    
    @staticmethod
    def _create_overlays(captions: list, width: int, height: int, has_video: bool) -> list:
        """Create subtitle and emotion icon overlays"""
        overlays = []
        
        # Calculate dynamic icon size based on video height
        # Use percentage of height for responsive sizing
        icon_size = int(height * Config.ICON_SIZE_RATIO)
        logger.info(f"Icon size calculated: {icon_size}px ({Config.ICON_SIZE_RATIO*100:.0f}% of {height}px height)")
        
        icon_count = 0
        for i, cap in enumerate(captions):
            # Calculate positions
            if has_video:
                subtitle_y = height - 120 - (i % 2) * 60
                # Place icons on the LEFT side of video, vertically centered with subtitle
                icon_x = 30
            else:
                subtitle_y = height - 100 - (i % 3) * 80
                icon_x = 30
            
            # Create subtitle
            sub = VideoRenderer._make_subtitle(
                cap["text"], cap["start"], cap["end"],
                subtitle_y, has_video
            )
            overlays.append(sub)
            
            # Create emotion icon
            emotion = cap.get("emotion", "neutral")
            icon_path = VideoRenderer._get_emotion_icon(emotion)
            
            if icon_path and os.path.exists(icon_path):
                try:
                    # Position icon vertically aligned with subtitle top
                    icon_y = subtitle_y - 10
                    
                    icon = (ImageClip(icon_path)
                           .set_start(cap["start"])
                           .set_duration(min(3.0, cap["end"] - cap["start"]))
                           .resize(height=icon_size)
                           .set_position((icon_x, icon_y)))
                    overlays.append(icon)
                    icon_count += 1
                    
                    if emotion != "neutral":
                        logger.info(f"🎭 {cap['start']:.1f}s: {emotion.upper()} ({icon_size}px) - {cap['text'][:40]}...")
                        
                except Exception as e:
                    logger.error(f"Failed to add icon for {emotion}: {e}")
            elif emotion != "neutral":
                logger.warning(f"No icon found for emotion: {emotion}")
        
        logger.info(f"Added {icon_count} emotion icons to video")
        return overlays
    
    @staticmethod
    def _make_subtitle(text: str, start: float, end: float, y_pos: int, has_video: bool):
        """Create subtitle text clip"""
        txt = TextClip(text, font=Config.FONT_NAME, fontsize=Config.SUBTITLE_FONT_SIZE,
                      color="white", method="label")
        
        # Enhanced background for video
        if has_video:
            txt = txt.on_color(size=(txt.w + 40, txt.h + 20),
                              color=(0, 0, 0), col_opacity=Config.SUBTITLE_BACKGROUND_OPACITY)
        else:
            txt = txt.on_color(size=(txt.w + 20, txt.h + 12),
                              color=(0, 0, 0), col_opacity=0.6)
        
        txt = txt.set_position(("center", y_pos)).set_start(start).set_duration(end - start)
        txt = fadein(txt, 0.08)
        txt = fadeout(txt, 0.08)
        
        return txt
    
    @staticmethod
    def _get_emotion_icon(emotion: str):
        """Get icon path for emotion"""
        if not emotion or emotion == "neutral":
            return None
        
        icon_files = {
            "happy": ["happy.png", "happy.jpg"],
            "sad": ["sad.png", "sad.jpg"],
            "angry": ["angry.png", "angry.jpg"],
            "surprised": ["surprised.png", "surprised.jpg"],
            "laugh": ["laugh.png", "laugh.jpg"],
        }
        
        if emotion not in icon_files:
            return None
        
        for filename in icon_files[emotion]:
            icon_path = os.path.join(Config.ICONS_FOLDER, filename)
            if os.path.exists(icon_path):
                return icon_path
        
        return None
