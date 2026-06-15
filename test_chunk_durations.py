#!/usr/bin/env python3
"""
Test script to demonstrate chunk audio duration reporting
"""

import vietvoicetts

def test_chunk_durations():
    """Test TTS with chunk duration reporting"""
    print("🎙️ Testing Chunk Audio Duration Reporting\n")
    
    # Test with long text that will be split into multiple chunks
    long_text = """
    Xin chào các bạn, hôm nay mình sẽ hướng dẫn các bạn cách sử dụng VietVoice TTS một cách chi tiết và hiệu quả.
    Trước tiên, bạn cần cài đặt Python phiên bản 3.7 trở lên trên máy tính của mình.
    Sau đó, hãy mở VSCode hoặc IDE yêu thích và tạo một file mới với phần mở rộng .py.
    Tiếp theo, chúng ta sẽ import thư viện VietVoice TTS vào project và bắt đầu sử dụng.
    Cuối cùng, bạn có thể bắt đầu tạo ra những file âm thanh tuyệt vời với giọng nói tiếng Việt tự nhiên.
    Đây là một công cụ rất hữu ích cho việc tạo nội dung âm thanh, podcast, hoặc ứng dụng text-to-speech.
    """
    
    output_path = "chunk_duration_test.wav"
    
    try:
        print("📝 Input text:")
        print(f"   Length: {len(long_text)} characters")
        print(f"   Preview: {long_text.strip()[:100]}...")
        
        print(f"\n🔄 Generating speech with chunk duration reporting...")
        
        # Generate audio and get generation time
        duration = vietvoicetts.synthesize(
            text=long_text,
            output_path=output_path,
            gender="female",
            emotion="neutral"
        )
        
        print(f"\n🎉 Generation completed!")
        print(f"   📁 Output file: {output_path}")
        print(f"   ⏱️  Total time: {duration:.2f} seconds")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def test_short_text():
    """Test with short text (single chunk)"""
    print("\n" + "="*60)
    print("🎙️ Testing Short Text (Single Chunk)\n")
    
    short_text = "Đây là một câu ngắn để test."
    output_path = "single_chunk_test.wav"
    
    try:
        print("📝 Input text:")
        print(f"   Text: {short_text}")
        print(f"   Length: {len(short_text)} characters")
        
        print(f"\n🔄 Generating speech...")
        
        duration = vietvoicetts.synthesize(
            text=short_text,
            output_path=output_path,
            gender="male",
            emotion="happy"
        )
        
        print(f"\n🎉 Generation completed!")
        print(f"   📁 Output file: {output_path}")
        print(f"   ⏱️  Total time: {duration:.2f} seconds")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Run all tests"""
    print("🎙️ VietVoice TTS - Chunk Duration Testing\n")
    
    # Test long text (multiple chunks)
    test_chunk_durations()
    
    # Test short text (single chunk)
    test_short_text()
    
    print("\n" + "="*60)
    print("✅ Testing completed!")
    print("\n💡 Now you can see:")
    print("   • Duration of each individual chunk")
    print("   • Text content of each chunk")
    print("   • Total duration before cross-fading")
    print("   • Final audio duration after cross-fading")
    print("   • Time reduction due to cross-fading")

if __name__ == "__main__":
    main()
