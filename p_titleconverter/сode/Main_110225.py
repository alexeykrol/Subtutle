from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import subprocess
import sys
from fastapi.responses import FileResponse, StreamingResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # можно указать конкретные адреса
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    print("Получен файл:", file.filename)
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {
        "message": f"Файл загружен: {file.filename}",
        "filename": file.filename
    }

@app.get("/translate_stream/")
async def translate_stream(filename: str):
    input_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(input_path):
        raise HTTPException(status_code=404, detail=f"Файл не найден для перевода: {input_path}")
    
    output_filename = f"translated_{filename}"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    # Добавлен флаг -u для unbuffered вывода
    command = [sys.executable, "-u", "translator.py", input_path, output_path]
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    def event_generator():
        # Читаем построчно вывод переводчика и отправляем через SSE
        for line in process.stdout:
            yield f"data: {line.rstrip()}\n\n"
        process.wait()
        if process.returncode == 0:
            yield f"data: Перевод завершён успешно: {output_filename}\n\n"
            yield f"data: download_url: /download/{output_filename}\n\n"
        else:
            yield f"data: Ошибка при переводе файла.\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден")
    return FileResponse(file_path, media_type='application/octet-stream', filename=filename)
