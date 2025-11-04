"""
Caption Generator Module
Handles semantic chunking and emotion classification
"""

from typing import List, Dict
from src.config import Config
from src.utils.logger import logger

# Check if advanced libraries are available (lazy import to avoid DLL errors)
ADVANCED_MODE = False
_advanced_libs_checked = False

def _check_advanced_libs():
    """Check if advanced libraries can be loaded"""
    global ADVANCED_MODE, _advanced_libs_checked
    if _advanced_libs_checked:
        return ADVANCED_MODE
    
    _advanced_libs_checked = True
    try:
        # Test import without actually importing yet
        import importlib.util
        specs = [
            importlib.util.find_spec("sentence_transformers"),
            importlib.util.find_spec("transformers"),
            importlib.util.find_spec("sklearn"),
            importlib.util.find_spec("numpy")
        ]
        if all(spec is not None for spec in specs):
            ADVANCED_MODE = Config.ENABLE_ADVANCED_EMOTIONS and Config.ENABLE_SEMANTIC_CHUNKING
            if ADVANCED_MODE:
                logger.info("Advanced emotion & semantic libraries available")
        else:
            logger.warning("Some advanced libraries missing. Using basic mode.")
    except Exception as e:
        logger.warning(f"Advanced libraries check failed: {e}. Using basic mode.")
        ADVANCED_MODE = False
    
    return ADVANCED_MODE


