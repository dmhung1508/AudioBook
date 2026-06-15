#!/usr/bin/env python3
"""
FastAPI implementation for VietVoice TTS - NhaNamApp AI Voice Service
Based on API documentation for http://14.224.131.219:4500
"""
import os
import sys
import asyncio
import json
import time
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import tempfile
import io

# FastAPI imports
from fastapi import FastAPI, HTTPException, Response, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Add parent directory to path for importing vietvoicetts
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import vietvoicetts
from vietvoicetts import ModelConfig, TTSApi

# Configuration
API_HOST = "0.0.0.0"
API_PORT = 4500
VOICE_PROCESSING_PORT = 4501

# FastAPI app
app = FastAPI(
    title="VietVoice TTS API",
    description="AI Voice Service for NhaNamApp - Text-to-Speech and Audio Summary Generation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Voice processing app (separate instance for port 4501)
voice_app = FastAPI(
    title="Voice Processing API",
    description="Voice Processing Status and Queue Management",
    version="1.0.0"
)

voice_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (in production, use Redis/Database)
voice_cache = {}
processing_status = {}
book_summaries = {}

# Available voices configuration
AVAILABLE_VOICES = [
    {
        "id": "voice_1",
        "name": "first",
        "displayName": "Giọng nữ 1",
        "language": "vi-VN",
        "gender": "female",
        "emotion": "neutral"
    },
    {
        "id": "voice_2", 
        "name": "second",
        "displayName": "Giọng nam 1",
        "language": "vi-VN",
        "gender": "male",
        "emotion": "neutral"
    },
    {
        "id": "voice_3",
        "name": "third",
        "displayName": "Giọng nữ 2 - Vui vẻ",
        "language": "vi-VN",
        "gender": "female",
        "emotion": "happy"
    },
    {
        "id": "voice_4",
        "name": "fourth",
        "displayName": "Giọng nam 2 - Nghiêm túc",
        "language": "vi-VN",
        "gender": "male",
        "emotion": "serious"
    }
]

# Sample book data
SAMPLE_BOOKS = {
    "test_book": {
        "id": "test_book",
        "name": "Sách Kiểm Tra",
        "summary": "Đây là một cuốn sách kiểm tra hệ thống TTS. Cuốn sách này được thiết kế để test các tính năng của API VietVoice TTS.",
        "full_content": """
        Chương 1: Giới thiệu
        Đây là chương đầu tiên của cuốn sách kiểm tra. Chúng ta sẽ tìm hiểu về các tính năng cơ bản của hệ thống text-to-speech.
        
        Chương 2: Các tính năng nâng cao
        Trong chương này, chúng ta sẽ khám phá các tính năng nâng cao như thay đổi giọng đọc, tốc độ đọc và cảm xúc.
        
        Chương 3: Kết luận
        Cuối cùng, chúng ta sẽ tổng kết những gì đã học được và đưa ra kết luận về hiệu quả của hệ thống.
        """
    },
    "book_001": {
        "id": "book_001",
        "name": "Truyện Cổ Tích Việt Nam",
        "summary": "Tuyển tập những truyện cổ tích Việt Nam hay nhất, mang đậm bản sắc văn hóa dân tộc.",
        "full_content": "Ngày xưa, có một cô bé tên là Tấm sống với mẹ kế và em gái cùng cha khác mẹ..."
    }
}

def get_voice_config(voice_name: str) -> Dict[str, Any]:
    """Get voice configuration by name"""
    voice_map = {
        "first": {"gender": "female", "emotion": "neutral"},
        "second": {"gender": "male", "emotion": "neutral"},
        "third": {"gender": "female", "emotion": "happy"},
        "fourth": {"gender": "male", "emotion": "serious"}
    }
    return voice_map.get(voice_name, {"gender": "female", "emotion": "neutral"})

async def generate_audio_async(text: str, voice_name: str, output_path: str) -> float:
    """Generate audio asynchronously"""
    try:
        voice_config = get_voice_config(voice_name)
        
        # Use VietVoice TTS to generate audio
        generation_time = vietvoicetts.synthesize(
            text=text,
            output_path=output_path,
            gender=voice_config["gender"],
            emotion=voice_config["emotion"]
        )
        
        return generation_time
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio generation failed: {str(e)}")

# Main API Endpoints (Port 4500)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "VietVoice TTS API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "/all_voice",
            "/summary_transcript/{bookId}/{voice}",
            "/summary_audio/{bookId}/{voice}",
            "/docs"
        ]
    }

