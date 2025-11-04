"""
CapCut Project Generator Module
Creates CapCut-compatible project folders with full timeline structure
"""

import os
import json
import shutil
import uuid
import time
from typing import List, Dict, Optional
from src.config import Config
from src.utils.logger import logger


class CapCutProjectGenerator:
    """Generates real CapCut-compatible project folders"""
    
    @staticmethod
    def create_project(
        video_file: Optional[str],
        audio_file: str,
        captions: List[Dict],
        title: str
    ) -> str:
        """
        Create full CapCut project with timeline structure
        
        Args:
            video_file: Path to video file (optional)
            audio_file: Path to audio file
            captions: List of caption dictionaries
            title: Project title
            
        Returns:
            Path to created project folder
        """
        logger.info("Creating CapCut-compatible project...", "📁")
        
        # Create project structure
        project_id = str(uuid.uuid4()).upper()
        project_path = os.path.join(Config.CAPCUT_PROJECTS_FOLDER, project_id)
        import_path = os.path.join(project_path, "material", "import")
        os.makedirs(import_path, exist_ok=True)
        
        # Copy files
        shutil.copy(audio_file, import_path)
        audio_basename = os.path.basename(audio_file)
        logger.debug(f"Audio copied: {audio_basename}")
        
        video_basename = None
        if video_file and os.path.exists(video_file):
            shutil.copy(video_file, import_path)
            video_basename = os.path.basename(video_file)
            logger.debug(f"Video copied: {video_basename}")
        
        # Build CapCut project structure
        project_data = CapCutProjectGenerator._build_capcut_structure(
            project_id, title, video_basename, audio_basename, captions
        )
        
        # Write draft_content.json (main project file)
        draft_file = os.path.join(project_path, "draft_content.json")
        with open(draft_file, "w", encoding="utf-8") as f:
            json.dump(project_data, f, indent=2, ensure_ascii=False)
        
        # Write draft_info.json (metadata)
        info_data = {
            "draft_id": project_id,
            "draft_name": title,
            "draft_create_time": int(time.time() * 1000000),
            "draft_update_time": int(time.time() * 1000000),
            "draft_cover": "",
            "draft_timeline_position": 0
        }
        info_file = os.path.join(project_path, "draft_info.json")
        with open(info_file, "w", encoding="utf-8") as f:
            json.dump(info_data, f, indent=2, ensure_ascii=False)
        
        logger.success(f"CapCut project created: {project_id}")
        logger.info(f"Location: {project_path}")
        logger.info(f"Captions: {len(captions)} segments")
        
        return project_path
    
    @staticmethod
    def _build_capcut_structure(project_id, title, video_file, audio_file, captions):
        """Build complete CapCut JSON structure"""
        
        # Calculate total duration in microseconds
        duration_us = int(captions[-1]["end"] * 1000000) if captions else 0
        
        materials = {
            "audios": [],
            "videos": [],
            "texts": [],
            "images": [],
            "stickers": []
        }
        
        tracks = []
        
        # Add video track if exists
        if video_file:
            video_id = str(uuid.uuid4()).upper()
            materials["videos"].append({
                "id": video_id,
                "path": f"material/import/{video_file}",
                "type": "video",
                "duration": duration_us
            })
            
            tracks.append({
                "type": "video",
                "attribute": 0,
                "flag": 0,
                "segments": [{
                    "id": str(uuid.uuid4()).upper(),
                    "category": "video",
                    "material_id": video_id,
                    "target_timerange": {"start": 0, "duration": duration_us},
                    "source_timerange": {"start": 0, "duration": duration_us},
                    "extra_material_refs": []
                }]
            })
        
        # Add audio track
        audio_id = str(uuid.uuid4()).upper()
        materials["audios"].append({
            "id": audio_id,
            "path": f"material/import/{audio_file}",
            "type": "audio",
            "duration": duration_us
        })
        
        tracks.append({
            "type": "audio",
            "attribute": 0,
            "flag": 0,
            "segments": [{
                "id": str(uuid.uuid4()).upper(),
                "category": "audio",
                "material_id": audio_id,
                "target_timerange": {"start": 0, "duration": duration_us},
                "source_timerange": {"start": 0, "duration": duration_us},
                "volume": 1.0
            }]
        })
        
        # Add text tracks for captions
        for cap in captions:
            text_id = str(uuid.uuid4()).upper()
            start_us = int(cap["start"] * 1000000)
            duration_us_cap = int((cap["end"] - cap["start"]) * 1000000)
            
            materials["texts"].append({
                "id": text_id,
                "content": cap["text"],
                "type": "text"
            })
            
            tracks.append({
                "type": "text",
                "attribute": 0,
                "flag": 0,
                "segments": [{
                    "id": str(uuid.uuid4()).upper(),
                    "category": "text",
                    "material_id": text_id,
                    "target_timerange": {"start": start_us, "duration": duration_us_cap},
                    "content": cap["text"],
                    "font": "Arial",
                    "font_size": 40.0,
                    "color": [255, 255, 255],
                    "position": {"x": 0.5, "y": 0.85},
                    "align": "center",
                    "style": {
                        "bold": False,
                        "italic": False,
                        "underline": False
                    },
                    "animations": [{
                        "type": "fade_in",
                        "duration": 200000
                    }, {
                        "type": "fade_out",
                        "duration": 200000
                    }],
                    "metadata": {
                        "emotion": cap.get("emotion", "neutral"),
                        "chunk_id": cap.get("chunk_id", 0)
                    }
                }]
            })
        
        return {
            "draft_id": project_id,
            "draft_name": title,
            "draft_create_time": int(time.time() * 1000000),
            "draft_update_time": int(time.time() * 1000000),
            "duration": duration_us,
            "materials": materials,
            "tracks": tracks,
            "canvas_config": {
                "width": 1920,
                "height": 1080,
                "ratio": "16:9"
            },
            "extra_info": {
                "generator": "Python CapCut Automation",
                "version": "1.0",
                "chunking": "semantic" if Config.ENABLE_SEMANTIC_CHUNKING else "basic",
                "emotions": "transformer" if Config.ENABLE_ADVANCED_EMOTIONS else "keyword"
            }
        }
    
    
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
        
        # Extract captions from either old or new format
        captions = []
        
        # New format: captions in tracks
        if "tracks" in project_data:
            for track in project_data.get("tracks", []):
                if track.get("type") == "text":
                    for segment in track.get("segments", []):
                        start_s = segment["target_timerange"]["start"] / 1000000.0
                        duration_s = segment["target_timerange"]["duration"] / 1000000.0
                        captions.append({
                            "start": start_s,
                            "end": start_s + duration_s,
                            "text": segment.get("content", ""),
                            "emotion": segment.get("metadata", {}).get("emotion", "neutral")
                        })
            
            # Sort by start time
            captions.sort(key=lambda x: x["start"])
            
            # Extract file paths from materials
            audio_path = None
            video_path = None
            
            for audio in project_data.get("materials", {}).get("audios", []):
                audio_rel_path = audio.get("path", "").replace("/", "\\")
                audio_path = os.path.join(project_path, audio_rel_path)
                break
            
            for video in project_data.get("materials", {}).get("videos", []):
                video_rel_path = video.get("path", "").replace("/", "\\")
                video_path = os.path.join(project_path, video_rel_path)
                break
                
        # Old format: captions as separate array
        elif "captions" in project_data:
            for cap in project_data.get('captions', []):
                captions.append({
                    "start": cap["start"],
                    "end": cap["start"] + cap["duration"],
                    "text": cap["text"],
                    "emotion": cap.get("emotion", "neutral")
                })
            
            audio_path = os.path.join(project_path, project_data.get('audio', ''))
            if 'video' in project_data and project_data['video']:
                video_path = os.path.join(project_path, project_data['video'])
            else:
                video_path = None
        
        # Validate paths
        if not os.path.exists(audio_path):
            raise Exception(f"Audio file not found: {audio_path}")
        
        if video_path and not os.path.exists(video_path):
            logger.warning(f"Video file not found: {video_path}")
            video_path = None
        
        project_name = project_data.get('draft_name', project_data.get('project_name', 'Unknown'))
        
        logger.success(f"Loaded project: {project_name}")
        logger.info(f"Audio: {os.path.basename(audio_path)}")
        logger.info(f"Video: {os.path.basename(video_path) if video_path else 'None (colored background)'}")
        logger.info(f"Captions: {len(captions)} segments")
        
        return audio_path, video_path, captions
