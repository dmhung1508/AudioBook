from fastapi import FastAPI, Query, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from uuid import uuid4
from typing import Optional
import vietvoicetts
import os
from pathlib import Path
import sqlite3
import time
import threading
import itertools
from io import BytesIO
from ebooklib import epub, ITEM_DOCUMENT
from bs4 import BeautifulSoup
import tempfile

app = FastAPI()

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

conn = sqlite3.connect("tts.db", check_same_thread=False)
conn.row_factory = sqlite3.Row

def init_db():
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT UNIQUE NOT NULL,
            text TEXT NOT NULL,
            gender TEXT NOT NULL,
            emotion TEXT NOT NULL,
            area TEXT,
            "group" TEXT,
            reference_audio BLOB,
            reference_text TEXT,
            book_id TEXT,
            chapter_id INTEGER,
            title TEXT,
            status TEXT DEFAULT 'pending',
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    try:
        cur.execute("ALTER TABLE tasks ADD COLUMN book_id TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        cur.execute("ALTER TABLE tasks ADD COLUMN chapter_id INTEGER")
    except sqlite3.OperationalError:
        pass
    try:
        cur.execute("ALTER TABLE tasks ADD COLUMN title TEXT")
    except sqlite3.OperationalError:
        pass
    cur.execute("""
        CREATE TABLE IF NOT EXISTS voices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            gender TEXT NOT NULL,
            emotion TEXT NOT NULL,
            area TEXT,
            "group" TEXT
        )
    """)
    conn.commit()

    # Populate voices if empty
    cur.execute("SELECT COUNT(*) FROM voices")
    if cur.fetchone()[0] == 0:
        genders = ["male", "female"]
        emotions = ["neutral", "serious", "monotone", "sad", "surprised", "happy", "angry"]
        areas = ["northern", "southern", "central"]
        groups = ["story", "news", "articles", "audiobook", "review"]
        for g, e, a, gr in itertools.product(genders, emotions, areas, groups):
            name = f"{g}-{e}-{a}-{gr}"
            cur.execute(
                'INSERT INTO voices (name, gender, emotion, area, "group") VALUES (?, ?, ?, ?, ?)',
                (name, g, e, a, gr)
            )
        conn.commit()

init_db()

def worker():
    while True:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tasks WHERE status = 'pending' ORDER BY created_at ASC LIMIT 1")
        row = cur.fetchone()
        if row:
            task_id = row['task_id']
            cur.execute("UPDATE tasks SET status = 'processing' WHERE task_id = ?", (task_id,))
            conn.commit()
            try:
                text = row['text']
                gender = row['gender']
                emotion = row['emotion']
                area = row['area']
                group = row['group']
                reference_audio_bytes = row['reference_audio']
                reference_text = row['reference_text']
                if reference_audio_bytes:
                    audio_bytes, transcript = vietvoicetts.synthesize_to_bytes(
                        text=text,
                        reference_audio=reference_audio_bytes,
                        reference_text=reference_text,
                        gender=gender,
                        emotion=emotion,
                        area=area,
                        group=group
                    )
                else:
                    audio_bytes, transcript = vietvoicetts.synthesize_to_bytes(
                        text=text,
                        gender=gender,
                        emotion=emotion,
                        area=area,
                        group=group
                    )
                output_audio_path = OUTPUT_DIR / f"{task_id}.wav"
                with open(output_audio_path, "wb") as f:
                    f.write(audio_bytes)
                output_transcript_path = OUTPUT_DIR / f"{task_id}.txt"
                with open(output_transcript_path, "w", encoding="utf-8") as f:
                    f.write(transcript)
                cur.execute("UPDATE tasks SET status = 'done' WHERE task_id = ?", (task_id,))
                conn.commit()
            except Exception as e:
                cur.execute("UPDATE tasks SET status = 'error', error_message = ? WHERE task_id = ?", (str(e), task_id))
                conn.commit()
        else:
            time.sleep(1)

thread = threading.Thread(target=worker, daemon=True)
thread.start()

@app.get("/voices")
async def list_voices():
    cur = conn.cursor()
    cur.execute("SELECT * FROM voices")
    voices = [dict(row) for row in cur.fetchall()]
    return voices

@app.post("/synthesize")
async def create_tts_task_without_reference(
    text: str = Query(...),
    voice_name: str = Query("female-neutral-southern-audiobook"),
):
    cur = conn.cursor()
    cur.execute("SELECT * FROM voices WHERE name = ?", (voice_name,))
    voice_row = cur.fetchone()
    if not voice_row:
        raise HTTPException(status_code=404, detail="Voice not found")

    task_id = str(uuid4())
    gender = voice_row['gender']
    emotion = voice_row['emotion']
    area = voice_row['area']
    group = voice_row['group']
    reference_audio_bytes = None
    reference_text = None

    cur.execute("""
        INSERT INTO tasks (task_id, text, gender, emotion, area, "group", reference_audio, reference_text, book_id, chapter_id, title)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (task_id, text, gender, emotion, area, group, reference_audio_bytes, reference_text, None, None, None))
    conn.commit()

    return {"task_id": task_id}

@app.post("/synthesize_with_reference")
async def create_tts_task_with_reference(
    text: str = Query(...),
    voice_name: str = Query("female-neutral-southern-audiobook"),
    reference_audio: UploadFile = File(...),
    reference_text: str = Query(...),
):
    cur = conn.cursor()
    cur.execute("SELECT * FROM voices WHERE name = ?", (voice_name,))
    voice_row = cur.fetchone()
    if not voice_row:
        raise HTTPException(status_code=404, detail="Voice not found")

    task_id = str(uuid4())
    gender = voice_row['gender']
    emotion = voice_row['emotion']
    area = voice_row['area']
    group = voice_row['group']
    reference_audio_bytes = await reference_audio.read()
    reference_text = reference_text

    cur.execute("""
        INSERT INTO tasks (task_id, text, gender, emotion, area, "group", reference_audio, reference_text, book_id, chapter_id, title)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (task_id, text, gender, emotion, area, group, reference_audio_bytes, reference_text, None, None, None))
    conn.commit()

    return {"task_id": task_id}

@app.post("/synthesize_epub")
async def synthesize_epub(
    file: UploadFile = File(...),
    voice_name: str = Query("female-neutral-southern-audiobook"),
):
    content = await file.read()
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as tmp:
            tmp.write(content)
            tmp.flush()
            tmp_path = tmp.name
        book = epub.read_epub(tmp_path)
    finally:
        if tmp_path:
            os.unlink(tmp_path)

    chapters = []
    chapter_index = 1
    first_chapter_skipped = False
    for item in book.get_items():
        if item.get_type() == ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            title = soup.title.string if soup.title else f"Chương {chapter_index}"
            content = soup.get_text(separator='\n', strip=True)
            if len(content.strip()) < 100:
                continue
            if not first_chapter_skipped:
                first_chapter_skipped = True
                continue
            chapters.append({
                "id": chapter_index,
                "title": title,
                "content": content
            })
            chapter_index += 1

    if not chapters:
        raise HTTPException(status_code=400, detail="No chapters found")

    cur = conn.cursor()
    cur.execute("SELECT * FROM voices WHERE name = ?", (voice_name,))
    voice_row = cur.fetchone()
    if not voice_row:
        raise HTTPException(status_code=404, detail="Voice not found")

    gender = voice_row['gender']
    emotion = voice_row['emotion']
    area = voice_row['area']
    group = voice_row['group']

    book_id = str(uuid4())
    for chap in chapters:
        task_id = str(uuid4())
        text = chap['content']
        chapter_id = chap['id']
        chapter_title = chap['title']
        reference_audio_bytes = None
        reference_text = None

        cur.execute("""
            INSERT INTO tasks (task_id, text, gender, emotion, area, "group", reference_audio, reference_text, book_id, chapter_id, title)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (task_id, text, gender, emotion, area, group, reference_audio_bytes, reference_text, book_id, chapter_id, chapter_title))
    conn.commit()

    return {"book_id": book_id}

@app.get("/book_result/{book_id}")
async def get_book_result(book_id: str):
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE book_id = ? ORDER BY chapter_id ASC", (book_id,))
    rows = cur.fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail="Book not found")

    chapters = []
    all_done = True
    has_error = False
    for row in rows:
        status = row['status']
        if status != 'done':
            all_done = False
        if status == 'error':
            has_error = True
        chapters.append({
            "chapter_id": row['chapter_id'],
            "title": row['title'],
            "transcript": row['text'],
            "status": status,
            "audio_url": f"/result/{row['task_id']}" if status == 'done' else None,
            "error_message": row['error_message'] if status == 'error' else None
        })

    if has_error:
        status = "error"
    elif all_done:
        status = "done"
    else:
        status = "processing"

    return {"status": status, "chapters": chapters}

@app.get("/result/{task_id}")
async def get_audio_result(task_id: str):
    cur = conn.cursor()
    cur.execute("SELECT status, error_message FROM tasks WHERE task_id = ?", (task_id,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Task not found")

    status = row['status']
    if status == "done":
        audio_path = OUTPUT_DIR / f"{task_id}.wav"
        if audio_path.exists():
            return FileResponse(audio_path, media_type="audio/wav", filename="output.wav")
        else:
            raise HTTPException(status_code=500, detail="Audio file not found")
    elif status == "error":
        raise HTTPException(status_code=500, detail=f"TTS failed: {row['error_message']}")
    else:
        return {"status": status}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4500)