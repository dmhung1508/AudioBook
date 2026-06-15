#!/usr/bin/env python3
"""
Example usage of VietVoice TTS with transcript output
Demonstrates how to use the new functions that return both audio and processed transcript
"""

import vietvoicetts
from pathlib import Path


def basic_example_with_transcript():
    """Basic TTS synthesis example with transcript"""
    print("=== Basic TTS Example with Transcript ===")
    
    text = input
    output_path = "basic_with_transcript.wav"
    
    try:
        # Synthesize and get transcript
        generation_time, processed_transcript = vietvoicetts.synthesize_with_transcript(
            text=text,
            output_path=output_path,
            gender="female",
            emotion="happy"
        )
        
        print(f"✅ Synthesis completed in {generation_time:.2f} seconds")
        print(f"📁 Audio saved to: {output_path}")
        print(f"📝 Original text: {text}")
        print(f"📝 Processed transcript: {processed_transcript}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True


def bytes_example_with_transcript():
    """Example returning audio as bytes with transcript"""
    print("\n=== Bytes Output Example with Transcript ===")
    
    text = "Ví dụ này trả về dữ liệu âm thanh và transcript đã xử lý."
    
    try:
        # Get audio bytes and transcript
        audio_bytes, generation_time, processed_transcript = vietvoicetts.synthesize_to_bytes_with_transcript(
            text=text,
            gender="male",
            emotion="neutral"
        )
        
        print(f"✅ Synthesis completed in {generation_time:.2f} seconds")
        print(f"📊 Audio bytes length: {len(audio_bytes)} bytes")
        print(f"📝 Original text: {text}")
        print(f"📝 Processed transcript: {processed_transcript}")
        
        # Save bytes to file
        bytes_output_path = "bytes_with_transcript.wav"
        with open(bytes_output_path, 'wb') as f:
            f.write(audio_bytes)
        print(f"📁 Bytes also saved to: {bytes_output_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True


def voice_cloning_with_transcript():
    """Voice cloning example with transcript"""
    print("\n=== Voice Cloning Example with Transcript ===")
    
    text = "Đây là ví dụ nhân bản giọng nói với transcript được xử lý."
    output_path = "cloned_with_transcript.wav"
    
    # Check if reference file exists
    reference_audio_path = './examples/sample.m4a'
    if not Path(reference_audio_path).exists():
        print(f"⚠️  Reference audio file not found: {reference_audio_path}")
        print("Using built-in voice samples instead...")
        reference_audio_path = None
        reference_text = None
    else:
        reference_text = "Xin chào các anh chị và các bạn. Chào mừng các anh chị đến với podcast Hiếu TV."
    
    try:
        # Voice cloning with transcript
        generation_time, processed_transcript = vietvoicetts.synthesize_with_transcript(
            text=text,
            output_path=output_path,
            reference_audio=reference_audio_path,
            reference_text=reference_text
        )
        
        print(f"✅ Voice cloning completed in {generation_time:.2f} seconds")
        print(f"📁 Audio saved to: {output_path}")
        print(f"📝 Original text: {text}")
        print(f"📝 Processed transcript: {processed_transcript}")
        
        if reference_audio_path:
            print(f"🎤 Used reference audio: {reference_audio_path}")
        else:
            print("🎤 Used built-in voice samples")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True


def api_class_example_with_transcript():
    """Example using TTSApi class with transcript methods"""
    print("\n=== API Class Example with Transcript ===")
    
    text = "Đây là ví dụ sử dụng class TTSApi với các phương thức transcript."
    
    try:
        # Using TTSApi class
        with vietvoicetts.TTSApi() as tts:
            # Method 1: Get audio array with transcript
            audio_array, generation_time, processed_transcript = tts.synthesize_with_transcript(
                text=text,
                gender="female",
                area="northern"
            )
            
            print(f"✅ Audio array synthesis completed in {generation_time:.2f} seconds")
            print(f"📊 Audio array shape: {audio_array.shape}")
            print(f"📝 Processed transcript: {processed_transcript}")
            
            # Method 2: Save to file with transcript
            output_path = "api_class_with_transcript.wav"
            generation_time2, processed_transcript2 = tts.synthesize_to_file_with_transcript(
                text=text,
                output_path=output_path,
                gender="male",
                area="southern"
            )
            
            print(f"✅ File synthesis completed in {generation_time2:.2f} seconds")
            print(f"📁 Audio saved to: {output_path}")
            print(f"📝 Processed transcript: {processed_transcript2}")
            
            # Method 3: Get bytes with transcript
            audio_bytes, generation_time3, processed_transcript3 = tts.synthesize_to_bytes_with_transcript(
                text=text,
                emotion="surprised"
            )
            
            print(f"✅ Bytes synthesis completed in {generation_time3:.2f} seconds")
            print(f"📊 Audio bytes length: {len(audio_bytes)} bytes")
            print(f"📝 Processed transcript: {processed_transcript3}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True


def text_processing_comparison():
    """Show comparison between original and processed text"""
    print("\n=== Text Processing Comparison ===")
    
    # Test with various types of text
    test_texts = [
        "Xin chào! Đây là văn bản có ký tự đặc biệt: @#$%^&*()",
        "Text with numbers: 123456789 and symbols: !!!???",
        "Mixed languages: Hello, 你好, สวัสดี, مرحبا",
        "Vietnamese accents: áàảãạ éèẻẽẹ íìỉĩị óòỏõọ úùủũụ ýỳỷỹỵ"
    ]
    
    try:
        with vietvoicetts.TTSApi() as tts:
            for i, text in enumerate(test_texts, 1):
                print(f"\n--- Test {i} ---")
                print(f"📝 Original: {text}")
                
                # Just get the processed transcript without generating audio
                processed_text = tts.engine.text_processor.clean_text(text)
                print(f"📝 Processed: {processed_text}")
                
                # Show character differences
                if text != processed_text:
                    print("🔄 Text was modified during processing")
                else:
                    print("✅ Text remained unchanged")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True


def main():
    """Run all examples"""
    print("🎙️ VietVoice TTS - Examples with Transcript Output\n")
    
    examples = [
        basic_example_with_transcript,
        # bytes_example_with_transcript,
        # voice_cloning_with_transcript,
        # api_class_example_with_transcript,
        # text_processing_comparison
    ]
    
    success_count = 0
    for example in examples:
        try:
            if example():
                success_count += 1
            print()  # Add spacing between examples
        except Exception as e:
            print(f"❌ Example failed: {e}\n")
    
    print(f"\n🎯 Summary: {success_count}/{len(examples)} examples completed successfully")
    
    if success_count == len(examples):
        print("✅ All examples completed successfully!")
        print("\n📋 Available methods with transcript:")
        print("1. vietvoicetts.synthesize_with_transcript() - Save to file + get transcript")
        print("2. vietvoicetts.synthesize_to_bytes_with_transcript() - Get bytes + transcript") 
        print("3. TTSApi.synthesize_with_transcript() - Get audio array + transcript")
        print("4. TTSApi.synthesize_to_file_with_transcript() - Save to file + transcript")
        print("5. TTSApi.synthesize_to_bytes_with_transcript() - Get bytes + transcript")
    else:
        print("⚠️  Some examples failed. Check the error messages above.")


if __name__ == "__main__":
    main()