@app.get("/all_voice")
async def get_all_voices():
    """Get list of all available voices"""
    return {"voices": AVAILABLE_VOICES}

@app.get("/summary_transcript/{book_id}/{voice}")
async def get_summary_transcript(book_id: str, voice: str):
    """Get book summary transcript for specific voice"""
    
    # Check if book exists
    if book_id not in SAMPLE_BOOKS:
        raise HTTPException(status_code=404, detail=f"Book '{book_id}' not found")
    
    # Check if voice exists
    voice_names = [v["name"] for v in AVAILABLE_VOICES]
    if voice not in voice_names:
        raise HTTPException(status_code=400, detail=f"Voice '{voice}' not supported. Available voices: {voice_names}")
    
    book = SAMPLE_BOOKS[book_id]
    
    # Return summary transcript
    transcript = {
        "bookId": book_id,
        "voice": voice,
        "title": book["name"],
        "summary": book["summary"],
        "transcript": book["summary"],
        "generatedAt": datetime.now().isoformat(),
        "duration": "estimated 30-60 seconds"
    }
    
    return transcript

@app.get("/summary_audio/{book_id}/{voice}")
async def get_summary_audio(book_id: str, voice: str):
    """Get book summary audio file"""
    
    # Check if book exists
    if book_id not in SAMPLE_BOOKS:
        raise HTTPException(status_code=404, detail=f"Book '{book_id}' not found")
    
    # Check if voice exists
    voice_names = [v["name"] for v in AVAILABLE_VOICES]
    if voice not in voice_names:
        raise HTTPException(status_code=400, detail=f"Voice '{voice}' not supported. Available voices: {voice_names}")
    
    # Create cache key
    cache_key = f"{book_id}_{voice}"
    
    # Check cache first
    if cache_key in voice_cache:
        cached_file = voice_cache[cache_key]
        if os.path.exists(cached_file):
            return FileResponse(
                cached_file,
                media_type="audio/mpeg",
                filename=f"summary_{book_id}_{voice}.wav"
            )
    
    # Generate new audio
    book = SAMPLE_BOOKS[book_id]
    text = book["summary"]
    
    # Create temporary file
    temp_dir = tempfile.gettempdir()
    output_file = os.path.join(temp_dir, f"summary_{book_id}_{voice}_{int(time.time())}.wav")
    
    try:
        # Generate audio
        generation_time = await generate_audio_async(text, voice, output_file)
        
        # Cache the file
        voice_cache[cache_key] = output_file
        
        # Return audio file
        return FileResponse(
            output_file,
            media_type="audio/wav",
            filename=f"summary_{book_id}_{voice}.wav",
            headers={
                "X-Generation-Time": str(generation_time),
                "X-Voice": voice,
                "X-Book-ID": book_id
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate audio: {str(e)}")

@app.post("/generate_custom_audio")
async def generate_custom_audio(
    text: str,
    voice: str = "first",
    speed: float = 1.0,
    background_tasks: BackgroundTasks = None
):
    """Generate custom audio from text (for testing)"""
    
    # Validate voice
    voice_names = [v["name"] for v in AVAILABLE_VOICES]
    if voice not in voice_names:
        raise HTTPException(status_code=400, detail=f"Voice '{voice}' not supported")
    
    # Validate text length
    if len(text) > 5000:
        raise HTTPException(status_code=400, detail="Text too long (max 5000 characters)")
    
    # Create temporary file
    temp_dir = tempfile.gettempdir()
    output_file = os.path.join(temp_dir, f"custom_{voice}_{int(time.time())}.wav")
    
    try:
        # Configure TTS with custom speed
        voice_config = get_voice_config(voice)
        config = ModelConfig(speed=speed)
        
        with TTSApi(config) as tts:
            audio_data, generation_time = tts.synthesize(
                text=text,
                output_path=output_file
            )
        
        return FileResponse(
            output_file,
            media_type="audio/wav",
            filename=f"custom_{voice}.wav",
            headers={
                "X-Generation-Time": str(generation_time),
                "X-Voice": voice,
                "X-Speed": str(speed),
                "X-Text-Length": str(len(text))
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate custom audio: {str(e)}")

@app.get("/books")
async def get_books():
    """Get list of available books (for testing)"""
    return {
        "books": [
            {
                "id": book_id,
                "name": book_data["name"],
                "summary_length": len(book_data["summary"]),
                "content_length": len(book_data["full_content"])
            }
            for book_id, book_data in SAMPLE_BOOKS.items()
        ]
    }

# Voice Processing API Endpoints (Port 4501)

@voice_app.get("/")
async def voice_root():
    """Voice processing root endpoint"""
    return {
        "service": "Voice Processing API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "/processing-all/{bookId}",
            "/queue-status",
            "/docs"
        ]
    }

@voice_app.get("/processing-all/{book_id}")
async def get_processing_status(book_id: str):
    """Get processing status for all voices of a book"""
    
    # Check if book exists
    if book_id not in SAMPLE_BOOKS:
        raise HTTPException(status_code=404, detail=f"Book '{book_id}' not found")
    
    # Initialize processing status if not exists
    if book_id not in processing_status:
        processing_status[book_id] = {
            "bookId": book_id,
            "status": "completed",  # Default to completed for testing
            "progress": 1.0,
            "startedAt": datetime.now().isoformat(),
            "completedAt": datetime.now().isoformat(),
            "voices": []
        }
        
        # Add voice processing status
        for voice in AVAILABLE_VOICES:
            processing_status[book_id]["voices"].append({
                "name": voice["name"],
                "displayName": voice["displayName"],
                "status": "ready",
                "progress": 1.0,
                "audioUrl": f"http://14.224.131.219:4500/summary_audio/{book_id}/{voice['name']}"
            })
    
    return processing_status[book_id]

@voice_app.post("/start-processing/{book_id}")
async def start_processing(book_id: str, background_tasks: BackgroundTasks):
    """Start processing audio for all voices (simulate async processing)"""
    
    if book_id not in SAMPLE_BOOKS:
        raise HTTPException(status_code=404, detail=f"Book '{book_id}' not found")
    
    # Initialize processing
    processing_status[book_id] = {
        "bookId": book_id,
        "status": "processing",
        "progress": 0.0,
        "startedAt": datetime.now().isoformat(),
        "completedAt": None,
        "voices": []
    }
    
    # Add voice processing status
    for voice in AVAILABLE_VOICES:
        processing_status[book_id]["voices"].append({
            "name": voice["name"],
            "displayName": voice["displayName"],
            "status": "queued",
            "progress": 0.0,
            "audioUrl": None
        })
    
    # Start background processing
    background_tasks.add_task(process_book_async, book_id)
    
    return {
        "message": f"Processing started for book '{book_id}'",
        "bookId": book_id,
        "estimatedTime": "60-120 seconds"
    }

async def process_book_async(book_id: str):
    """Simulate async book processing"""
    try:
        book = SAMPLE_BOOKS[book_id]
        total_voices = len(AVAILABLE_VOICES)
        
        for i, voice in enumerate(AVAILABLE_VOICES):
            # Update voice status to processing
            processing_status[book_id]["voices"][i]["status"] = "processing"
            processing_status[book_id]["progress"] = i / total_voices
            
            # Simulate processing time
            await asyncio.sleep(2)
            
            # Generate actual audio (optional - can be skipped for demo)
            try:
                temp_dir = tempfile.gettempdir()
                output_file = os.path.join(temp_dir, f"processed_{book_id}_{voice['name']}.wav")
                
                await generate_audio_async(book["summary"], voice["name"], output_file)
                
                # Update voice status to ready
                processing_status[book_id]["voices"][i]["status"] = "ready"
                processing_status[book_id]["voices"][i]["progress"] = 1.0
                processing_status[book_id]["voices"][i]["audioUrl"] = f"http://14.224.131.219:4500/summary_audio/{book_id}/{voice['name']}"
                
            except Exception as e:
                # Handle processing error
                processing_status[book_id]["voices"][i]["status"] = "error"
                processing_status[book_id]["voices"][i]["error"] = str(e)
        
        # Mark overall processing as completed
        processing_status[book_id]["status"] = "completed"
        processing_status[book_id]["progress"] = 1.0
        processing_status[book_id]["completedAt"] = datetime.now().isoformat()
        
    except Exception as e:
        # Handle overall processing error
        processing_status[book_id]["status"] = "error"
        processing_status[book_id]["error"] = str(e)

@voice_app.get("/queue-status")
async def get_queue_status():
    """Get overall queue status"""
    total_books = len(processing_status)
    processing_books = sum(1 for status in processing_status.values() if status["status"] == "processing")
    completed_books = sum(1 for status in processing_status.values() if status["status"] == "completed")
    error_books = sum(1 for status in processing_status.values() if status["status"] == "error")
    
    return {
        "totalBooks": total_books,
        "processing": processing_books,
        "completed": completed_books,
        "errors": error_books,
        "queue": list(processing_status.keys())
    }

async def run_servers():
    """Run both servers concurrently"""
    import asyncio
    
    # Configure uvicorn
    main_config = uvicorn.Config(
        app,
        host=API_HOST,
        port=API_PORT,
        log_level="info",
        access_log=True
    )
    
    voice_config = uvicorn.Config(
        voice_app,
        host=API_HOST,
        port=VOICE_PROCESSING_PORT,
        log_level="info",
        access_log=True
    )
    
    # Create servers
    main_server = uvicorn.Server(main_config)
    voice_server = uvicorn.Server(voice_config)
    
    # Run both servers concurrently
    await asyncio.gather(
        main_server.serve(),
        voice_server.serve()
    )

if __name__ == "__main__":
    print("🎙️  VietVoice TTS FastAPI Server")
    print("=" * 50)
    print(f"Main API Server: http://{API_HOST}:{API_PORT}")
    print(f"Voice Processing: http://{API_HOST}:{VOICE_PROCESSING_PORT}")
    print("=" * 50)
    print("Available endpoints:")
    print(f"  - GET  /all_voice")
    print(f"  - GET  /summary_transcript/{{bookId}}/{{voice}}")
    print(f"  - GET  /summary_audio/{{bookId}}/{{voice}}")
    print(f"  - POST /generate_custom_audio")
    print(f"  - GET  /books")
    print(f"  - GET  :{VOICE_PROCESSING_PORT}/processing-all/{{bookId}}")
    print(f"  - POST :{VOICE_PROCESSING_PORT}/start-processing/{{bookId}}")
    print("=" * 50)
    print("📖 API Documentation:")
    print(f"  - Swagger UI: http://{API_HOST}:{API_PORT}/docs")
    print(f"  - ReDoc: http://{API_HOST}:{API_PORT}/redoc")
    print("=" * 50)
    
    try:
        asyncio.run(run_servers())
    except KeyboardInterrupt:
        print("\n⏹️  Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")