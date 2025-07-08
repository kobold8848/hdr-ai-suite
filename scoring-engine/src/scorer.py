import tempfile, pathlib, shutil, subprocess
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import cv2, rawpy, numpy as np

app = FastAPI()

RAW_EXT  = {".cr2", ".cr3", ".nef", ".arw", ".dng", ".raf", ".rw2", ".orf"}
JPEG_EXT = {".jpg", ".jpeg", ".jpe"}

# ---------- 工具函数 ---------- #
def save_temp(upload: UploadFile) -> pathlib.Path:
    suffix = pathlib.Path(upload.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
        shutil.copyfileobj(upload.file, f)
        return pathlib.Path(f.name)

def raw_to_tiff(raw_path: pathlib.Path) -> pathlib.Path:
    with rawpy.imread(str(raw_path)) as raw:
        rgb = raw.postprocess(output_bps=16, gamma=(1,1), no_auto_bright=True)
    tiff_path = raw_path.with_suffix(".tif")
    cv2.imwrite(str(tiff_path), cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
    return tiff_path

def jpeg_to_exr(jpeg_path: pathlib.Path) -> pathlib.Path:
    exr_path = jpeg_path.with_suffix(".exr")
    cmd = [
        "ffmpeg","-y","-loglevel","error","-i",str(jpeg_path),
        "-vf","hdrgainmap,format=gbrpf32le","-frames:v","1", str(exr_path)
    ]
    subprocess.run(cmd, check=True)
    return exr_path
# -------------------------------- #

@app.post("/score")
async def score(file: UploadFile):
    tmp_path = save_temp(file)
    ext = tmp_path.suffix.lower()

    try:
        if ext in RAW_EXT:
            out_path = raw_to_tiff(tmp_path)
            pipeline = "raw->tiff"
        elif ext in JPEG_EXT:
            out_path = jpeg_to_exr(tmp_path)
            pipeline = "hdr-jpeg->exr"
        else:
            out_path = tmp_path
            pipeline = "other"

        img = cv2.imread(str(out_path), cv2.IMREAD_UNCHANGED)
        if img is None:
            raise HTTPException(status_code=400, detail="Unsupported or corrupted image")

        h, w = img.shape[:2]

        # ---------- 占位示例分数 / 建议，可替换为真实模型 ---------- #
        result = {
            "pipeline": pipeline,
            "width": int(w),
            "height": int(h),
            "score":  round((w * h) % 10, 1),          # demo 分数
            "suggest": "曝光 +0.3EV，白平衡 +200 K"       # demo 建议
        }
        # -------------------------------------------------------- #

        return JSONResponse(result)

    finally:
        # 清理上传的临时文件
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        # out_path 如果是 RAW 转出的 tiff/exr，可按需删除
