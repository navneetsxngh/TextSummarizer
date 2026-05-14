from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import asyncio

app = FastAPI(title="AI Text Summarizer")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

_training: dict = {"running": False, "completed": False, "error": None, "logs": []}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/train", response_class=HTMLResponse)
async def train_page(request: Request):
    return templates.TemplateResponse(request, "train.html")


@app.post("/train/start")
async def start_training():
    global _training
    if _training["running"]:
        return JSONResponse({"message": "Training already in progress"}, status_code=409)
    _training = {
        "running": True,
        "completed": False,
        "error": None,
        "logs": ["[INFO] Initializing training pipeline..."],
    }
    asyncio.create_task(_run_training())
    return JSONResponse({"status": "started"})


@app.get("/train/status")
async def train_status():
    return JSONResponse(_training)


@app.post("/train/reset")
async def reset_training():
    global _training
    _training = {"running": False, "completed": False, "error": None, "logs": []}
    return JSONResponse({"status": "reset"})


async def _run_training():
    global _training
    try:
        proc = await asyncio.create_subprocess_shell(
            "python main.py",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        async for line in proc.stdout:
            decoded = line.decode("utf-8", errors="replace").strip()
            if decoded:
                _training["logs"].append(decoded)
        await proc.wait()
        if proc.returncode == 0:
            _training.update(running=False, completed=True)
            _training["logs"].append("[SUCCESS] Training completed successfully!")
        else:
            _training.update(running=False, error="Process exited with non-zero code")
            _training["logs"].append("[ERROR] Training failed — check logs above.")
    except Exception as exc:
        _training.update(running=False, error=str(exc))
        _training["logs"].append(f"[ERROR] {exc}")


@app.get("/predict", response_class=HTMLResponse)
async def predict_page(request: Request):
    return templates.TemplateResponse(request, "predict.html")


@app.post("/predict")
async def predict(request: Request):
    try:
        body = await request.json()
        text = body.get("text", "").strip()
        if not text:
            return JSONResponse({"error": "Text is required"}, status_code=400)
        from src.textsummarizer.pipeline.predictionpipeline import PredictionPipeline
        obj = PredictionPipeline()
        summary = obj.predict(text)
        return JSONResponse({"summary": summary})
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