class CaptionGenerator:
    """Generates captions with semantic chunking and emotion classification"""
    
    def __init__(self):
        self.embedding_model = None
        self.emotion_classifier = None
    
    def generate(self, asr_words: List[Dict]) -> List[Dict]:
        """
        Generate captions from ASR words
        
        Args:
            asr_words: List of word dictionaries from transcription
            
        Returns:
            List of caption dictionaries
        """
        if not asr_words:
            logger.warning("No words to process")
            return []
        
        logger.info("Generating captions with semantic chunking...", "📝")
        
        # Check if advanced mode is available
        use_advanced = _check_advanced_libs()
        
        # Step 1: Group words into sentences
        sentences = self._group_words_into_sentences(asr_words)
        logger.info(f"Created {len(sentences)} sentences from word timestamps")
        
        # Step 2: Apply semantic chunking
        if use_advanced and Config.ENABLE_SEMANTIC_CHUNKING:
            semantic_chunks = self._semantic_chunking(sentences)
        else:
            semantic_chunks = [[s] for s in sentences]  # One sentence per chunk
            logger.info("Using basic sentence-level chunking")
        
        # Step 3: Create captions with emotion classification
        captions = []
        for i, chunk in enumerate(semantic_chunks):
            combined_text = " ".join([s["text"] for s in chunk])
            start_time = chunk[0]["start"]
            end_time = chunk[-1]["end"]
            
            # Classify emotion
            emotion = self._classify_emotion(combined_text)
            
            caption = {
                "start": start_time,
                "end": end_time,
                "text": combined_text,
                "emotion": emotion,
                "chunk_id": i,
                "sentence_count": len(chunk)
            }
            captions.append(caption)
        
        logger.success(f"Generated {len(captions)} semantic captions")
        
        # Preview
        for i, cap in enumerate(captions[:3]):
            logger.debug(f"Preview {i+1}: [{cap['start']:.1f}-{cap['end']:.1f}s] ({cap['emotion']}) {cap['text'][:60]}...")
        
        return captions
    
    def _group_words_into_sentences(self, asr_words: List[Dict]) -> List[Dict]:
        """Group words into sentences based on pauses"""
        sentences = []
        current_sentence = []
        
        for i, word in enumerate(asr_words):
            current_sentence.append(word)
            
            should_end = False
            
            # Check gap to next word
            if i < len(asr_words) - 1:
                next_word = asr_words[i + 1]
                gap = next_word["start"] - word["end"]
                if gap > Config.MAX_PAUSE_GAP:
                    should_end = True
            else:
                should_end = True
            
            # Prevent very long sentences
            if len(current_sentence) > Config.MAX_WORDS_PER_SENTENCE:
                should_end = True
            
            if should_end and current_sentence:
                sentence = {
                    "words": current_sentence.copy(),
                    "text": " ".join([w["word"] for w in current_sentence]),
                    "start": current_sentence[0]["start"],
                    "end": current_sentence[-1]["end"]
                }
                sentences.append(sentence)
                current_sentence = []
        
        return sentences
    
    def _semantic_chunking(self, sentences: List[Dict]) -> List[List[Dict]]:
        """Group semantically similar sentences using embeddings"""
        if len(sentences) <= 1:
            return [[s] for s in sentences]
        
        try:
            # Lazy import to avoid DLL errors
            from sentence_transformers import SentenceTransformer
            from sklearn.metrics.pairwise import cosine_similarity
            
            logger.info("Performing semantic chunking...", "🧠")
            
            # Load embedding model if needed
            if self.embedding_model is None:
                self.embedding_model = SentenceTransformer(Config.EMBEDDING_MODEL)
            
            # Get embeddings
            texts = [s["text"] for s in sentences]
            embeddings = self.embedding_model.encode(texts)
            
            # Group by similarity
            chunks = []
            current_chunk = [sentences[0]]
            
            for i in range(1, len(sentences)):
                similarity = cosine_similarity(
                    embeddings[i-1].reshape(1, -1),
                    embeddings[i].reshape(1, -1)
                )[0][0]
                
                if similarity > Config.SIMILARITY_THRESHOLD and len(current_chunk) < Config.MAX_SENTENCES_PER_CHUNK:
                    current_chunk.append(sentences[i])
                else:
                    chunks.append(current_chunk)
                    current_chunk = [sentences[i]]
            
            if current_chunk:
                chunks.append(current_chunk)
            
            logger.success(f"Created {len(chunks)} semantic chunks from {len(sentences)} sentences")
            return chunks
            
        except Exception as e:
            logger.warning(f"Semantic chunking failed: {e}")
            logger.info("Falling back to sentence-level chunks")
            return [[s] for s in sentences]
    
    def _classify_emotion(self, text: str) -> str:
        """Classify emotion using transformer or keywords"""
        if ADVANCED_MODE and Config.ENABLE_ADVANCED_EMOTIONS:
            return self._classify_emotion_advanced(text)
        else:
            return self._classify_emotion_basic(text)
    
    def _classify_emotion_advanced(self, text: str) -> str:
        """Use transformer-based emotion classification"""
        try:
            # Lazy import to avoid DLL errors
            from transformers import pipeline
            
            # Load classifier if needed
            if self.emotion_classifier is None:
                self.emotion_classifier = pipeline(
                    "text-classification",
                    model=Config.EMOTION_MODEL,
                    device=-1  # CPU
                )
            
            result = self.emotion_classifier(text[:512])[0]  # Limit text length
            emotion = result['label'].lower()
            confidence = result['score']
            
            # Map to our categories
            emotion_mapping = {
                'joy': 'happy',
                'happiness': 'happy',
                'sadness': 'sad',
                'anger': 'angry',
                'fear': 'sad',
                'surprise': 'surprised',
                'disgust': 'angry',
                'neutral': 'neutral'
            }
            
            mapped_emotion = emotion_mapping.get(emotion, 'neutral')
            
            if Config.VERBOSE_LOGGING and mapped_emotion != 'neutral':
                logger.debug(f"Emotion: {text[:40]}... -> {mapped_emotion} ({confidence:.2f})")
            
            return mapped_emotion
            
        except Exception as e:
            if Config.VERBOSE_LOGGING:
                logger.warning(f"Advanced emotion classification failed: {e}")
            return self._classify_emotion_basic(text)
    
    def _classify_emotion_basic(self, text: str) -> str:
        """Basic keyword-based emotion detection"""
        t = text.lower()
        
        if any(w in t for w in ["happy", "joy", "laugh", "smile", "great", "amazing", "love"]):
            return "happy"
        if any(w in t for w in ["sad", "cry", "tears", "terrible", "awful", "bad"]):
            return "sad"
        if any(w in t for w in ["angry", "mad", "rage", "hate", "furious"]):
            return "angry"
        if any(w in t for w in ["wow", "surprise", "shocked", "amazing", "incredible"]):
            return "surprised"
        
        return "neutral"
