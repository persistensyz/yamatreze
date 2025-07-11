from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import os
import uuid

app = FastAPI()

# Libera requisições de qualquer lugar (inclusive do GitHub Pages)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ou especifique seu domínio ex: ["https://seudominio.github.io"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.get("/download")
def download_youtube(url: str = Query(...), format: str = Query("mp4")):
    if format not in ["mp3", "mp4"]:
        raise HTTPException(status_code=400, detail="Invalid format")

    file_id = str(uuid.uuid4())
    output_template = f"{DOWNLOAD_FOLDER}/{file_id}.%(ext)s"

    ydl_opts = {
        "outtmpl": output_template,
        "quiet": True,
        "no_warnings": True,
    }

    if format == "mp3":
        ydl_opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
        })
    else:
        ydl_opts["format"] = "bestvideo+bestaudio/best"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            ext = "mp3" if format == "mp3" else info.get("ext", "mp4")
            filename = f"{DOWNLOAD_FOLDER}/{file_id}.{ext}"
            if not os.path.exists(filename):
                raise Exception("File not found after download")
            return FileResponse(filename, media_type="application/octet-stream", filename=f"{info.get('title', 'video')}.{ext}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")
