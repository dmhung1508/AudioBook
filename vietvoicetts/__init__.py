"""
VietVoice TTS - Vietnamese Text-to-Speech Library
"""

from .core.model_config import ModelConfig, TTSConfig, MODEL_GENDER, MODEL_GROUP, MODEL_AREA, MODEL_EMOTION
from .core.tts_engine import TTSEngine
from .api import TTSApi, synthesize, synthesize_to_bytes, synthesize_with_transcript, synthesize_to_bytes_with_transcript
from .text_chunker import TextChunker, chunk_text, analyze_text_chunks, print_text_analysis

__version__ = "0.1.0"

__all__ = [
    "ModelConfig",
    "TTSConfig",  # Backward compatibility
    "TTSEngine",
    "TTSApi",
    "synthesize",
    "synthesize_to_bytes",
    "synthesize_with_transcript",
    "synthesize_to_bytes_with_transcript",
    "TextChunker",
    "chunk_text",
    "analyze_text_chunks", 
    "print_text_analysis",
    "MODEL_GENDER",
    "MODEL_GROUP",
    "MODEL_AREA",
    "MODEL_EMOTION",
] 