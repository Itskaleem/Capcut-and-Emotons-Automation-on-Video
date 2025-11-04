# Video Caption & Emotion Generator 🎬

Automatically generate videos with subtitles and emotion overlays from YouTube videos or local media files. Uses advanced semantic chunking and transformer-based emotion classification.

## Features ✨

- 🎥 **YouTube Download**: Automatically download videos from YouTube URLs
- 🎙️ **Speech Recognition**: Transcribe audio using Vosk ASR (offline)
- 🧠 **Semantic Chunking**: Group transcribed text into meaningful sentences using embeddings
- 😊 **Emotion Analysis**: Classify emotions using transformer models (7 emotion types)
- 📽️ **Video Rendering**: Overlay subtitles and emotion icons on original video
- 🎬 **CapCut Export**: Generate CapCut project folders for further editing

## Installation 🔧

### Prerequisites

- Python 3.9+ (tested on 3.11.5)
- FFmpeg installed and in PATH
- Vosk model downloaded (see below)

### 1. Clone/Download Project

```bash
cd c:\Users\kaleem.ullah\Projects\test
```

### 2. Create Virtual Environment

```powershell
python -m venv test
.\test\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
# Basic dependencies (required)
pip install -r requirements.txt

# For advanced emotion & semantic analysis (recommended)
pip install sentence-transformers transformers torch scikit-learn
```

### 4. Download Vosk Model

Download and extract the Vosk model to `models/`:

- [vosk-model-small-en-us-0.15](https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip)
- Extract to: `c:\Users\kaleem.ullah\Projects\test\models\vosk-model-small-en-us-0.15\`

### 5. Configure Environment

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

**Minimal configuration**:
```env
INPUT_SOURCE=https://www.youtube.com/watch?v=YOUR_VIDEO_ID
VOSK_MODEL_PATH=models/vosk-model-small-en-us-0.15
```

## Quick Start 🚀

### Option 1: Using .env file (Recommended)

1. Edit `.env` file:
   ```env
   INPUT_SOURCE=https://www.youtube.com/watch?v=dQw4w9WgXcQ
   ```

2. Run the pipeline:
   ```bash
   python main.py
   ```

### Option 2: Direct execution

```python
from main import VideoPipeline

pipeline = VideoPipeline()
pipeline.run()
```

## Configuration 🛠️

All settings in `.env` file:

### Input/Output
```env
INPUT_SOURCE=https://www.youtube.com/watch?v=VIDEO_ID  # YouTube URL, video path, or audio path
OUTPUT_DIR=output                                       # Output directory
CAPCUT_PROJECTS_DIR=capcut_projects                     # CapCut project folders
```

### Processing Options
```env
ENABLE_SEMANTIC_CHUNKING=true      # Use semantic chunking (vs basic time-based)
ENABLE_ADVANCED_EMOTIONS=true      # Use transformer emotions (vs keyword-based)
CHUNKING_SIMILARITY_THRESHOLD=0.7  # Sentence similarity threshold (0.0-1.0)
```

### Model Paths
```env
VOSK_MODEL_PATH=models/vosk-model-small-en-us-0.15
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
EMOTION_MODEL_NAME=j-hartmann/emotion-english-distilroberta-base
```

### Video Rendering
```env
VIDEO_WIDTH=1080               # Output video width
VIDEO_HEIGHT=1920              # Output video height
VIDEO_FPS=24                   # Frames per second
SUBTITLE_FONT_SIZE=40          # Subtitle text size
SUBTITLE_Y_OFFSET=120          # Distance from bottom (pixels)
ICON_SIZE=50                   # Emotion icon size
ICON_X_OFFSET=50               # Icon distance from left
USE_ORIGINAL_VIDEO=true        # Use original video as background
```

## Project Structure 📁

```
test/
├── main.py                    # Pipeline orchestrator
├── .env                       # Configuration (create from .env.example)
├── requirements.txt           # Python dependencies
├── src/
│   ├── config.py             # Configuration loader
│   ├── utils/
│   │   └── logger.py         # Logging utilities
│   └── modules/
│       ├── input_handler.py      # YouTube/video/audio processing
│       ├── transcriber.py        # Vosk speech recognition
│       ├── caption_generator.py  # Semantic chunking & emotions
│       ├── capcut_generator.py   # CapCut project creation
│       └── video_renderer.py     # Final video rendering
├── models/
│   └── vosk-model-small-en-us-0.15/  # Vosk ASR model
├── icons/                     # Emotion icons (auto-created)
├── capcut_projects/           # Generated CapCut projects
└── output/                    # Final rendered videos
```

## How It Works 🔍

1. **Input Processing**: Download YouTube video or load local media
2. **Transcription**: Convert audio to text using Vosk (word-level timestamps)
3. **Caption Generation**: 
   - Semantic chunking: Group words into sentences using embedding similarity
   - Emotion classification: Detect emotions using transformer models
4. **CapCut Export**: Generate CapCut project folder with metadata
5. **Video Rendering**: Overlay subtitles and emotions on video using MoviePy
6. **Cleanup**: Remove temporary files

## Advanced Features 🎯

### Semantic Chunking

Instead of fixed-duration chunks, sentences are grouped based on semantic similarity:

```python
# Words with similar embeddings are grouped together
# Threshold: 0.7 (configurable in .env)
"Hello world" + "How are you" → One chunk (similar)
"Hello world" + "Quantum physics" → Two chunks (dissimilar)
```

### Transformer Emotions

Uses DistilRoBERTa fine-tuned on emotion classification:

- 7 emotion classes: angry, disgust, fear, happy, neutral, sad, surprise
- Confidence scores: 0.70-0.99 (higher = more confident)
- Fallback to keyword-based if transformers unavailable

## Troubleshooting 🔧

### "Module not found: torch/transformers"
```bash
pip install torch transformers sentence-transformers scikit-learn
```
Or set in `.env`:
```env
ENABLE_SEMANTIC_CHUNKING=false
ENABLE_ADVANCED_EMOTIONS=false
```

### "FFmpeg not found"
Download FFmpeg and add to PATH:
- https://ffmpeg.org/download.html

### "Vosk model not found"
Ensure model path in `.env` matches extracted folder:
```env
VOSK_MODEL_PATH=models/vosk-model-small-en-us-0.15
```

### PyTorch DLL errors on Windows
The pipeline automatically handles DLL errors with lazy imports. If issues persist:
```bash
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

## Example Output 📊

```
🎬 ====== Video Caption & Emotion Pipeline ======

📥 Step 1/6: Processing Input
   ✅ Downloaded YouTube video: video_123.mp4

🎙️ Step 2/6: Transcribing Audio
   ✅ Transcribed 1989 words in 839.89s

📝 Step 3/6: Generating Captions
   ✅ Created 140 semantic chunks
   📊 Emotion distribution: angry(55%), neutral(30%), sad(8%)

🎬 Step 4/6: Creating CapCut Project
   ✅ CapCut project: E9C09BE7-38DB-4BAD-8F72-416D077B9836

🎥 Step 5/6: Rendering Final Video
   ✅ Video rendered: output/final_video_123.mp4

🧹 Step 6/6: Cleanup
   ✅ Removed temporary files

✅ Pipeline completed in 245.67s
```

## License

MIT License - Free to use and modify

## Credits

- **Vosk**: Offline speech recognition
- **Sentence Transformers**: Semantic embeddings
- **Hugging Face**: Emotion classification models
- **MoviePy**: Video processing
- **yt-dlp**: YouTube downloading
