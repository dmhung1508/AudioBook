"""
Text Chunking API - Simple API to split text into chunks
"""

from typing import List, Tuple, Optional
from .core.text_processor import TextProcessor
from .core.model_config import ModelConfig


class TextChunker:
    """Simple text chunking utility"""
    
    def __init__(self, vocab_path: Optional[str] = None):
        """Initialize text chunker with vocabulary path"""
        if vocab_path is None:
            # Use default model config to get vocab path
            config = ModelConfig()
            from .core.model import ModelSessionManager
            session_manager = ModelSessionManager(config)
            session_manager.load_models()
            vocab_path = session_manager.vocab_path
            session_manager.cleanup()
        
        self.text_processor = TextProcessor(vocab_path)
    
    def chunk_text_simple(self, text: str, max_chars: int = 135) -> List[str]:
        """
        Split text into chunks with maximum character limit
        
        Args:
            text: Input text to split
            max_chars: Maximum characters per chunk
            
        Returns:
            List of text chunks
        """
        cleaned_text = self.text_processor.clean_text(text)
        chunks = self.text_processor.chunk_text(cleaned_text, max_chars)
        return chunks
    
    def chunk_text_with_info(self, text: str, max_chars: int = 135) -> List[dict]:
        """
        Split text into chunks with detailed information
        
        Args:
            text: Input text to split
            max_chars: Maximum characters per chunk
            
        Returns:
            List of dictionaries with chunk information
        """
        cleaned_text = self.text_processor.clean_text(text)
        chunks = self.text_processor.chunk_text(cleaned_text, max_chars)
        
        chunk_info = []
        for i, chunk in enumerate(chunks):
            chunk_length = self.text_processor.calculate_text_length(chunk, r'[.!?]')
            info = {
                'index': i + 1,
                'text': chunk,
                'char_count': len(chunk),
                'weighted_length': chunk_length,
                'preview': chunk[:50] + '...' if len(chunk) > 50 else chunk
            }
            chunk_info.append(info)
        
        return chunk_info
    
    def estimate_chunk_durations(self, text: str, max_chars: int = 135, 
                                speaking_rate: float = 150.0) -> List[dict]:
        """
        Split text and estimate audio duration for each chunk
        
        Args:
            text: Input text to split
            max_chars: Maximum characters per chunk
            speaking_rate: Characters per second speaking rate
            
        Returns:
            List of dictionaries with chunk and duration information
        """
        chunk_info = self.chunk_text_with_info(text, max_chars)
        
        for info in chunk_info:
            # Estimate duration based on weighted text length
            estimated_duration = max(info['weighted_length'] / speaking_rate, 0.5)
            info['estimated_duration'] = round(estimated_duration, 2)
        
        return chunk_info
    
    def print_chunk_analysis(self, text: str, max_chars: int = 135, 
                           speaking_rate: float = 150.0) -> None:
        """
        Print detailed analysis of text chunking
        
        Args:
            text: Input text to analyze
            max_chars: Maximum characters per chunk
            speaking_rate: Characters per second speaking rate
        """
        print("📝 Text Chunking Analysis")
        print("=" * 60)
        
        original_length = len(text)
        cleaned_text = self.text_processor.clean_text(text)
        cleaned_length = len(cleaned_text)
        
        print(f"Original text length: {original_length} characters")
        print(f"Cleaned text length: {cleaned_length} characters")
        print(f"Characters removed: {original_length - cleaned_length}")
        print(f"Max characters per chunk: {max_chars}")
        print(f"Speaking rate: {speaking_rate} chars/second")
        
        chunk_info = self.estimate_chunk_durations(text, max_chars, speaking_rate)
        
        print(f"\nChunks created: {len(chunk_info)}")
        print("-" * 60)
        
        total_estimated_duration = 0
        for info in chunk_info:
            print(f"Chunk {info['index']}:")
            print(f"  📏 Length: {info['char_count']} chars (weighted: {info['weighted_length']})")
            print(f"  ⏱️  Estimated duration: {info['estimated_duration']}s")
            print(f"  📄 Preview: {info['preview']}")
            print()
            total_estimated_duration += info['estimated_duration']
        
        print("-" * 60)
        print(f"Total estimated duration: {total_estimated_duration:.2f}s")
        print(f"Average chunk duration: {total_estimated_duration/len(chunk_info):.2f}s")


# Convenience functions
def chunk_text(text: str, max_chars: int = 135, vocab_path: Optional[str] = None) -> List[str]:
    """
    Simple function to split text into chunks
    
    Args:
        text: Input text to split
        max_chars: Maximum characters per chunk
        vocab_path: Path to vocabulary file (optional)
        
    Returns:
        List of text chunks
    """
    chunker = TextChunker(vocab_path)
    return chunker.chunk_text_simple(text, max_chars)

def analyze_text_chunks(text: str, max_chars: int = 135, 
                       speaking_rate: float = 150.0, vocab_path: Optional[str] = None) -> List[dict]:
    """
    Analyze text and return detailed chunk information
    
    Args:
        text: Input text to analyze
        max_chars: Maximum characters per chunk
        speaking_rate: Characters per second speaking rate
        vocab_path: Path to vocabulary file (optional)
        
    Returns:
        List of dictionaries with detailed chunk information
    """
    chunker = TextChunker(vocab_path)
    return chunker.estimate_chunk_durations(text, max_chars, speaking_rate)

def print_text_analysis(text: str, max_chars: int = 135, 
                       speaking_rate: float = 150.0, vocab_path: Optional[str] = None) -> None:
    """
    Print detailed text chunking analysis
    
    Args:
        text: Input text to analyze
        max_chars: Maximum characters per chunk
        speaking_rate: Characters per second speaking rate
        vocab_path: Path to vocabulary file (optional)
    """
    chunker = TextChunker(vocab_path)
    chunker.print_chunk_analysis(text, max_chars, speaking_rate)
