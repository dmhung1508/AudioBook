#!/usr/bin/env python3
"""
Test script for text chunking functionality
"""

import vietvoicetts

def test_simple_chunking():
    """Test simple text chunking"""
    print("📝 Simple Text Chunking Test")
    print("=" * 50)
    
    text = """
    Xin chào các bạn, hôm nay mình sẽ hướng dẫn các bạn cách sử dụng VietVoice TTS.
    Trước tiên, bạn cần cài đặt Python trên máy tính của mình.
    Sau đó, hãy mở VSCode và tạo một file mới với phần mở rộng .py.
    Tiếp theo, chúng ta sẽ import thư viện VietVoice TTS vào project.
    Cuối cùng, bạn có thể bắt đầu tạo ra những file âm thanh tuyệt vời.
    """
    
    try:
        # Simple chunking
        chunks = vietvoicetts.chunk_text(text, max_chars=100)
        
        print(f"Original text length: {len(text)} characters")
        print(f"Number of chunks: {len(chunks)}")
        print("\nChunks:")
        for i, chunk in enumerate(chunks, 1):
            print(f"  {i}. [{len(chunk)} chars] {chunk}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def test_detailed_analysis():
    """Test detailed text analysis"""
    print("\n\n📊 Detailed Text Analysis Test")
    print("=" * 50)
    
    text = """
    Xin chào các bạn, hôm nay mình sẽ hướng dẫn các bạn cách sử dụng VietVoice TTS một cách chi tiết.
    Trước tiên, bạn cần cài đặt Python phiên bản 3.7 trở lên trên máy tính của mình.
    Sau đó, hãy mở VSCode hoặc IDE yêu thích và tạo một file mới với phần mở rộng .py.
    Tiếp theo, chúng ta sẽ import thư viện VietVoice TTS vào project và bắt đầu coding.
    Cuối cùng, bạn có thể bắt đầu tạo ra những file âm thanh tuyệt vời với giọng nói tự nhiên.
    """
    
    try:
        # Detailed analysis
        chunk_info = vietvoicetts.analyze_text_chunks(text, max_chars=120, speaking_rate=150)
        
        print(f"Analysis Results:")
        print(f"  Original length: {len(text)} characters")
        print(f"  Chunks created: {len(chunk_info)}")
        
        total_duration = sum(info['estimated_duration'] for info in chunk_info)
        print(f"  Total estimated duration: {total_duration:.2f}s")
        
        print(f"\nDetailed Chunk Information:")
        for info in chunk_info:
            print(f"  Chunk {info['index']}:")
            print(f"    📏 Length: {info['char_count']} chars")
            print(f"    ⚖️  Weighted: {info['weighted_length']}")
            print(f"    ⏱️  Duration: {info['estimated_duration']}s")
            print(f"    📄 Preview: {info['preview']}")
            print()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def test_print_analysis():
    """Test print analysis function"""
    print("\n\n🖨️  Print Analysis Test")
    print("=" * 50)
    
    text = """
    Đây là một ví dụ về phân tích văn bản chi tiết với VietVoice TTS.
    Chúng ta sẽ xem cách hệ thống chia nhỏ văn bản thành các đoạn phù hợp.
    Mỗi đoạn sẽ có thông tin về độ dài, thời gian ước tính và nội dung.
    """
    
    try:
        # Use the print analysis function
        vietvoicetts.print_text_analysis(text, max_chars=80, speaking_rate=160)
        
    except Exception as e:
        print(f"❌ Error: {e}")

def test_api_class():
    """Test using TextChunker class directly"""
    print("\n\n🏗️  TextChunker Class Test")
    print("=" * 50)
    
    text = "Xin chào! Đây là test class TextChunker. Nó sẽ chia text thành các chunk nhỏ."
    
    try:
        chunker = vietvoicetts.TextChunker()
        
        # Simple chunking
        simple_chunks = chunker.chunk_text_simple(text, max_chars=30)
        print(f"Simple chunks ({len(simple_chunks)}):")
        for i, chunk in enumerate(simple_chunks, 1):
            print(f"  {i}. {chunk}")
        
        # Detailed info
        print(f"\nDetailed chunk info:")
        chunk_info = chunker.chunk_text_with_info(text, max_chars=30)
        for info in chunk_info:
            print(f"  Chunk {info['index']}: {info['char_count']} chars - {info['preview']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Run all tests"""
    print("🎙️ VietVoice TTS - Text Chunking API Tests\n")
    
    test_simple_chunking()
    test_detailed_analysis()
    test_print_analysis()
    test_api_class()
    
    print("\n" + "="*60)
    print("✅ All text chunking tests completed!")
    print("\n💡 Available functions:")
    print("  • vietvoicetts.chunk_text() - Simple text chunking")
    print("  • vietvoicetts.analyze_text_chunks() - Detailed analysis")
    print("  • vietvoicetts.print_text_analysis() - Print analysis")
    print("  • vietvoicetts.TextChunker() - Full API class")

if __name__ == "__main__":
    main()
