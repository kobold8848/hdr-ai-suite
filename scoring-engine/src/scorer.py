from fastapi import FastAPI, UploadFile
app = FastAPI()
@app.post("/score")
async def score(file: UploadFile):
    return {"dummy": "ok"}
