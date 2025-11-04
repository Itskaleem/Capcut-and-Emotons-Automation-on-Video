"""
CapCut Project Generator Module
Creates CapCut-compatible project folders
"""

import os
import json
import shutil
import uuid
from typing import List, Dict, Optional
from src.config import Config
from src.utils.logger import logger


class CapCutProjectGenerator:
    """Generates CapCut project folders"""
    
    @staticmethod
    def create_project(
        video_file: Optional[str],
        audio_file: str,
        captions: List[Dict],
        title: str
    ) -> str:
        """
        Create CapCut project folder structure
        
        Args:
            video_file: Path to video file (optional)
            audio_file: Path to audio file
            captions: List of caption dictionaries
            title: Project title
            
        Returns:
            Path to created project folder
        """
        logger.info("Creating CapCut project...", "📁")
        
        # Create project structure
        project_id = str(uuid.uuid4()).upper()
        project_path = os.path.join(Config.CAPCUT_PROJECTS_FOLDER, project_id)
        import_path = os.path.join(project_path, "material", "import")
        os.makedirs(import_path, exist_ok=True)
        
        # Copy files
        shutil.copy(audio_file, import_path)
        logger.debug(f"Audio copied: {os.path.basename(audio_file)}")
        
        project_data = {
            "project_id": project_id,
            "project_name": title,
            "audio": os.path.join("material", "import", os.path.basename(audio_file)),
        }
        
        if video_file and os.path.exists(video_file):
            shutil.copy(video_file, import_path)
            project_data["video"] = os.path.join("material", "import", os.path.basename(video_file))
            logger.debug(f"Video copied: {os.path.basename(video_file)}")
        else:
            project_data["video"] = None
            logger.debug("No video file - will use background")
        
        # Create caption entries
        entries = []
        for i, cap in enumerate(captions):
            entries.append({
                "id": str(uuid.uuid4()).upper(),
                "index": i,
                "text": cap["text"],
                "start": cap["start"],
                "duration": cap["end"] - cap["start"],
                "emotion": cap.get("emotion", "neutral"),
                "chunk_id": cap.get("chunk_id", i),
                "sentence_count": cap.get("sentence_count", 1),
                "semantic_chunk": True
            })
        
        # Add metadata
        project_data.update({
            "captions": entries,
            "metadata": {
                "chunking_method": "semantic" if Config.ENABLE_SEMANTIC_CHUNKING else "basic",
                "emotion_classifier": "transformer" if Config.ENABLE_ADVANCED_EMOTIONS else "keyword",
                "total_chunks": len(captions),
                "total_duration": captions[-1]["end"] if captions else 0,
                "has_original_video": video_file is not None
            }
        })
        
        # Write project file
        draft_file = os.path.join(project_path, "draft_content.json")
        with open(draft_file, "w", encoding="utf-8") as f:
            json.dump(project_data, f, indent=2)
        
        logger.success(f"CapCut project created: {project_id}")
        logger.info(f"Method: {'Semantic' if Config.ENABLE_SEMANTIC_CHUNKING else 'Basic'} chunking + {'Transformer' if Config.ENABLE_ADVANCED_EMOTIONS else 'Keyword'} emotions")
        
        return project_path
    
    @staticmethod
    def load_latest_project() -> tuple:
        """
        Load the most recent CapCut project
        
        Returns:
            Tuple of (audio_path, video_path, captions)
        """
        if not os.path.exists(Config.CAPCUT_PROJECTS_FOLDER):
            raise Exception(f"CapCut projects folder not found: {Config.CAPCUT_PROJECTS_FOLDER}")
        
        # Find most recent project
        project_folders = [
            f for f in os.listdir(Config.CAPCUT_PROJECTS_FOLDER)
            if os.path.isdir(os.path.join(Config.CAPCUT_PROJECTS_FOLDER, f))
        ]
        
        if not project_folders:
            raise Exception("No CapCut projects found!")
        
        # Sort by modification time
        project_folders.sort(
            key=lambda x: os.path.getmtime(os.path.join(Config.CAPCUT_PROJECTS_FOLDER, x)),
            reverse=True
        )
        
        latest_project = project_folders[0]
        project_path = os.path.join(Config.CAPCUT_PROJECTS_FOLDER, latest_project)
        draft_file = os.path.join(project_path, "draft_content.json")
        
        if not os.path.exists(draft_file):
            raise Exception(f"No draft_content.json found in {project_path}")
        
        # Load project data
        with open(draft_file, 'r', encoding='utf-8') as f:
            project_data = json.load(f)
        
        # Extract captions
        captions = []
        for cap in project_data.get('captions', []):
            captions.append({
                "start": cap["start"],
                "end": cap["start"] + cap["duration"],
                "text": cap["text"],
                "emotion": cap.get("emotion", "neutral")
            })
        
        # Get file paths
        audio_path = os.path.join(project_path, project_data['audio'])
        video_path = None
        
        if 'video' in project_data and project_data['video']:
            video_path = os.path.join(project_path, project_data['video'])
            if not os.path.exists(video_path):
                logger.warning(f"Video file not found: {video_path}")
                video_path = None
        
        logger.success(f"Loaded project: {project_data['project_name']}")
        logger.info(f"Audio: {os.path.basename(audio_path)}")
        logger.info(f"Video: {os.path.basename(video_path) if video_path else 'None (colored background)'}")
        logger.info(f"Captions: {len(captions)} segments")
        
        return audio_path, video_path, captions
