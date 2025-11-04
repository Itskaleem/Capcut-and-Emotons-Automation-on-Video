"""
Transcription Module
Handles speech-to-text transcription using Vosk
"""

import wave
import json
from vosk import Model, KaldiRecognizer
from src.config import Config
from src.utils.logger import logger


class Transcriber:
    """Handles audio transcription using Vosk"""
    
    def __init__(self):
        self.model = None
    
    def transcribe(self, wav_path: str) -> list:
        """
        Transcribe audio file to word-level timestamps
        
        Args:
            wav_path: Path to 16kHz mono WAV file
            
        Returns:
            List of word dictionaries with timestamps
        """
        logger.info("Starting transcription with Vosk...", "🎙️")
        logger.warning("This may take a few minutes...")
        
        # Load model if not already loaded
        if self.model is None:
            self.model = Model(Config.VOSK_MODEL_PATH)
        
        wf = wave.open(wav_path, "rb")
        rec = KaldiRecognizer(self.model, wf.getframerate())
        rec.SetWords(True)
        
        results = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                if "result" in res:
                    results.extend(res["result"])
        
        # Final result
        final = json.loads(rec.FinalResult())
        if "result" in final:
            results.extend(final["result"])
        
        logger.success(f"Transcription complete: {len(results)} words recognized")
        return results
