"""
Video Processing Pipeline
Main entry point for the application
"""

import os
import sys
from src.config import Config
from src.utils.logger import logger
from src.modules.input_handler import InputHandler
from src.modules.transcriber import Transcriber
from src.modules.caption_generator import CaptionGenerator
from src.modules.capcut_generator import CapCutProjectGenerator
from src.modules.video_renderer import VideoRenderer


class VideoPipeline:
    """Main video processing pipeline"""
    
    def __init__(self):
        self.input_handler = InputHandler()
        self.transcriber = Transcriber()
        self.caption_generator = CaptionGenerator()
        self.temp_files = []
    
    def process(self, source: str = None):
        """
        Run the complete pipeline
        
        Args:
            source: Input source (URL or file path). If None, uses CONFIG.INPUT_SOURCE
        """
        try:
            # Use source from parameter or config
            source = source or Config.INPUT_SOURCE
            
            if not source:
                raise ValueError("No input source provided. Set INPUT_SOURCE in .env file")
            
            logger.section("🚀 Starting Video Processing Pipeline")
            
            # Step 1: Process input
            logger.step(1, "Processing Input Source")
            video_file, audio_file, title = self.input_handler.process_input(source)
            
            # Step 2: Prepare audio for transcription
            logger.step(2, "Preparing Audio for Transcription")
            wav_file = self.input_handler.prepare_audio_for_transcription(audio_file)
            self.temp_files.append(wav_file)
            
            # Step 3: Transcribe audio
            logger.step(3, "Transcribing Audio")
            asr_words = self.transcriber.transcribe(wav_file)
            
            if not asr_words:
                raise Exception("Transcription failed - no words detected")
            
            # Step 4: Generate captions
            logger.step(4, "Generating Semantic Captions & Classifying Emotions")
            captions = self.caption_generator.generate(asr_words)
            
            if not captions:
                raise Exception("Caption generation failed")
            
            # Step 5: Create CapCut project
            logger.step(5, "Creating CapCut Project")
            project_path = CapCutProjectGenerator.create_project(
                video_file, audio_file, captions, title
            )
            
            # Step 6: Render final video
            logger.step(6, "Rendering Final Video with Overlays")
            output_path = Config.get_output_path()
            
            # Load from CapCut project to ensure consistency
            audio_path, video_path, project_captions = CapCutProjectGenerator.load_latest_project()
            
            VideoRenderer.render(audio_path, video_path, project_captions, output_path)
            
            # Cleanup
            self._cleanup()
            
            # Summary
            logger.section("✨ Pipeline Completed Successfully!")
            logger.success(f"Final video: {output_path}")
            logger.success(f"CapCut project: {project_path}")
            logger.info(f"Total captions: {len(captions)}")
            logger.info(f"Video duration: {captions[-1]['end']:.1f}s")
            logger.info(f"Emotion types detected: {len(set(c['emotion'] for c in captions))}")
            
            return output_path, project_path
            
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            self._cleanup()
            raise
    
    def _cleanup(self):
        """Clean up temporary files"""
        if not Config.KEEP_INTERMEDIATE_FILES:
            for temp_file in self.temp_files:
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                        logger.debug(f"Cleaned up: {temp_file}")
                    except:
                        pass


def main():
    """Main entry point"""
    try:
        # Ensure directories exist
        Config.ensure_directories()
        
        # Validate configuration
        Config.validate()
        
        # Run pipeline
        pipeline = VideoPipeline()
        pipeline.process()
        
    except KeyboardInterrupt:
        logger.warning("\nProcess interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
